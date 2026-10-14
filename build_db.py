"""Build db.json: a Downloader/update_all database with the newest core (RBF)
of MiSTer arcade cores that publish their releases in a GitHub repository's
releases/ folder but have no database of their own.

    python build_db.py [db.json]

Only the RBFs: the MRAs that use them are kept elsewhere. Each file's URL is
pinned to the commit it was read at, so its md5 always matches. The
timestamp only changes when a file does.
"""
import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request

DB_ID = 'RealGoemon/mister-extra-cores'
# (repository, branch, folder, RBF name prefix, tag)
SOURCES = [
    ('diegov-au/Syvalion_MiSTer', 'main', 'releases', 'Syvalion_', 'syvalion'),
    ('spacestate1/Arcade-taitoF3_MiSTer', 'master', 'releases', 'Rayforce_', 'taitof3'),
]


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'mister-extra-cores'})
    token = os.environ.get('GITHUB_TOKEN')
    if token and url.startswith('https://api.github.com/'):
        req.add_header('Authorization', 'Bearer ' + token)
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def newest_rbf(repo, branch, folder, prefix):
    """(commit, name) of the newest <prefix>*.rbf: the dated names sort by
    date ("Rayforce_20260908b" after "Rayforce_20260908")."""
    commit = json.loads(get(f'https://api.github.com/repos/{repo}/commits/{branch}'))['sha']
    listing = json.loads(get(f'https://api.github.com/repos/{repo}/contents/{folder}?ref={commit}'))
    names = sorted(f['name'] for f in listing
                   if f['type'] == 'file' and f['name'].startswith(prefix) and f['name'].lower().endswith('.rbf'))
    if not names:
        raise SystemExit(f'{repo}: no {prefix}*.rbf in {folder}/')
    return commit, names[-1]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'db.json'
    old = {}
    try:
        with open(out, encoding='utf-8') as f:
            old = json.load(f)
    except (OSError, ValueError):  # (none yet, or the workflow's empty copy)
        pass
    files = {}
    for repo, branch, folder, prefix, tag in SOURCES:
        commit, name = newest_rbf(repo, branch, folder, prefix)
        path = '_Arcade/cores/' + name
        url = f'https://raw.githubusercontent.com/{repo}/{commit}/{folder}/' + urllib.parse.quote(name)
        prev = old.get('files', {}).get(path)
        if prev:  # (the same name: the same file, unless its size changed)
            data = None
            files[path] = prev
            if prev.get('url') != url:
                data = get(url)
        else:
            data = get(url)
        if data is not None:
            files[path] = {'hash': hashlib.md5(data).hexdigest(), 'size': len(data), 'url': url,
                           'tags': ['arcade', 'cores', tag]}
        print(f'{repo}: {name}')
    db = {
        'db_id': DB_ID,
        'v': 1,
        'timestamp': old.get('timestamp', 0),
        'files': files,
        'folders': {'_Arcade': {'tags': ['arcade']}, '_Arcade/cores': {'tags': ['arcade', 'cores']}},
    }
    if files != old.get('files'):
        db['timestamp'] = int(time.time())
        print('changed')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(db, f, indent=1, sort_keys=True)
        f.write('\n')


if __name__ == '__main__':
    main()
