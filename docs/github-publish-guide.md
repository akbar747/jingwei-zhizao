# GitHub发布指南

本指南用于把本地仓库发布到GitHub。不要在公开聊天或命令中粘贴GitHub密码、个人访问令牌或SSH私钥。

## 一、在GitHub创建仓库

1. 登录GitHub，点击右上角“+”→“New repository”。
2. 仓库名建议：`jingwei-zhizao`。
3. Description建议：`花楼提花机可编程密码——民族文化与计算机科普桌面交互软件`。
4. 开发阶段建议选择 **Private**，避免参赛创意过早公开；比赛提交后再决定是否改为Public。
5. **不要**勾选“Add a README”“Add .gitignore”或“Choose a license”，因为本地仓库已经包含这些内容。
6. 点击“Create repository”。

## 二、复制远端地址

HTTPS格式：

```text
https://github.com/<你的用户名>/jingwei-zhizao.git
```

SSH格式：

```text
git@github.com:<你的用户名>/jingwei-zhizao.git
```

## 三、关联本地仓库

在PowerShell中执行：

```powershell
cd D:\aicode\jingwei-zhizao
git remote add origin https://github.com/<你的用户名>/jingwei-zhizao.git
git remote -v
```

如果已经存在名为`origin`的远端，使用：

```powershell
git remote set-url origin https://github.com/<你的用户名>/jingwei-zhizao.git
```

## 四、推送main分支

```powershell
git push -u origin main
```

首次推送时，Git Credential Manager可能打开浏览器登录。不要输入GitHub账号密码；应使用浏览器授权或Personal Access Token。

成功标志：

```text
branch 'main' set up to track 'origin/main'
```

## 五、验证

```powershell
git status
git branch -vv
git ls-remote --heads origin main
```

预期：

- `git status`显示`working tree clean`；
- 本地`main`跟踪`origin/main`；
- GitHub仓库能看到README、src、tests、docs和GitHub Actions。

## 六、仓库展示设置

1. 将默认分支设为`main`。
2. 添加Topics：`digital-media`、`cultural-heritage`、`jacquard-loom`、`python`、`pyside6`、`education`。
3. 在About中填写项目简介和主页链接（如有）。
4. 在Actions中确认Windows Tests通过。
5. 截图和README更新后及时提交，不要在比赛现场临时改代码。

## 七、后续更新流程

```powershell
git switch main
git pull --ff-only
# 修改代码或文档
git add .
git commit -m "feat: describe the change"
git push
```

每一步提交前运行：

```powershell
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m jingwei --smoke-test
```