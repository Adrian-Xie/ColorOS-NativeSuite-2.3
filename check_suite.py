from pathlib import Path
import hashlib,json,shlex,xml.etree.ElementTree as ET
from adb_readonly import adb,shell,ROOT

BASE=Path(__file__).resolve().parent
SUITE=BASE/'coloros_native_suite'
OUT=BASE/'suite_research/validation';OUT.mkdir(exist_ok=True)
REMOTE='/data/local/tmp/coloros-suite-check'
shell('mkdir -p '+REMOTE)
def push(p,d):
 r=adb('push',str(p),d,timeout=180)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace'))
def root(c):return shell('su -c '+shlex.quote(c),timeout=120)
checks=[]
for i,p in enumerate(SUITE.rglob('*.sh')):
 dest=f'{REMOTE}/script-{i}.sh';push(p,dest)
 root('/data/adb/ksu/bin/busybox sh -n '+dest)
 checks.append(str(p.relative_to(SUITE)))
push(SUITE/'parts/features/patch_features.awk',REMOTE+'/patch.awk')
added_app={'com.android.launcher.support_stack_recents','com.android.launcher_card_force_enable','com.android.launcher_group_card_force_enable'}
removed_app={'com.oplus.wallpapers.LIGHT_WEIGHT_OS_FUNC','speechassist.cui.device.light.low','speechassist.cui.device.light'}
added_oplus={'oplus.software.support_fluid_entry','oplus.software.fluid_replace_ntf'}
allowed=added_app|removed_app|added_oplus
results=[]
def entries(tree):
 return {e.attrib.get('name'):ET.tostring(e,encoding='unicode').strip() for e in tree.getroot() if e.attrib.get('name') not in allowed}
for i,p in enumerate(sorted((ROOT/'configs').rglob('*.xml'))):
 if p.name not in ('com.oplus.app-features.xml','com.oplus.oplus-feature.xml'):continue
 kind='app' if p.name=='com.oplus.app-features.xml' else 'oplus'
 inp=f'{REMOTE}/input.xml';push(p,inp)
 for primary in (0,1):
  cmd=f'/data/adb/ksu/bin/busybox awk -v kind={kind} -v primary={primary} -f {REMOTE}/patch.awk'
  root(f'{cmd} {inp} > {REMOTE}/output.xml')
  patched=shell('cat '+REMOTE+'/output.xml')
  out=OUT/f'{i}-{primary}.xml';out.write_text(patched,encoding='utf8')
  orig=ET.parse(p);new=ET.ElementTree(ET.fromstring(patched))
  assert entries(orig)==entries(new),(p,'unrelated feature changed')
  root(f'{cmd} {REMOTE}/output.xml > {REMOTE}/second.xml')
  assert shell('cat '+REMOTE+'/second.xml')==patched,(p,'non-idempotent')
  names={e.attrib.get('name'):e.attrib for e in new.getroot()}
  if kind=='app':
   for name in removed_app:assert name not in names
   if primary:
    assert added_app<=names.keys()
    assert names['com.android.launcher_group_card_force_enable']['args']=='boolean:true'
  elif primary:assert added_oplus<=names.keys()
  results.append({'source':str(p.relative_to(ROOT/'configs')),'primary':primary,'sha256':hashlib.sha256(patched.encode()).hexdigest(),'unrelated_features_unchanged':True,'idempotent':True})
report={'shell_syntax':checks,'xml_cases':results}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'scripts':len(checks),'xml_cases':len(results),'passed':True}))
