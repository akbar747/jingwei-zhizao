# 经纬智造 · 花楼提花机的可编程密码

面向第十四届全国大学生数字媒体科技作品及创意竞赛的桌面交互软件项目。当前仓库处于 **MVP 原型阶段**，已经打通：

```text
点阵绘制 → PatternGrid领域模型 → 花本编译 → 去重指令 → 织物矩阵
```

## 当前可用功能

- 16×16默认点阵画布。
- 左键绘制、右键擦除、橡皮模式、清空纹样。
- 按行扫描纹样，提取被提升的经线。
- 相同提升组合自动复用同一花本编号。
- 显示原始行数、唯一花本数、压缩率和花本列表。
- 修改纹样后自动将旧编译结果标记为“已过期”。
- 核心织物矩阵生成和非法数据校验。
- Windows离屏冒烟测试，无需人工点击即可验证应用接线。

## 当前界面截图

![MVP绘制与编译界面](docs/screenshots/mvp-drawing-compile.png)

该截图由Qt离屏渲染生成，用于自动验证界面结构；真实Windows运行仍需要项目负责人进行鼠标和视觉验收。

## 尚未实现

- 织造动画和花楼/综片/梭子可视化。
- PNG、CSV、WIF导出。
- 保存/打开 `.jwg` 工程。
- 撤销、重做、直线、矩形和填充工具。
- PyInstaller可执行程序。

这些功能属于后续迭代，不应在当前MVP中混入。

## 项目结构

```text
jingwei-zhizao/
├─ pyproject.toml
├─ src/jingwei/
│  ├─ __main__.py
│  ├─ application/
│  │  └─ compile_service.py
│  ├─ domain/
│  │  ├─ models.py
│  │  ├─ compiler.py
│  │  └─ weaver.py
│  └─ ui/
│     ├─ canvas_geometry.py
│     ├─ pattern_canvas.py
│     └─ main_window.py
├─ tests/
│  ├─ domain/
│  ├─ ui/
│  ├─ test_compile_service.py
│  └─ test_smoke.py
└─ docs/
   ├─ ai-log/
   ├─ design/
   ├─ review/
   └─ superpowers/
```

## 安装

建议使用项目内虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

`pyproject.toml` 固定使用 `PySide6-Essentials==6.11.2`。该包包含本阶段所需的 QtWidgets、QtGui、QtCore 和 QtTest，不包含未使用的 Qt Addons，可以减小开发和打包体积。

## 运行

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m jingwei
```

## 自动测试

```powershell
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

运行无窗口冒烟检查：

```powershell
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m jingwei --smoke-test
```

## 核心语义

- 点阵单元 `True`：该列经线在对应梭次被提升。
- 点阵单元 `False`：该列经线不提升。
- 花本编号 `C01`、`C02`：按首次出现顺序分配。
- 织物矩阵：提升经线覆盖当前纬线记为 `True`，否则为 `False`。

当前模型是为教学演示设计的确定性模型，不宣称是对某台实体花楼提花机的逐零件工程复刻。

## 开发要求

- 领域层不得导入 PySide6。
- 所有核心算法必须在GUI之外可测试。
- 新行为先写失败测试，再写实现。
- 代码保持离线可运行，不调用外部API。
- AI参与记录保存在 `docs/ai-log/`，不能事后伪造或省略。

## Git与GitHub

当前提交历史保存在本地Git仓库。尚未配置GitHub远端；需要项目负责人提供仓库URL，或先完成GitHub登录。未确认前不创建公开仓库、不推送任何代码。

## 素材与合规

- 当前代码没有使用第三方纹样、照片、字体或音乐。
- 后续加入民族纹样示例时，必须记录来源、授权和人工设计过程。
- 参赛申报中的AI使用情况以 `docs/ai-log/ai-usage.jsonl` 为准逐项核对。
