from pathlib import Path
import subprocess,zipfile
root=Path(__file__).resolve().parent.parent
t=root/'work/v2_research/toolchain';java=next((t/'jdk').rglob('bin/java.exe'));bt=next((t/'build-tools-35.0.0').rglob('aapt2.exe')).parent
android=next((t/'platforms-android-35').rglob('android.jar'));out=root/'work/suite_research/scope-helper';out.mkdir(exist_ok=True)
def run(*cmd):
 r=subprocess.run([str(x) for x in cmd],capture_output=True,timeout=80)
 if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace'))
run(java.with_name('javac.exe'),'-encoding','UTF-8','-source','8','-target','8','-classpath',android,'-d',out,root/'work/suite_research/ScopeSetup.java')
with zipfile.ZipFile(out/'helper.jar','w') as z:
 for f in out.glob('*.class'):z.write(f,f.name)
run(java,'-cp',bt/'lib/d8.jar','com.android.tools.r8.D8','--lib',android,'--min-api','35','--output',out,out/'helper.jar')
print(out/'classes.dex')
