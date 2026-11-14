# 第三方来源与许可边界

本仓库公开模块脚本、自写 Java 辅助代码、打包脚本与来源清单。未统一指定项目开源许可证；公开可读不等于所有文件均获得同一种再分发许可。第三方文件保留各自权利。

1. 原特性参考与 OEM 应用扩展：
   https://github.com/CiZhanYue/magisk-ColorOSCommonFeatureSupplements
   组件来自原应用扩展 v1.1，保持原签名；版本、来源和哈希见 `work/public_v2/components/provenance.json`。OEM APK 与库不属于本项目自写源码，也未包含在 Git 仓库。
2. 独立挂载机制参考：
   https://github.com/backslashxx/mountify/tree/standalone-script
   采用 Unlicense；原许可证与改动说明保留于 `work/public_v2/components/MOUNT-LICENSE`、`MOUNT-SOURCE.txt`，最终脚本快照中亦保留。用于限定组件的挂载，非全局挂载器。
3. Zygisk Next 1.5.3 build 880：
   https://github.com/Dr-TSNG/ZygiskNext/releases/tag/v1.5.3
   此源码仓库不包含框架 ZIP，遵循其上游许可与使用要求。
4. LSPosed Irena 2.0.0 build 7316：
   https://github.com/re-zero001/LSPosed-Irena/releases/tag/2.0.0
   框架源码、配置结构和许可见上游仓库。此处只包含本项目配置辅助器及传统 Xposed 接口调用代码，不把第三方框架宣称为自写成果。
5. 原厂主题资源来源：
   https://gitlab.com/rama-firmware-dumps/oneplus/CPH2719
   固定 commit：`38076cbb63f3b0234e27114bf8352d16801612e6`。本仓库仅保存目录元数据、来源与哈希记录，不分发原厂图片或其他主题素材；见 `work/public_v2/themes/payload/source-manifest.json`。

本项目与 OPPO、ColorOS 无官方关系。第三方组件能否再分发，不能由本项目自行授予许可。修改或发布衍生包时应自行核实对应文件的权利与许可。
