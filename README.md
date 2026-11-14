# ColorOS 原生功能整合补全 2.3（公开测试版）

为 OPPO ColorOS 15 补全部分原厂特性：流体云配套、小布普通模式及建议卡片容器、桌面堆叠与卡片、原厂主题资源、堆叠修复 Hook。一包安装，无固定机型 / 固件号 / ColorOS 版本上限校验，无外部“元模块”依赖。

> **公开测试版，不是“满血 AI”版。** 小布建议卡片添加仍失败、一键问屏、AI 视频总结、票务识别并加入日历未完成验收，外卖 / 打车的真实订单展示也未做业务测试。详细结果见 [验收记录.md](验收记录.md)。

## 实测设备

- OPPO A6k 5G（PLT120），ColorOS 15.0.2.1005(CN01)，Android 15，ARM64，4KB 内存页
- ColorOS 16 尚未实机验证，不能描述为已经通用兼容

## 这个仓库里有什么

这是**源码包**，用于审阅构建脚本和 Hook，不是可直接刷机的安装包，也不是一键构建环境：

- `build_suite.py` / `build_oem_theme_part.py` / `build_public_hooks.py` / `build_scope_helper.py`：构建脚本
- `check_suite.py`：验收检查脚本（依赖本地 `adb_readonly` 模块，不在包内）
- `public_v2/recents_repair/`：桌面堆叠修复 Hook 的 Java 源码
- `helpers/`：`ScopeSetup.java`、`ThemeSetup.java`
- `suite/`：刷机包内的脚本、配置、主题轮廓数据（`*.sh`、`module.prop`、`patch_features.awk` 等）
- `发布说明.md` / `验收记录.md`：发布说明与实测验收记录

## 这个仓库里没有

- **没有可刷机的安装包**（`ColorOS_NativeSuite_2.3-test.zip` 不在内）
- **没有原厂 APK**（5 个缺失的原厂组件 APK 不在内）
- **没有 Zygisk Next / LSPosed 框架安装包**（只在 `suite/SOURCES.txt` 和 `suite/payloads.sha256` 里列出了来源和哈希）
- **没有签名私钥、没有用户日志、没有应用数据库**

`build_suite.py` 引用的是原作者电脑上的 `work/`、`outputs/` 等本地路径，这些路径不在仓库内；`suite/payloads.sha256` 对应的是完整可刷机包，其中很多条目（原厂 APK、框架 zip、主题 `.webp` 资源等）在这个源码包里并不存在。请以仓库内实际文件为准。

原厂 APK 与框架的来源见 `suite/SOURCES.txt`。

## 安装（使用完整刷机包时）

用 KernelSU 系管理器从完整 ZIP 安装，重启。Action 可查看挂载、包注册、流体云能力返回和 Hook 状态。首次部署框架可能需要两次重启，无需重复刷包。

在 Root 管理器停用此整合模块并重启，可撤销配置、资源和 APK 挂载；卸载模块会删除配套修复 APK。不要与原仓库大而全的补全模块 / 应用扩展同时启用。

小布登录不等于识屏、智慧决策等每个独立服务均已同意协议；首次隐私条款、权限、第三方服务绑定需本人处理，模块不代点同意、不全量授权。

## 隐私说明

本仓库不含 IMEI、序列号、手机号、邮箱、账号、密码、私钥、运行日志或数据库。测试设备信息（机型、ColorOS 版本）予以保留，因为这是判断该模块在哪些设备上实测过、哪些版本尚未验证的必要信息；本地测试签名文件路径与口令已在公开前从 `build_public_hooks.py` 中移除，请使用自己的签名文件。
