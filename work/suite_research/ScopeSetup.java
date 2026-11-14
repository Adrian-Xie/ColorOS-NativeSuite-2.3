import android.content.ContentValues;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import java.util.HashSet;
import java.util.Set;

/** Only this suite's module and owner-user scopes. Unknown schemas are never edited. */
public final class ScopeSetup {
 private static final String PKG="cn.local.plt120.recentsfix";
 private static Set<String> columns(SQLiteDatabase db,String table){
  Set<String> result=new HashSet<>();try(Cursor c=db.rawQuery("PRAGMA table_info("+table+")",null)){while(c.moveToNext())result.add(c.getString(c.getColumnIndexOrThrow("name")));}return result;
 }
 private static void require(boolean value,String message){if(!value)throw new IllegalStateException(message);}
 public static void main(String[] args){
  try{
   require(args.length>=2,"Usage: inspect|enable|disable database [apkPath]");
   String mode=args[0];
   require(mode.equals("inspect")||mode.equals("enable")||mode.equals("disable"),"Unknown operation");
   SQLiteDatabase.OpenParams.Builder options=new SQLiteDatabase.OpenParams.Builder().setOpenFlags(mode.equals("inspect")?SQLiteDatabase.OPEN_READONLY:SQLiteDatabase.OPEN_READWRITE);
   // Some OEM SQLiteGlobal defaults assume an application context in app_process.
   if(!mode.equals("inspect"))options.getClass().getMethod("setSynchronousMode",String.class).invoke(options,"NORMAL");
   SQLiteDatabase db=SQLiteDatabase.openDatabase(new java.io.File(args[1]),options.build());
   Set<String> modules=columns(db,"modules"),scope=columns(db,"scope"),state=columns(db,"modules_state");
   System.out.println("modules="+modules+" scope="+scope+" state="+state);
   boolean old=modules.contains("mid")&&modules.contains("enabled")&&scope.contains("mid");
   boolean modern=state.contains("enabled")&&state.contains("user_id")&&scope.contains("module_pkg_name");
   require(modules.contains("module_pkg_name")&&modules.contains("apk_path")&&scope.contains("app_pkg_name")&&scope.contains("user_id")&&(old||modern),"Unsupported LSPosed schema; use manager to enable this module manually");
   if(mode.equals("inspect")){db.close();return;}
   if(mode.equals("enable"))require(args.length==3&&args[2].startsWith("/data/app/")&&args[2].endsWith(".apk"),"Unexpected package path");
   db.beginTransaction();
   try{
    ContentValues v=new ContentValues();
    if(mode.equals("enable")){
     v.put("module_pkg_name",PKG);v.put("apk_path",args[2]);
     db.insertWithOnConflict("modules",null,v,SQLiteDatabase.CONFLICT_IGNORE);
     v.clear();v.put("apk_path",args[2]);db.update("modules",v,"module_pkg_name=?",new String[]{PKG});
    }
    String key;String id;
    if(old){
     try(Cursor c=db.rawQuery("SELECT mid FROM modules WHERE module_pkg_name=?",new String[]{PKG})){require(c.moveToFirst(),"Suite module is not registered");id=c.getString(0);}
     key="mid";v.clear();v.put("enabled",mode.equals("enable")?1:0);db.update("modules",v,"mid=?",new String[]{id});
    }else{
     key="module_pkg_name";id=PKG;v.clear();v.put("module_pkg_name",PKG);v.put("user_id",0);v.put("enabled",mode.equals("enable")?1:0);
     db.insertWithOnConflict("modules_state",null,v,SQLiteDatabase.CONFLICT_REPLACE);
    }
    if(mode.equals("enable")){
     db.delete("scope",key+"=? AND user_id=0",new String[]{id});
     for(String target:new String[]{"com.android.launcher"}){
      v.clear();v.put(key,id);v.put("app_pkg_name",target);v.put("user_id",0);db.insertOrThrow("scope",null,v);
     }
    }
    db.setTransactionSuccessful();
   }finally{db.endTransaction();db.close();}
   System.out.println(mode.toUpperCase()+" committed for "+PKG+" owner-user only; effective after reboot");
  }catch(Throwable e){System.err.println("SCOPE_SETUP_FAILED: "+e);e.printStackTrace();System.exit(2);}
 }
}
