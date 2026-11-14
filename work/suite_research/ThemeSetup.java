import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;

/** Append missing OEM template groups; keep existing groups and original APKs. */
public final class ThemeSetup {
 private static final String CATALOG="inspiration_theme_templates.json";
 private static final Set<String> ALLOWED=new HashSet<>(Arrays.asList("sleek","light_and_shadow","composition","rhythm","healing","aerial_view"));
 private static void require(boolean b,String m){if(!b)throw new IllegalStateException(m);}
 private static String read(Path p)throws IOException{return new String(Files.readAllBytes(p),StandardCharsets.UTF_8);}
 private static Path child(Path root,String rel)throws IOException{
  require(rel.matches("[A-Za-z0-9_./-]+")&&!rel.startsWith("/")&&!Arrays.asList(rel.split("/")).contains(".."),"Unsafe OEM resource path");
  Path p=root.resolve(rel).normalize();require(p.startsWith(root),"Resource outside root");return p;
 }
 private static void clean(Path p)throws IOException{
  if(!Files.exists(p,LinkOption.NOFOLLOW_LINKS))return;
  require(!Files.isSymbolicLink(p),"Unexpected directory symlink");
  try(java.util.stream.Stream<Path> paths=Files.walk(p)){for(Path f:(Iterable<Path>)paths.sorted(Comparator.reverseOrder())::iterator)Files.delete(f);}
 }
 private static void copyTree(Path from,Path to)throws IOException{
  try(java.util.stream.Stream<Path> paths=Files.walk(from)){
   for(Path f:(Iterable<Path>)paths::iterator){
    require(!Files.isSymbolicLink(f),"Unexpected OEM resource symlink");
    Path dest=to.resolve(from.relativize(f));
    if(Files.isDirectory(f))Files.createDirectories(dest);else Files.copy(f,dest,StandardCopyOption.REPLACE_EXISTING);
   }
  }
 }
 public static void main(String[] args){
  try{
   require(args.length==4,"Usage: source-directory payload-directory output-directory wallpapers-apk");
   Path src=Paths.get(args[0]).toRealPath(),payload=Paths.get(args[1]).toRealPath();
   Path out=Paths.get(args[2]).toAbsolutePath().normalize();
   require(out.startsWith(payload.getParent())&&!out.equals(payload)&&out.getFileName().toString().equals("generated"),"Unexpected output directory");
   require(Files.isRegularFile(src.resolve(CATALOG)),"Original template catalogue missing");
   JSONArray original=new JSONArray(read(src.resolve(CATALOG))),add=new JSONArray(read(payload.resolve("groups.json")));
   require(original.length()>0&&original.length()<100,"Unexpected original catalogue size");
   Set<String> seen=new HashSet<>(),appended=new HashSet<>();
   for(int i=0;i<original.length();i++){
    JSONObject g=original.getJSONObject(i);String name=g.getString("inspirationTypeName");
    require(seen.add(name),"Duplicate original template group");g.getJSONArray("templates");
   }
   try(ZipFile apk=new ZipFile(args[3])){
    boolean compatible=false;
    Enumeration<? extends ZipEntry> entries=apk.entries();
    while(entries.hasMoreElements()){
     ZipEntry e=entries.nextElement();if(!e.getName().matches("classes[0-9]*\\.dex"))continue;
     String s;try(InputStream in=apk.getInputStream(e)){ByteArrayOutputStream b=new ByteArrayOutputStream();byte[] buf=new byte[65536];int n;while((n=in.read(buf))!=-1)b.write(buf,0,n);s=new String(b.toByteArray(),StandardCharsets.ISO_8859_1);}
     if(s.contains("inspirationTypeName")&&s.contains("healing")&&s.contains("rhythm")&&s.contains("light_and_shadow"))compatible=true;
    }
    require(compatible,"OEM catalogue engine does not expose the required template schema");
    for(int i=0;i<add.length();i++){
     JSONObject g=add.getJSONObject(i);String name=g.getString("inspirationTypeName");require(ALLOWED.contains(name),"Unreviewed template group");
     if(seen.contains(name))continue;
     JSONArray templates=g.getJSONArray("templates");require(templates.length()>0,"Empty OEM template group");
     for(int j=0;j<templates.length();j++){
      JSONObject t=templates.getJSONObject(j),clock=new JSONObject(t.getString("clockInfo"));
      require(Arrays.asList("com.oplus.keyguard.clock.base","com.oplus.keyguard.clock.magazine","com.oplus.keyguard.clock.gallery","com.oplus.keyguard.clock.graffiti").contains(clock.getString("pkg")),"Unsupported native clock package");
      new JSONObject(clock.getString("clockStyleConfig"));
      for(String key:Arrays.asList("wallpaper","aiImage","previewSimplified","previewTraditional","previewEng")){
       String rel=t.optString(key,"");if(!rel.isEmpty())require(Files.isRegularFile(child(payload.resolve("assets"),rel)),"Missing template asset: "+rel);
      }
      JSONObject diff=new JSONObject(t.optString("difference","{}"));
      Iterator<String> keys=diff.keys();while(keys.hasNext()){
       Object value=diff.get(keys.next());if(!(value instanceof String))continue;String rel=(String)value;
       if(rel.matches(".*\\.(svg|webp|mp4)$")){child(payload,rel);require(apk.getEntry("assets/inspiration_theme_styles/"+rel)!=null,"Native style dependency missing: "+rel);}
      }
     }
     original.put(g);seen.add(name);appended.add(name);System.out.println("APPEND "+name+": "+templates.length()+" OEM templates");
    }
   }
   Path next=out.resolveSibling("generated.next");require(!next.equals(src),"Source aliases output");clean(next);
   copyTree(src,next);for(String group:appended)copyTree(payload.resolve("assets").resolve(group),next.resolve(group));
   Files.write(next.resolve(CATALOG),(original.toString(2)+"\n").getBytes(StandardCharsets.UTF_8));
   clean(out);Files.move(next,out);
   System.out.println("PREPARED "+original.length()+" groups; native editor and lockscreen availability depends on device support");
  }catch(Throwable e){System.err.println("OEM_THEME_SETUP_FAILED: "+e);System.exit(2);}
 }
}
