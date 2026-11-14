"""Fetch unmodified OEM template assets, pinned to a public firmware tree."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, urllib.parse, urllib.request, urllib.error, time, tarfile, io, subprocess

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'oem_theme_payload'
OUT.mkdir(exist_ok=True)
PROJECT = 77173148
BASE = f'https://gitlab.com/api/v4/projects/{PROJECT}/repository/'
REF = 'sys_mssi_64_64only_cn_armv82-user-16-BP2A.250605.015-1763482170296-release-keys'
REMOTE = 'my_product/decouping_wallpaper/inspiration_theme_resource/inspiration_theme_templates'
GROUPS = ['sleek', 'light_and_shadow', 'composition', 'rhythm', 'healing', 'aerial_view']

def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code==429:
                raise RuntimeError('GitLab rate limit; wait '+str(e.headers.get('Retry-After'))+' seconds before retrying') from e
            if attempt==2: raise
            time.sleep(attempt+1)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)

def tree(group):
    args = urllib.parse.urlencode({'ref': REF, 'per_page': 100, 'path': REMOTE + '/' + group})
    return json.loads(get(BASE + 'tree?' + args))

def fetch(item):
    assert item['type'] == 'blob'
    remote = item['path']
    rel = remote.removeprefix(REMOTE + '/')
    assert '..' not in Path(rel).parts and rel.split('/')[0] in GROUPS
    dest = OUT / 'assets' / rel
    url = BASE + 'files/' + urllib.parse.quote(remote, safe='') + '/raw?' + urllib.parse.urlencode({'ref': REF})
    if dest.exists():
        data = dest.read_bytes()
    else:
        data = get(url)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    git_sha = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert git_sha == item['id'], (rel, git_sha, item['id'])
    return {'path': rel, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'git_blob': git_sha, 'url': url}

if __name__ == '__main__':
    source = ROOT / 'suite_research/donor-inspiration_theme_templates.json'
    catalog = json.loads(source.read_text('utf8'))
    selected = [g for g in catalog if g['inspirationTypeName'] in GROUPS]
    assert len(selected) == len(GROUPS)
    (OUT / 'groups.json').write_text(json.dumps(selected, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    # Fetch with Git's supported sparse/partial-clone protocol, then verify every blob.
    repo=ROOT/'suite_research/donor-sparse'
    commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    assert commit=='38076cbb63f3b0234e27114bf8352d16801612e6'
    listing=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','HEAD','--',REMOTE],text=True)
    hashes={line.split('\t',1)[1].removeprefix(REMOTE+'/'):line.split()[2] for line in listing.splitlines()}
    assert json.loads((repo/REMOTE/'inspiration_theme_templates.json').read_bytes())==json.loads(source.read_bytes())
    wanted={rel:sha for rel,sha in hashes.items() if rel.split('/')[0] in GROUPS}
    batch=subprocess.run(['git','-C',str(repo),'cat-file','--batch'],input=''.join(sha+'\n' for sha in wanted.values()).encode(),capture_output=True,check=True).stdout
    stream=io.BytesIO(batch)
    manifest=[]
    for rel,expected in wanted.items():
        assert '..' not in Path(rel).parts and not Path(rel).is_absolute()
        header=stream.readline().decode().split();assert header[0]==expected and header[1]=='blob'
        data=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        if rel.endswith('.webp'):assert data[:4]==b'RIFF' and data[8:12]==b'WEBP',rel
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert actual==expected,rel
        dest=OUT/'assets'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        manifest.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob':actual})
    report = {'project': PROJECT, 'ref': REF, 'commit':commit, 'repository':'https://gitlab.com/rama-firmware-dumps/oneplus/CPH2719', 'remote_root': REMOTE, 'groups': GROUPS, 'files': sorted(manifest, key=lambda x:x['path'])}
    (OUT / 'source-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'groups': [(g['inspirationTypeName'],len(g['templates'])) for g in selected], 'files':len(manifest),'bytes':sum(f['bytes'] for f in manifest)}, ensure_ascii=False))
