"""Build public-test APKs with native-interface checks rather than model/version locks."""
from pathlib import Path
import hashlib,json,os,subprocess,zipfile,sys

ROOT=Path(__file__).resolve().parent.parent
TOOLS=ROOT/'work/v2_research/toolchain'
OUT=ROOT/'outputs/public-test'
java=next((TOOLS/'jdk').rglob('bin/java.exe'));javac=java.with_name('javac.exe')
bt=next((TOOLS/'build-tools-35.0.0').rglob('aapt2.exe')).parent
android=next((TOOLS/'platforms-android-35').rglob('android.jar'))
api=TOOLS/'xposed-api82.jar'
# Public version: use your own signing keystore. The original local
# development keystore path and credentials were removed before publishing.
key=Path(os.environ.get('SIGN_KEYSTORE', 'path/to/your-keystore.p12'))

def build(name,filename):
    src=ROOT/'work/public_v2'/name;folder=ROOT/'work/public_v2'/('build-'+name)
    # Compile into empty task-owned staging directories; removed source classes
    # must never linger in a rebuilt APK.
    import shutil
    for f in ['classes','dex']:
        stage=(folder/f).resolve()
        assert stage.is_relative_to((ROOT/'work/public_v2').resolve())
        if stage.exists():shutil.rmtree(stage)
        stage.mkdir(parents=True,exist_ok=True)
    logs=[]
    def run(*args):
        r=subprocess.run([str(x) for x in args],capture_output=True,timeout=90)
        logs.append({'tool':Path(args[0]).name,'returncode':r.returncode,'output':(r.stdout+r.stderr).decode('utf-8',errors='replace')})
        if r.returncode:raise RuntimeError(logs[-1])
    run(bt/'aapt2.exe','compile','--dir',src/'res','-o',folder/'resources.zip')
    run(bt/'aapt2.exe','link','-o',folder/'resources.apk','-I',android,'--manifest',src/'AndroidManifest.xml','-A',src/'assets',folder/'resources.zip')
    run(javac,'-encoding','UTF-8','-source','8','-target','8','-classpath',str(android)+';'+str(api),'-d',folder/'classes',*sorted((src/'src').rglob('*.java')))
    with zipfile.ZipFile(folder/'classes.jar','w',zipfile.ZIP_DEFLATED) as z:
        for f in (folder/'classes').rglob('*.class'):z.write(f,f.relative_to(folder/'classes').as_posix())
    run(java,'-cp',bt/'lib/d8.jar','com.android.tools.r8.D8','--lib',android,'--min-api','35','--output',folder/'dex',folder/'classes.jar')
    (folder/'unsigned.apk').write_bytes((folder/'resources.apk').read_bytes())
    with zipfile.ZipFile(folder/'unsigned.apk','a',zipfile.ZIP_DEFLATED) as z:z.write(folder/'dex/classes.dex','classes.dex')
    run(bt/'zipalign.exe','-f','4',folder/'unsigned.apk',folder/'aligned.apk')
    apk=OUT/filename
    run(java,'-jar',bt/'lib/apksigner.jar','sign','--ks',key,'--ks-pass',os.environ.get('SIGN_KEYSTORE_PASS', 'change-me'),'--ks-key-alias',os.environ.get('SIGN_KEY_ALIAS', 'your-alias'),'--v4-signing-enabled','false','--out',apk,folder/'aligned.apk')
    run(java,'-jar',bt/'lib/apksigner.jar','verify','--verbose','--print-certs',apk)
    run(bt/'zipalign.exe','-c','4',apk)
    digest=hashlib.sha256(apk.read_bytes()).hexdigest()
    apk.with_name(apk.name+'.sha256').write_text(digest+'  '+apk.name+'\n',encoding='utf-8')
    with zipfile.ZipFile(OUT/(apk.stem+'-source.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src.rglob('*')):
            if f.is_file():z.write(f,f.relative_to(src).as_posix())
    report={'artifact':filename,'bytes':apk.stat().st_size,'sha256':digest,'build_checks':logs}
    (folder/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='build_checks'},ensure_ascii=False),flush=True)

targets={'recents_repair':'ColorOS_RecentsRepair_0.4.apk'}
for name in (sys.argv[1:] or targets):build(name,targets[name])
