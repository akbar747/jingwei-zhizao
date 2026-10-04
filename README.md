# 经纬智造 · 花楼提花机的可编程密码

> 一款把中国传统花楼提花工艺转化为“可设计、可编译、可织造、可验证”交互体验的非遗文化教育软件。

[![Windows Tests](https://github.com/akbar747/jingwei-zhizao/actions/workflows/tests.yml/badge.svg)](https://github.com/akbar747/jingwei-zhizao/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white)
![Status](https://img.shields.io/badge/Status-MVP-2F6F5E)

参赛方向：第十四届全国大学生数字媒体科技作品及创意竞赛  
赛道定位：指定命题类——民族文化创新表达  
作品形态：Windows离线桌面软件  
当前状态：MVP原型已完成，核心链路已通过自动测试

![MVP绘制与编译界面](docs/screenshots/mvp-drawing-compile.png)

## 一键下载安装

前往 [最新Release](https://github.com/akbar747/jingwei-zhizao/releases/latest) 下载对应文件：

- `JingweiZhizao-Setup-0.1.4.exe`：推荐，双击安装，无需Python和管理员权限。
- `JingweiZhizao-Portable-0.1.4.zip`：解压后直接运行，适合演示和课堂临时使用。
- `SHA256SUMS.txt`：发布文件SHA256校验值。
## 评审快速体验

1. 启动软件后，在中央点阵画布中使用左键绘制纹样。
2. 使用右键或“橡皮”按钮擦除错误单元。
3. 点击左侧“编译花本”。
4. 在右侧查看原始织造行、唯一花本数量、压缩率和指令列表。
5. 修改纹样后，界面会提示旧结果已过期；重新编译即可得到新结果。

## 一、项目解决的问题

传统提花工艺展示常见两个问题：观众只能看到复杂的织机和漂亮成品，却看不懂“纹样如何变成机械动作”；普通计算机教学又很少能从真实文化工艺切入。

《经纬智造》把两者连接起来。用户不是在软件里观看一段织布动画，而是在点阵画布中亲自设计纹样，再观察软件如何把纹样编译成花本指令、控制经线提升并生成织物结果。

核心链路：

```text
点阵纹样
   ↓ 逐行解析
提升经线集合
   ↓ 相同组合去重
花本提花指令 C01、C02……
   ↓ 状态推进
织物矩阵与成品预览
```

## 二、创新点

### 1. 不是动画播放器，而是可验证映射

每个织物单元都能追溯到原始纹样位置、花本编号、提升经线和对应梭次。视觉动画负责表现状态，结果本身由确定性算法生成。

### 2. 把“花本”解释为可执行程序

软件把连续相同的提升行合并成可复用指令，直观展示：

- 离散数据如何表达图案；
- 指令如何存储和复用；
- 机械如何读取并执行信息；
- 输入变化如何影响织造结果。

### 3. 民族文化与计算机科普的双向翻译

界面同时保留两套语言：

| 工艺术语 | 计算类比 |
|---|---|
| 点阵纹样 | 输入数据 |
| 花本 | 指令集或程序数据 |
| 提升组合 | 状态参数 |
| 综片/花楼 | 执行机构 |
| 梭子 | 数据写入 |
| 打纬 | 状态提交 |
| 织物矩阵 | 输出结果 |

### 4. 面向课堂与博物馆的真实应用

目标用户包括中学信息科技、劳动教育学生、博物馆科普观众和非遗教育工作者。软件不依赖网络，可以在普通Windows电脑、触摸屏或教学机房中运行。

## 三、功能完成度

| 模块 | 当前状态 | 验证证据 |
|---|---|---|
| 点阵绘图与擦除 | 已完成 | 真实鼠标交互测试 |
| 纹样边界与矩阵校验 | 已完成 | PatternGrid单元测试 |
| 花本编译与重复行复用 | 已完成 | 编号顺序与次数测试 |
| 织物矩阵生成 | 已完成 | 确定性与非法输入测试 |
| 结果过期提示 | 已完成 | 主窗口冒烟测试 |
| 织造动画与梭子可视化 | 计划中 | 尚未实现 |
| PNG、CSV、WIF导出 | 计划中 | 尚未实现 |
| Windows免安装程序 | 计划中 | 尚未实现 |

### 已完成MVP

- 16×16默认点阵画布。
- 左键绘制、右键擦除、橡皮模式、清空纹样。
- 按行解析纹样并提取被提升的经线。
- 相同提升组合自动复用同一花本编号。
- 显示原始织造行、唯一花本数量、压缩率和花本列表。
- 修改纹样后自动提示“结果已过期”。
- 织物矩阵生成和非法数据校验。
- Qt离屏冒烟测试，可在无人点击环境验证主流程。
- Windows CI自动测试配置。

## 四、尚未实现

以下功能属于后续迭代，不应混入当前MVP验收：

- 花楼、综片、梭子和筘的织造动画。
- 织物成品实时生长预览。
- PNG、CSV和WIF导出。
- `.jwg`工程保存与恢复。
- 撤销、重做、直线、矩形、填充和镜像工具。
- PyInstaller免安装Windows程序。
- 用户测试和兼容性测试报告。

## 五、技术架构

```text
表现层 presentation
  MainWindow
  PatternCanvas
  Canvas Geometry

应用层 application
  CompileService

领域层 domain
  PatternGrid
  CompilePattern / WeavePlan / Card / Pick
  WeaveMatrix

测试
  Unit Tests
  Qt Offscreen GUI Tests
  Application Smoke Test
```

技术选型：

- Python 3.14
- PySide6-Essentials 6.11.2
- Python标准库 `unittest`
- 领域层零Qt依赖
- 当前运行完全离线，不调用外部API

## 六、核心语义

- `True`：该列经线在对应梭次被提升。
- `False`：该列经线不提升。
- 花本编号按首次出现顺序分配：`C01`、`C02`、`C03`。
- 织物矩阵：提升经线覆盖当前纬线记为 `True`，否则为 `False`。

当前模型是为教学演示设计的确定性模型，不宣称是对某台实体花楼提花机的逐零件工程复刻。

## 七、安装与运行

```powershell
git clone https://github.com/akbar747/jingwei-zhizao.git
cd jingwei-zhizao
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m jingwei
```

## 八、自动测试

```powershell
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

无窗口冒烟检查：

```powershell
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m jingwei --smoke-test
```

当前验证结果：

```text
Ran 31 tests
OK
Smoke test exit code: 0
```

## 九、项目结构

```text
jingwei-zhizao/
├─ .github/workflows/         GitHub Actions
├─ src/jingwei/
│  ├─ application/            应用服务
│  ├─ domain/                 纯Python领域模型与算法
│  └─ ui/                     PySide6界面
├─ tests/                     单元测试、GUI测试与冒烟测试
├─ docs/
│  ├─ ai-log/                 AI使用证据
│  ├─ design/                 UI与交互设计
│  ├─ review/                 评审清单
│  ├─ screenshots/            展示截图
│  └─ superpowers/            策划书与实施计划
├─ pyproject.toml
└─ README.md
```

## 文档导航

- [项目策划书](docs/superpowers/specs/2026-10-04-jingwei-zhizao-design.md)
- [UI交互设计](docs/design/ui-interaction-design.md)
- [MVP实施计划](docs/superpowers/plans/2026-10-04-mvp-drawing-compile.md)
- [AI使用记录](docs/ai-log/2026-10-04.md)
- [GitHub发布指南](docs/github-publish-guide.md)
- [测试说明](tests/README.md)

## 十、开发与质量控制

- 领域层不得导入PySide6。
- 所有核心算法必须在GUI之外可测试。
- 新行为先写失败测试，再写最小实现。
- 使用确定性算法，相同输入必须得到相同输出。
- 每次代码变更必须运行完整测试。
- 不把生成缓存、虚拟环境、密钥或来源不明素材提交到仓库。

## 十一、AI使用与原创性

本项目的AI参与记录保存在 [`docs/ai-log/`](docs/ai-log/)。记录内容包括工具名称、使用环节、输入、输出、人工修改和核验状态。

当前软件运行时**不调用任何AI接口**。AI主要用于辅助需求整理、代码生成、测试设计和文档初稿，最终功能、边界和采用内容由项目团队审核。

## 十二、当前限制

- 尚未在真实Windows窗口进行最终视觉验收。
- 尚未完成打包后的独立运行测试。
- 历史说明和民族文化来源需要项目负责人进一步核验。
- 当前纹样编辑只支持基础点阵和单色提升模型。

## 十三、后续路线

1. 接入织造模拟预览，逐梭显示花楼、经线、梭子和织物生长。
2. 增加保存/打开、撤销/重做、PNG/CSV/WIF导出。
3. 完成PyInstaller打包与Windows 10/11兼容性测试。
4. 增加真实用户测试，记录完成时间和学习效果。
5. 形成演示视频脚本、作品介绍、原创声明和AI使用说明。
6. 在不影响核心闭环的前提下增加民族纹样示例和课堂任务。

## 十四、仓库说明

本仓库当前用于竞赛作品开发与版本管理。正式提交前，所有示例素材、历史说明和AI使用记录都必须完成来源核验。