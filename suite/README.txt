ColorOS native suite 2.3 test / 2026-11-10
One ZIP installs the feature layer, five missing OEM apps, one native repair Hook, and missing pinned framework dependencies.
No fixed model, firmware or ColorOS version restriction. APK ABI, page-size, XML structure and signature checks are retained.
Current actual test device: OPPO PLT120, ColorOS 15.0.2.1005. ColorOS 16 is unverified; interface mismatch skips the Hook.
Native lockscreen clock editor includes weather/lunar information, clock styles and fonts. This is not proof of an arbitrary agenda-widget picker.
Missing OEM inspiration-template groups are appended from a pinned public firmware resource tree. Existing device groups are retained. Native editor/schema/style-asset compatibility is checked before mounting; an incompatible theme part is skipped. No APK is replaced and no theme is automatically applied. Theme-resource provenance and hashes are included under parts/themes/payload/source-manifest.json. Unrelated live-wallpaper and global animation gates are preserved.
AI/video/order services require OEM support and user consent/account. Installed packages alone do not verify complete workflows.
The Xiaobu suggestions container override has args=boolean:true: UMS reads its boolean value, not only its presence. The OEM card resource already exists and is not a third-party replacement.
Both speechassist.cui.device.light.low and speechassist.cui.device.light declarations are removed. This changes the native lightweight-mode branch and isLightSystem request flag; it does not replace OEM cloud configuration or impersonate another model.
KernelSU-family first-time framework installation may require two reboots, but the ZIP is flashed once. Existing compatible framework users need one reboot.
The framework configuration helper changes only cn.local.plt120.recentsfix, owner-user 0, with Launcher scope, using a checked schema and an atomic SQLite transaction.
Disable and reboot reverses XML/APK mounting and disables the suite Hook through its boot-session activation property. Uninstall removes the suite Hook APK automatically.
The original companion from this task is disabled automatically. It is not deleted or re-enabled on uninstall. Existing frameworks are not removed automatically.
