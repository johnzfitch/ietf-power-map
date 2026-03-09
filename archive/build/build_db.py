#!/usr/bin/env python3
"""
Bulk-fetch IETF Datatracker into SQLite.
Strategy: concurrent paginated fetches, stream directly into DB.
"""
import sqlite3, json, urllib.request, time, sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError

DB = '/home/claude/ietf.db'
BASE = 'https://datatracker.ietf.org'
LIMIT = 1000
WORKERS = 6  # respectful concurrency
RETRY = 3

def fetch_json(url, attempt=0):
    if not url.startswith('http'):
        url = BASE + url
    try:
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except (HTTPError, Exception) as e:
        if attempt < RETRY:
            time.sleep(1 * (attempt + 1))
            return fetch_json(url, attempt + 1)
        print(f"  FAIL {url}: {e}", file=sys.stderr)
        return None

def get_total(endpoint):
    data = fetch_json(f'{BASE}{endpoint}?format=json&limit=0')
    return data['meta']['total_count'] if data else 0

def fetch_page(endpoint, offset, limit=LIMIT):
    """Fetch one page, return list of objects."""
    data = fetch_json(f'{BASE}{endpoint}?format=json&limit={limit}&offset={offset}')
    return data['objects'] if data else []

def bulk_fetch(endpoint, total, label):
    """Parallel paginated fetch of entire endpoint."""
    pages = list(range(0, total, LIMIT))
    all_objects = []
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(fetch_page, endpoint, off): off for off in pages}
        for f in as_completed(futures):
            objs = f.result()
            if objs:
                all_objects.extend(objs)
            done += 1
            if done % 10 == 0 or done == len(pages):
                print(f"  {label}: {done}/{len(pages)} pages ({len(all_objects)} rows)", file=sys.stderr)
    return all_objects

# ═══════════════════════════════════════════
# SCHEMA
# ═══════════════════════════════════════════
if os.path.exists(DB):
    os.remove(DB)

conn = sqlite3.connect(DB)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
conn.execute("PRAGMA cache_size=-64000")  # 64MB cache

conn.executescript("""
CREATE TABLE documents (
    name TEXT PRIMARY KEY,
    title TEXT,
    rfc_number INTEGER,
    time TEXT,
    pages INTEGER,
    words INTEGER,
    stream TEXT,
    std_level TEXT,
    abstract TEXT,
    group_uri TEXT
);

CREATE TABLE persons (
    id INTEGER PRIMARY KEY,
    name TEXT,
    ascii TEXT,
    bio TEXT,
    photo TEXT
);

CREATE TABLE document_authors (
    id INTEGER PRIMARY KEY,
    document TEXT,
    person_id INTEGER,
    affiliation TEXT,
    author_order INTEGER,
    FOREIGN KEY (document) REFERENCES documents(name),
    FOREIGN KEY (person_id) REFERENCES persons(id)
);

CREATE TABLE groups (
    id INTEGER PRIMARY KEY,
    acronym TEXT,
    name TEXT,
    type TEXT,
    state TEXT,
    parent_id INTEGER
);

CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    person_id INTEGER,
    group_id INTEGER,
    role_name TEXT,
    email TEXT,
    FOREIGN KEY (person_id) REFERENCES persons(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);
""")

# ═══════════════════════════════════════════
# 1. RFC DOCUMENTS (9.7K)
# ═══════════════════════════════════════════
print("=== Phase 1: RFC Documents ===", file=sys.stderr)
total_rfcs = get_total('/api/v1/doc/document/?type=rfc')
print(f"  Total RFCs: {total_rfcs}", file=sys.stderr)

rfcs = bulk_fetch('/api/v1/doc/document/?type=rfc', total_rfcs, 'RFCs')
rows = []
for d in rfcs:
    rows.append((
        d['name'],
        d.get('title', ''),
        d.get('rfc_number'),
        d.get('time', ''),
        d.get('pages'),
        d.get('words'),
        (d.get('stream') or '').split('/')[-2] if d.get('stream') else None,
        (d.get('std_level') or '').split('/')[-2] if d.get('std_level') else None,
        d.get('abstract', ''),
        d.get('group', '')
    ))
conn.executemany("INSERT OR IGNORE INTO documents VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
conn.commit()
print(f"  Inserted {len(rows)} RFC documents", file=sys.stderr)

# ═══════════════════════════════════════════
# 2. DOCUMENT AUTHORS (136K) - ALL, not just RFCs
# ═══════════════════════════════════════════
print("=== Phase 2: Document Authors ===", file=sys.stderr)
total_authors = get_total('/api/v1/doc/documentauthor/')
print(f"  Total author records: {total_authors}", file=sys.stderr)

authors = bulk_fetch('/api/v1/doc/documentauthor/', total_authors, 'Authors')
rows = []
person_ids = set()
for a in authors:
    pid_str = (a.get('person') or '').split('/')[-2]
    pid = int(pid_str) if pid_str.isdigit() else None
    doc_name = (a.get('document') or '').split('/')[-2]
    if pid and doc_name:
        person_ids.add(pid)
        rows.append((
            a['id'],
            doc_name,
            pid,
            a.get('affiliation', ''),
            a.get('order', 0)
        ))
conn.executemany("INSERT OR IGNORE INTO document_authors VALUES (?,?,?,?,?)", rows)
conn.commit()
print(f"  Inserted {len(rows)} author records, {len(person_ids)} unique persons", file=sys.stderr)

# ═══════════════════════════════════════════
# 3. PERSONS (bulk resolve all unique authors)
# ═══════════════════════════════════════════
print("=== Phase 3: Persons ===", file=sys.stderr)
print(f"  Resolving {len(person_ids)} unique persons...", file=sys.stderr)

pid_list = sorted(person_ids)
done = 0

def fetch_person(pid):
    data = fetch_json(f'/api/v1/person/person/{pid}/?format=json')
    if data:
        return (
            data['id'],
            data.get('name', ''),
            data.get('ascii', ''),
            (data.get('biography') or '')[:500],
            data.get('photo_thumb', '')
        )
    return (pid, f'Person #{pid}', '', '', '')

# Batch with thread pool
person_rows = []
with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = {pool.submit(fetch_person, pid): pid for pid in pid_list}
    for f in as_completed(futures):
        person_rows.append(f.result())
        done += 1
        if done % 500 == 0:
            print(f"  Persons: {done}/{len(pid_list)}", file=sys.stderr)

conn.executemany("INSERT OR IGNORE INTO persons VALUES (?,?,?,?,?)", person_rows)
conn.commit()
print(f"  Inserted {len(person_rows)} persons", file=sys.stderr)

# ═══════════════════════════════════════════
# 4. GROUPS + ROLES (for governance overlay)
# ═══════════════════════════════════════════
print("=== Phase 4: Active Groups ===", file=sys.stderr)

# WGs, RGs, areas, governance bodies
for gtype in ['wg', 'rg', 'area', 'ietf', 'iab', 'irtf']:
    groups = bulk_fetch(f'/api/v1/group/group/?type={gtype}&state=active', 
                        get_total(f'/api/v1/group/group/?type={gtype}&state=active'), 
                        f'Groups({gtype})')
    rows = []
    for g in groups:
        parent_str = (g.get('parent') or '').split('/')[-2]
        rows.append((
            g['id'],
            g['acronym'],
            g['name'],
            (g.get('type') or '').split('/')[-2],
            (g.get('state') or '').split('/')[-2],
            int(parent_str) if parent_str.isdigit() else None
        ))
    conn.executemany("INSERT OR IGNORE INTO groups VALUES (?,?,?,?,?,?)", rows)

# IAB, IESG, IRTF explicit
for grp in ['iab', 'iesg']:
    data = fetch_json(f'/api/v1/group/group/?format=json&acronym={grp}&limit=5')
    for g in (data or {}).get('objects', []):
        parent_str = (g.get('parent') or '').split('/')[-2]
        conn.execute("INSERT OR IGNORE INTO groups VALUES (?,?,?,?,?,?)", (
            g['id'], g['acronym'], g['name'],
            (g.get('type') or '').split('/')[-2],
            (g.get('state') or '').split('/')[-2],
            int(parent_str) if parent_str.isdigit() else None
        ))

conn.commit()

# Roles for all active groups
print("=== Phase 5: Roles ===", file=sys.stderr)
total_roles = get_total('/api/v1/group/role/')
print(f"  Total role records: {total_roles}", file=sys.stderr)
all_roles = bulk_fetch('/api/v1/group/role/', total_roles, 'Roles')
rows = []
for r in all_roles:
    pid_str = (r.get('person') or '').split('/')[-2]
    gid_str = (r.get('group') or '').split('/')[-2]
    rows.append((
        r['id'],
        int(pid_str) if pid_str.isdigit() else None,
        int(gid_str) if gid_str.isdigit() else None,
        (r.get('name') or '').split('/')[-2],
        (r.get('email') or '').split('/')[-2]
    ))
conn.executemany("INSERT OR IGNORE INTO roles VALUES (?,?,?,?,?)", rows)
conn.commit()
print(f"  Inserted {len(rows)} roles", file=sys.stderr)

# ═══════════════════════════════════════════
# 6. INDEXES
# ═══════════════════════════════════════════
print("=== Phase 6: Indexes ===", file=sys.stderr)
conn.executescript("""
CREATE INDEX idx_da_person ON document_authors(person_id);
CREATE INDEX idx_da_document ON document_authors(document);
CREATE INDEX idx_doc_rfc ON documents(rfc_number);
CREATE INDEX idx_doc_time ON documents(time);
CREATE INDEX idx_roles_person ON roles(person_id);
CREATE INDEX idx_roles_group ON roles(group_id);
CREATE INDEX idx_groups_type ON groups(type);
CREATE INDEX idx_groups_acronym ON groups(acronym);
CREATE INDEX idx_persons_name ON persons(name);
""")
conn.commit()

# ═══════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════
print("\n=== SUMMARY ===", file=sys.stderr)
for table in ['documents', 'persons', 'document_authors', 'groups', 'roles']:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:20s} {count:>8,} rows", file=sys.stderr)

size = os.path.getsize(DB)
print(f"\n  Database size: {size/1024/1024:.1f} MB", file=sys.stderr)
conn.close()
print("DONE", file=sys.stderr)
