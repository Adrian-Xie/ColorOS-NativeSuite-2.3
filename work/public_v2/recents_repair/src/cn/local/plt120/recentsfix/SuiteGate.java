package cn.local.plt120.recentsfix;
import de.robv.android.xposed.XposedHelpers;
final class SuiteGate {
 static boolean active(){try{return "1".equals(XposedHelpers.callStaticMethod(Class.forName("android.os.SystemProperties"),"get","sys.coloros_native_suite","0"));}catch(Throwable e){return false;}}
}
