# Windows Installer and GitHub Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为`v0.2.2`建立可一键下载安装的Windows安装程序、便携版ZIP和自动GitHub Release流程。

**Architecture:** PyInstaller把Python/PySide6应用构建为`--onedir --windowed`目录；PowerShell脚本运行测试、生成便携ZIP、调用Inno Setup生成无管理员权限的安装程序并计算SHA256；GitHub Actions在`v*`标签推送时构建并调用`gh release create`发布全部资产。

**Tech Stack:** Python 3.14、PySide6-Essentials 6.11.2、PyInstaller 6.22.3、Inno Setup 6、PowerShell、GitHub Actions、GitHub CLI。

**Spec:** `docs/superpowers/specs/2026-10-04-jingwei-zhizao-design.md`

## Global Constraints

- 安装包必须支持 Windows 10/11 64位。
- 最终用户无需安装Python或PySide6。
- 应用核心功能必须离线运行。
- 安装范围使用当前用户目录，默认不请求管理员权限。
- 版本号以`pyproject.toml`的`0.2.2`为单一事实来源。
- 发布资产命名必须稳定：`JingweiZhizao-Setup-0.2.2.exe`和`JingweiZhizao-Portable-0.2.2.zip`。
- GitHub Release由标签`v0.2.2`触发，不手工上传构建目录。

## Review Focus

- PyInstaller是否收集完整Qt插件，打包程序启动不能出现DLL或platform plugin错误。
- 安装程序是否写入用户目录，不能因权限问题失败。
- 版本号在pyproject、安装程序和Release名称之间必须一致。
- ZIP解压后必须能直接运行，不依赖仓库或虚拟环境。
- Release工作流失败时要能通过Actions定位构建步骤，不能生成半成品Release。

---

### Task 1: 发布配置契约测试

**Files:**
- Create: `tests/test_release_config.py`
- Create: `packaging/windows/installer.iss`
- Create: `scripts/build_release.ps1`
- Create: `.github/workflows/release.yml`
- Create: `docs/releases/v0.2.2.md`
- Modify: `pyproject.toml`
- Modify: `.gitignore`

- [ ] 写失败测试，验证版本、资产命名、安装范围、标签触发和Release说明文件。
- [ ] 运行测试并确认因发布文件缺失而失败。
- [ ] 添加最小发布配置，使测试通过。

### Task 2: PyInstaller本地构建

**Files:**
- Modify: `scripts/build_release.ps1`
- Modify: `pyproject.toml`

- [ ] 在虚拟环境安装固定版本PyInstaller。
- [ ] 运行脚本构建`dist/JingweiZhizao/JingweiZhizao.exe`。
- [ ] 使用`--smoke-test`运行打包EXE并确认退出码0。
- [ ] 生成并检查便携ZIP内容。

### Task 3: Inno Setup安装程序

**Files:**
- Modify: `packaging/windows/installer.iss`
- Modify: `scripts/build_release.ps1`

- [ ] 安装Inno Setup编译器，或确认GitHub runner可用路径。
- [ ] 编译安装程序，检查安装目录、快捷方式、卸载项和无需管理员权限设置。
- [ ] 对安装程序计算SHA256。

### Task 4: 自动Release工作流

**Files:**
- Modify: `.github/workflows/release.yml`

- [ ] 工作流在`v*`标签推送时运行。
- [ ] 安装构建依赖和Inno Setup。
- [ ] 运行应用测试和打包脚本。
- [ ] 使用`GITHUB_TOKEN`调用`gh release create`，上传安装程序、便携ZIP和SHA256。
- [ ] 工作流失败时不创建部分Release。

### Task 5: README和Release说明

**Files:**
- Modify: `README.md`
- Modify: `docs/releases/v0.2.2.md`

- [ ] README增加“一键下载安装”入口、安装步骤、便携版说明和系统要求。
- [ ] Release说明列出主要功能、已知限制、安装方式和校验文件。
- [ ] 确认所有相对链接可用。

### Task 6: 发布v0.2.2

- [ ] 运行31项测试和冒烟检查。
- [ ] 提交发布工程并推送到`main`。
- [ ] 创建并推送标签`v0.2.2`。
- [ ] 等待Release工作流完成。
- [ ] 验证Release页面存在`Setup.exe`、`Portable.zip`和`SHA256SUMS.txt`。
- [ ] 下载至少一个安装资产并校验SHA256。