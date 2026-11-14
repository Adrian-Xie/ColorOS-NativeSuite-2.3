# Edit only named feature elements. Preserve all other XML, including comments.
function fail(s) { print s > "/dev/stderr"; failed=1; exit 2 }
function feature_name(t,    x,q,e) {
  if (!match(t, /[[:space:]]name[[:space:]]*=[[:space:]]*/)) return ""
  x=substr(t,RSTART+RLENGTH); q=substr(x,1,1)
  if(q!="\"" && q!=sprintf("%c",39)) return ""
  x=substr(x,2); e=index(x,q); if(!e)return ""
  return substr(x,1,e-1)
}
BEGIN {
  if(kind=="app") {
    root="extend_features"; element="app_feature"
    add[1]="com.android.launcher.support_stack_recents"
    add[2]="com.android.launcher_card_force_enable"
    add[3]="com.android.launcher_group_card_force_enable"
    argument[add[3]]="boolean:true"
    nadd=3
    remove["com.oplus.wallpapers.LIGHT_WEIGHT_OS_FUNC"]=1
    remove["speechassist.cui.device.light.low"]=1
    remove["speechassist.cui.device.light"]=1
  } else if(kind=="oplus") {
    root="oplus-config"; element="oplus-feature"
    add[1]="oplus.software.support_fluid_entry"
    add[2]="oplus.software.fluid_replace_ntf"; nadd=2
  } else fail("Unknown feature kind")
}
{ document=document $0 "\n" }
END {
  if(failed)exit 2
  rest=document; result=""; opened=0; closed=0
  while(length(rest)) {
    start=index(rest,"<")
    if(!start){result=result rest; break}
    result=result substr(rest,1,start-1); rest=substr(rest,start)
    if(substr(rest,1,4)=="<!--") {
      e=index(rest,"-->"); if(!e)fail("Unterminated XML comment")
      e+=2
    } else if(substr(rest,1,9)=="<![CDATA[") {
      e=index(rest,"]]>"); if(!e)fail("Unterminated CDATA")
      e+=2
    } else {
      e=index(rest,">"); if(!e)fail("Unterminated XML tag")
    }
    tag=substr(rest,1,e); rest=substr(rest,e+1)
    if(tag ~ ("^<" root "[[:space:]>]"))opened++
    if(tag ~ ("^</" root "[[:space:]]*>$")) {
      closed++
      if(primary==1)for(i=1;i<=nadd;i++)if(!seen[add[i]])
        result=result "\t<" element " name=\"" add[i] "\"" (argument[add[i]]?" args=\"" argument[add[i]] "\"":"") "/>\n"
    }
    if(tag ~ ("^<" element "[[:space:]]")) {
      name=feature_name(tag)
      if(name in remove){if(tag!~/\/[[:space:]]*>$/)fail("Nonempty target feature");continue}
      replace=0
      if(primary==1)for(i=1;i<=nadd;i++)if(name==add[i])replace=1
      if(replace) {
        if(tag!~/\/[[:space:]]*>$/)fail("Nonempty target feature")
        if(seen[name]++)continue
        tag="<" element " name=\"" name "\"" (argument[name]?" args=\"" argument[name] "\"":"") "/>"
      }
    }
    result=result tag
  }
  if(opened!=1||closed!=1)fail("Unexpected feature XML root")
  printf "%s",result
}
