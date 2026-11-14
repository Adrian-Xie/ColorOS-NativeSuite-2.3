# 源码构建说明

本仓库保留原开发工程的 `work/` 相对布局。只提供可审阅的自写代码和脚本、来源与哈希清单；不包含设备导出内容或二进制依赖。源码快照不能直接作为模块 ZIP 使用。

## 工具链

原构建脚本使用 Windows、Python 3.10+、JDK、Android SDK Build Tools 35.0.0、Android API 35 的 android.jar，以及传统 Xposed API 82。自行按官方渠道准备，放入：

```text
work/v2_research/toolchain/
  jdk/.../bin/java.exe
  build-tools-35.0.0/.../aapt2.exe
  platforms-android-35/.../android.jar
  xposed-api82.jar
```

脚本采用该 Windows 工具链布局，未承诺跨平台构建。

## 编译自写部分

使用自己的签名证书。设置 `COLOROS_KEYSTORE` 为本机私钥路径，`COLOROS_KEYSTORE_PASSWORD` 为口令，`COLOROS_KEY_ALIAS` 为别名（默认 `coloros-native-suite`）。私钥和口令不得提交仓库。

```text
python work/build_public_hooks.py recents_repair
python work/build_scope_helper.py
python work/build_theme_helper.py
```

输出分别为 `outputs/hooks/ColorOS_RecentsRepair_0.4.apk`、`work/suite_research/scope-helper/classes.dex` 与 `work/suite_research/theme-helper/classes.dex`。自签名 APK 不能直接覆盖发布者不同证书的同包名 APK；先备份配置并按 Android 的签名规则处理。

## 准备原厂及框架输入

构建者自行提供匹配来源清单的文件；仓库不自动下载或授权再分发这些第三方组件。

- `work/public_v2/components/system/product/app/`：按 `apks.tsv`、`native-libs.tsv` 中的相对路径准备原签名 APK 和库（路径相对于 `components/`）。来源及哈希见 `components/provenance.json`。来源应用扩展为上游 v1.1，主功能仓库版本与扩展版本分别计数。
- `work/oem_theme_payload/`：主题构建器的输入目录。在其中放入 `assets/`、`groups.json` 与 `source-manifest.json`。两个 JSON 的参考副本位于 `work/public_v2/themes/payload/`，原厂资源需按清单另行准备。
- 可核对指定固件树与 commit；`fetch_oem_themes.py` 依赖事先准备的 `work/suite_research/donor-sparse` 固件 Git 检出及 `donor-inspiration_theme_templates.json`，它不是通用一键下载器。
- 准备主题输入后运行 `python work/build_oem_theme_part.py`。它从 `work/oem_theme_payload/` 复制到 `work/public_v2/themes/payload/`，并更新主题部分的完整性清单。
- `work/v2_research/hook_versions/`：准备以下未经改动的上游 ZIP。整合脚本会核对哈希。

| 文件 | SHA256 |
| --- | --- |
| Zygisk-Next-1.5.3-880-22a1bf5-release.zip | 186a0a26c9fcb895af1954b42de831433c23d72d1bd0758b986069154359db67 |
| LSPosed-v2.0.0-7316-Irena-release.zip | 1f843e0b5062666ce4d8e8eecbb8510497419175b3c3fd1898f885c7cae37cd1 |

也可以从自己持有、核验过的 2.3 发布 ZIP 恢复对应的缺失二进制输入，保持 ZIP 内的相对目录；不要把原来生成的整机 XML、安装日志或运行时状态复制进源码。

最后运行 `python work/build_suite.py`，输出位于 `outputs/integrated/`。脚本会生成完整 payload 哈希并检查 ZIP CRC。修改文件后应重新生成清单，不能把只含文本的源码快照改扩展名后刷入。

## 快照与验证边界

`work/coloros_native_suite/` 保存发布包对应的脚本，供对照最终运行行为；原二进制的哈希记录在 `docs/*payloads-2.3.sha256`，其中列出的二进制没有随源码分发。

本次公开整理仅验证源码隐私、Python 语法、引用文件与归档完整性，没有在干净机器上完成含全部外部依赖的独立重建。未公开原签名私钥，因此不承诺字节级复现已签名 APK 或整合 ZIP。

没有发布手机序列号、账号数据、截图、设备连接配置、日志或应用数据库。
