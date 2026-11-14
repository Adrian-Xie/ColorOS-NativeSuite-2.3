package cn.local.plt120.recentsfix;
import android.animation.Animator;
import android.app.Application;
import android.content.Context;
import android.content.pm.PackageInfo;
import android.os.Build;
import android.util.Log;
import de.robv.android.xposed.*;
import de.robv.android.xposed.callbacks.XC_LoadPackage;
/** Exact-device candidate based on recorded false conversion flag in stable Overview. */
public final class RecentsRepairHook implements IXposedHookLoadPackage {
 private static boolean attempted;
 private static int logs;
 private static void log(String s){if(logs++<40){Log.i("PLT120RecentsRepair",s);XposedBridge.log("PLT120RecentsRepair "+s);}}
 @Override public void handleLoadPackage(final XC_LoadPackage.LoadPackageParam lp){
  if(!"com.android.launcher".equals(lp.packageName)||!lp.packageName.equals(lp.processName))return;
  if(!SuiteGate.active())return;
  XposedHelpers.findAndHookMethod(Application.class,"attach",Context.class,new XC_MethodHook(){
   @Override protected void afterHookedMethod(MethodHookParam p){if(attempted)return;attempted=true;try{
    PackageInfo info=((Context)p.args[0]).getPackageManager().getPackageInfo(lp.packageName,0);
    install(lp.classLoader);
   }catch(Throwable e){log("DISABLED "+e.getClass().getSimpleName());}}
  });
 }
 private static void install(ClassLoader cl)throws Throwable{
  final Class<?> flags=XposedHelpers.findClass("com.oplus.quickstep.utils.TaskStackLayoutAlgorithm",cl);
  final Class<?> config=XposedHelpers.findClass("com.oplus.quickstep.common.settingsvalue.CommonSettingsValueProxy",cl);
  final Class<?> state=XposedHelpers.findClass("com.android.launcher3.LauncherState",cl);
  final Object overview=XposedHelpers.getStaticObjectField(state,"OVERVIEW");
  final Class<?> callback=XposedHelpers.findClass("com.android.quickstep.uioverrides.OplusRecentsViewStateControllerImpl$setStateWithAnimationInternal$2$5",cl);
  XposedHelpers.findField(callback,"$toState");
  XposedHelpers.findField(callback,"$this_apply");
  XposedHelpers.findMethodExact(flags,"setIsTransToStackLayout",boolean.class);
  XposedHelpers.findAndHookMethod(callback,"onAnimationStart",Animator.class,new XC_MethodHook(){
   @Override protected void beforeHookedMethod(MethodHookParam p){try{
    if(XposedHelpers.getObjectField(p.thisObject,"$toState")!=overview)return;
    if(!(Boolean)XposedHelpers.callStaticMethod(config,"isStackLayout"))return;
    Object panel=XposedHelpers.getObjectField(p.thisObject,"$this_apply");
    if(!(Boolean)XposedHelpers.callMethod(panel,"getMIsStack"))return;
    if(XposedHelpers.getStaticBooleanField(flags,"mIsTransToStackLayout"))return;
    if((Boolean)XposedHelpers.callMethod(panel,"isGustureActive")){log("SKIP active gesture");return;}
    XposedHelpers.callStaticMethod(flags,"setIsTransToStackLayout",true);
    log("CORRECTED conversion=false at Overview animation start; native animation continues");
   }catch(Throwable e){log("SKIP "+e.getClass().getSimpleName());}}
  });
  log("ACTIVE Overview-entry candidate; no settings, blur, menu or system-file changes");
 }
}
