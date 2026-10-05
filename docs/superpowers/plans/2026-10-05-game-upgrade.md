# 织造工坊游戏化升级 Implementation Plan

**Goal:** 将现有“点阵绘图 + 花本编译”原型升级为有关卡目标、评分、星级和逐梭织造演出的游戏化体验。

**Architecture:** 新增纯Python游戏领域层，负责关卡定义、目标匹配和星级评分；UI层新增HUD、目标预览、实时评分和WeavePreview动画组件。花本编译与织物矩阵仍由现有domain负责，游戏层只读取它们。

**Tech Stack:** Python 3.13+、PySide6、标准库unittest、QTimer/QPainter。

**Spec:** `docs/superpowers/specs/2026-10-04-jingwei-zhizao-design.md`

## Global Constraints

- 不修改现有花本编译语义和织物矩阵算法。
- 游戏逻辑必须无Qt依赖并可单元测试。
- 首版只做3个关卡，不引入联网或大型资源。
- 评分必须稳定、可解释，并区分纹样匹配与花本压缩。
- 动画必须读取WeavePlan和WeaveMatrix，不自行计算另一套结果。

## Review Focus

- 目标纹样与玩家纹样尺寸不一致时必须有确定性处理。
- 空白纹样不能获得高分或星级。
- 动画单步推进必须与当前梭次、完成矩阵一致。
- 切换关卡时必须清理旧编译结果和动画状态。
- 游戏化反馈不能破坏原有绘图、编译和冒烟测试。

---

### Task 1: 游戏关卡与评分领域

**Files:** `src/jingwei/game/levels.py`, `src/jingwei/game/scoring.py`, `tests/game/test_scoring.py`

- [ ] 写失败测试：完全匹配得高分三星；部分匹配按比例得分；空纹样零星。
- [ ] 实现LevelDefinition与ScoreEngine，评分由匹配率70%和花本压缩30%构成。
- [ ] 运行测试并提交。

### Task 2: 三个教学关卡

**Files:** `src/jingwei/game/catalog.py`, `tests/game/test_catalog.py`

- [ ] 定义8×8“第一根经线”、12×12“菱纹锦”、16×16“万纹回环”。
- [ ] 测试每个关卡尺寸、目标和至少一条可复用行。
- [ ] 提交。

### Task 3: 织造预览动画组件

**Files:** `src/jingwei/ui/weave_preview.py`, `tests/ui/test_weave_preview.py`

- [ ] 写离屏测试：空计划不可播放；单步推进一梭；重置归零；完成信号只发一次。
- [ ] 实现WeavePreview，读取WeavePlan/WeaveMatrix，用QPainter绘制经线、梭子和已织区域。
- [ ] 提交。

### Task 4: 主窗口游戏化改造

**Files:** `src/jingwei/ui/main_window.py`, `tests/test_smoke.py`

- [ ] 增加顶部HUD：关卡名、目标、得分、星级和进度。
- [ ] 增加目标纹样预览、关卡切换、一键载入示例。
- [ ] 编译后评分；点击“开始织造”切换到动画预览。
- [ ] 保持原有画布、编译报告与冒烟接口兼容。
- [ ] 提交。

### Task 5: 完成反馈与视觉打磨

**Files:** `src/jingwei/ui/main_window.py`, `src/jingwei/ui/weave_preview.py`

- [ ] 完成时显示星级、得分和“继续下一关”。
- [ ] 增加织造中的交替高亮、布料生长和状态文案。
- [ ] 全量测试、截图检查、打包测试。
- [ ] 合并回main。