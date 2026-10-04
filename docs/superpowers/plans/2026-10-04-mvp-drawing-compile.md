# 点阵绘制与花本编译 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 提供一个可运行的 Windows 桌面最小原型，让用户能够绘制点阵纹样、编译成去重后的花本提花指令，并生成可核验的织物矩阵。

**Architecture:** 领域层使用纯 Python 数据模型与确定性算法，不依赖GUI；应用层负责调用编译流程；表现层使用 PySide6 Widgets，画布通过鼠标事件更新 `PatternGrid`，编译按钮调用应用服务并在右侧显示结果。核心逻辑和GUI坐标换算都可独立测试。

**Tech Stack:** Python 3.14、PySide6 6.11.x、标准库 `unittest`、Git；不使用网络、数据库或第三方算法库。

**Spec:** `docs/superpowers/specs/2026-10-04-jingwei-zhizao-design.md`

## Global Constraints

- 平台：Windows 10/11 64位。
- 运行：核心功能完全离线。
- 画布：默认 16×16，允许 4–64 行列。
- 单元语义：`True` 表示该经线在第N梭被提升，`False` 表示不提升。
- 织物简化规则：提升的经线覆盖当前纬线；未提升的经线位于纬线下方。
- 代码：所有核心逻辑写详细注释；领域层不得导入PySide6。
- 测试：每个行为先写失败测试，再写最小实现。
- 本阶段不做：自动播放动画、PNG/WIF导出、多色纬线、云同步。

## Review Focus

- 输入尺寸为最小/最大边界时，画布和编译不能越界或崩溃。
- 空纹样可以编译但必须产生明确警告，不能伪装成正常作品。
- 相同提升行必须复用同一花本编号，编号顺序必须稳定。
- 鼠标坐标落在单元边界或窗口缩放后，不能出现一格偏移。
- 用户修改纹样后，旧的编译结果必须被标记为过期，不能继续冒充最新结果。

---

### Task 1: 项目骨架与PatternGrid领域模型

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `src/jingwei/__init__.py`
- Create: `src/jingwei/domain/__init__.py`
- Create: `src/jingwei/domain/models.py`
- Create: `tests/__init__.py`
- Create: `tests/domain/__init__.py`
- Create: `tests/domain/test_models.py`

**Interfaces:**
- Produces: `PatternGrid(width: int, height: int, cells: list[list[bool]] | None = None)`
- Produces: `PatternGrid.set(x: int, y: int, value: bool) -> None`
- Produces: `PatternGrid.get(x: int, y: int) -> bool`
- Produces: `PatternGrid.toggle(x: int, y: int) -> bool`
- Produces: `PatternGrid.clear() -> None`
- Produces: `PatternGrid.copy() -> PatternGrid`
- Produces: `PatternGrid.is_empty() -> bool`
- Produces: `PatternGrid.row(y: int) -> tuple[bool, ...]`
- Produces: `PatternGrid.to_matrix() -> tuple[tuple[bool, ...], ...]`

- [ ] **Step 1: Write the failing test**

Test `tests/domain/test_models.py` with `unittest`:

```python
class PatternGridTests(unittest.TestCase):
    def test_new_grid_is_empty_and_has_requested_size(self):
        grid = PatternGrid(3, 2)
        self.assertEqual(grid.width, 3)
        self.assertEqual(grid.height, 2)
        self.assertTrue(grid.is_empty())
        self.assertEqual(grid.to_matrix(), ((False, False, False), (False, False)))

    def test_set_get_toggle_and_copy_are_independent(self):
        grid = PatternGrid(2, 2)
        grid.set(1, 0, True)
        self.assertTrue(grid.get(1, 0))
        self.assertFalse(grid.toggle(1, 0))
        self.assertFalse(grid.get(1, 0))
        clone = grid.copy()
        clone.set(0, 1, True)
        self.assertFalse(grid.get(0, 1))
        self.assertTrue(clone.get(0, 1))

    def test_out_of_range_coordinates_raise_value_error(self):
        grid = PatternGrid(2, 2)
        with self.assertRaises(ValueError):
            grid.set(2, 0, True)
        with self.assertRaises(ValueError):
            grid.get(-1, 0)

    def test_invalid_dimensions_and_cells_raise_value_error(self):
        with self.assertRaises(ValueError):
            PatternGrid(0, 2)
        with self.assertRaises(ValueError):
            PatternGrid(2, 2, [[False, False]])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.domain.test_models -v` with `PYTHONPATH=src`  
Expected: import failure because `PatternGrid` does not exist.

- [ ] **Step 3: Write minimal implementation**

Create `PatternGrid` as a small mutable domain object. Validate dimensions on construction and coordinate access. Copy must deep-copy all cells. No Qt imports in this module.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.domain.test_models -v` with `PYTHONPATH=src`  
Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .gitignore src/jingwei tests
git commit -m "feat: add pattern grid domain model"
```

### Task 2: 花本编译核心

**Files:**
- Create: `src/jingwei/domain/compiler.py`
- Create: `tests/domain/test_compiler.py`
- Modify: `src/jingwei/domain/__init__.py`

**Interfaces:**
- Consumes: `PatternGrid`
- Produces: `Card(card_id: str, lifted_warp: tuple[int, ...], first_source_row: int, occurrences: int)`
- Produces: `Pick(pick_index: int, source_row: int, card_id: str, lifted_warp: tuple[int, ...])`
- Produces: `CompileReport(original_pick_count: int, unique_card_count: int, compression_ratio: float, warnings: tuple[str, ...])`
- Produces: `WeavePlan(warp_count: int, weft_count: int, cards: tuple[Card, ...], picks: tuple[Pick, ...], report: CompileReport)`
- Produces: `compile_pattern(grid: PatternGrid) -> WeavePlan`

- [ ] **Step 1: Write the failing tests**

Test that:

```python
def test_identical_rows_share_one_card_and_keep_first_seen_order(self):
    grid = PatternGrid(3, 3, [
        [True, False, True],
        [False, True, False],
        [True, False, True],
    ])
    plan = compile_pattern(grid)
    self.assertEqual([p.card_id for p in plan.picks], ["C01", "C02", "C01"])
    self.assertEqual(plan.report.unique_card_count, 2)
    self.assertEqual(plan.report.original_pick_count, 3)
    self.assertAlmostEqual(plan.report.compression_ratio, 1 / 3)

def test_pick_lifted_warp_matches_true_columns(self):
    grid = PatternGrid(4, 1, [[False, True, True, False]])
    plan = compile_pattern(grid)
    self.assertEqual(plan.picks[0].lifted_warp, (1, 2))

def test_empty_pattern_compiles_to_empty_plan_with_warning(self):
    plan = compile_pattern(PatternGrid(3, 3))
    self.assertEqual(plan.picks, ())
    self.assertEqual(plan.cards, ())
    self.assertIn("纹样为空", plan.report.warnings[0])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.domain.test_compiler -v` with `PYTHONPATH=src`  
Expected: import failure because `compile_pattern` does not exist.

- [ ] **Step 3: Write minimal implementation**

For each row, build `lifted_warp` as the tuple of columns whose value is `True`. Use the tuple as the de-duplication key. Assign card IDs in first-seen order as `C01`, `C02`, etc. Empty rows still count as picks with a card containing an empty tuple. If the entire grid is empty, return no picks/cards and one warning. Do not add uneeded options.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.domain.test_compiler -v` with `PYTHONPATH=src`  
Expected: 3 tests PASS.

- [ ] **Step 5: Run full domain suite**

Run: `python -m unittest discover -s tests/domain -v` with `PYTHONPATH=src`  
Expected: all domain tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/jingwei/domain/compiler.py src/jingwei/domain/__init__.py tests/domain/test_compiler.py
git commit -m "feat: compile pattern rows into jacquard cards"
```

### Task 3: 织物矩阵生成

**Files:**
- Create: `src/jingwei/domain/weaver.py`
- Create: `tests/domain/test_weaver.py`
- Modify: `src/jingwei/domain/__init__.py`

**Interfaces:**
- Consumes: `WeavePlan`
- Produces: `WeaveMatrix(warp_count: int, weft_count: int, cells: tuple[tuple[bool, ...], ...])`
- Produces: `build_weave_matrix(plan: WeavePlan) -> WeaveMatrix`

- [ ] **Step 1: Write the failing tests**

```python
def test_weave_matrix_uses_each_pick_as_one_weft_row(self):
    grid = PatternGrid(3, 2, [
        [True, False, False],
        [False, True, False],
    ])
    plan = compile_pattern(grid)
    matrix = build_weave_matrix(plan)
    self.assertEqual(matrix.cells, ((True, False, False), (False, True, False)))

def test_malformed_plan_with_out_of_range_lift_is_rejected(self):
    pick = Pick(0, 0, "C01", (5,))
    plan = WeavePlan(3, 1, (), (pick,), CompileReport(1, 1, 0.0, ()))
    with self.assertRaises(ValueError):
        build_weave_matrix(plan)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.domain.test_weaver -v` with `PYTHONPATH=src`  
Expected: import failure because `build_weave_matrix` does not exist.

- [ ] **Step 3: Write minimal implementation**

For each `Pick`, create a row of `warp_count` booleans. Set `True` only at columns in `pick.lifted_warp`. Reject lifted indices outside `0..warp_count-1`. The result must have `weft_count` rows; if the pick count differs, raise `ValueError` so callers cannot silently export a partial result.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.domain.test_weaver -v` with `PYTHONPATH=src`  
Expected: 2 tests PASS.

- [ ] **Step 5: Run all non-GUI tests**

Run: `python -m unittest discover -s tests -v` with `PYTHONPATH=src`  
Expected: all tests PASS without importing PySide6.

- [ ] **Step 6: Commit**

```bash
git add src/jingwei/domain/weaver.py src/jingwei/domain/__init__.py tests/domain/test_weaver.py
git commit -m "feat: generate deterministic weave matrix"
```

### Task 4: PySide6环境与画布坐标换算

**Files:**
- Modify: `pyproject.toml`
- Create: `src/jingwei/ui/__init__.py`
- Create: `src/jingwei/ui/canvas_geometry.py`
- Create: `tests/ui/__init__.py`
- Create: `tests/ui/test_canvas_geometry.py`

**Interfaces:**
- Produces: `cell_from_point(x: float, y: float, width: int, height: int, columns: int, rows: int) -> tuple[int, int] | None`
- Produces: `cell_rect(column: int, row: int, width: int, height: int, columns: int, rows: int) -> tuple[float, float, float, float]`

- [ ] **Step 1: Create the virtual environment and install PySide6**

Run with approval:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install "PySide6==6.11.2"
```

Expected: package import succeeds.

- [ ] **Step 2: Write the failing geometry tests**

Test that a point at the top-left maps to `(0, 0)`, a point at the bottom-right inside the canvas maps to the final cell, and points exactly on the right/bottom edge or outside return `None`. Also test that `cell_rect` partitions the canvas without gaps.

- [ ] **Step 3: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m unittest tests.ui.test_canvas_geometry -v` with `PYTHONPATH=src`  
Expected: import failure because `cell_from_point` does not exist.

- [ ] **Step 4: Write minimal implementation**

Use integer arithmetic or `math.floor`. Clamp only after confirming the point is inside `0 <= x < width` and `0 <= y < height`. Reject non-positive canvas dimensions or cell counts.

- [ ] **Step 5: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m unittest tests.ui.test_canvas_geometry -v` with `PYTHONPATH=src`  
Expected: 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .gitignore src/jingwei/ui tests/ui
git commit -m "feat: add canvas geometry helpers"
```

### Task 5: 点阵画布组件

**Files:**
- Create: `src/jingwei/ui/pattern_canvas.py`
- Create: `tests/ui/test_pattern_canvas.py`

**Interfaces:**
- Consumes: `PatternGrid`, `cell_from_point`
- Produces: `PatternCanvas(QWidget)`
- Produces signal: `patternChanged = Signal()`
- Produces: `PatternCanvas.set_grid(grid: PatternGrid) -> None`
- Produces: `PatternCanvas.grid -> PatternGrid`
- Produces: `PatternCanvas.set_erase_mode(enabled: bool) -> None`

- [ ] **Step 1: Write the failing widget test**

Use `QT_QPA_PLATFORM=offscreen` and a `QApplication`. Assert that initial grid dimensions are correct, simulating a left press toggles the intended cell, right press or erase mode clears a cell, and `patternChanged` is emitted once per committed mouse move. Use `QTest.mouseClick` only for a real committed interaction.

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.ui.test_pattern_canvas -v
```

Expected: import failure because `PatternCanvas` does not exist.

- [ ] **Step 3: Write minimal implementation**

Subclass `QWidget`. Paint the grid with `QPainter`, draw a light background and dark square for `True` cells. Convert mouse positions with `cell_from_point`. Left mouse presses/moves paint `True`; right mouse presses/moves paint `False`; the erase-mode property makes left button paint `False`. Emit `patternChanged` only when a cell value actually changes. Keep the widget independent of `MainWindow`.

- [ ] **Step 4: Run test to verify it passes**

Run the same command as Step 2  
Expected: all canvas tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/jingwei/ui/pattern_canvas.py tests/ui/test_pattern_canvas.py
git commit -m "feat: add interactive point pattern canvas"
```

### Task 6: 主窗口与应用服务接线

**Files:**
- Create: `src/jingwei/application/__init__.py`
- Create: `src/jingwei/application/compile_service.py`
- Create: `src/jingwei/ui/main_window.py`
- Create: `src/jingwei/__main__.py`
- Create: `tests/test_smoke.py`
- Modify: `src/jingwei/__init__.py`

**Interfaces:**
- Produces: `CompileService.compile(grid: PatternGrid) -> WeavePlan`
- Produces: `MainWindow`
- Produces CLI: `python -m jingwei`
- Produces CLI: `python -m jingwei --smoke-test`

- [ ] **Step 1: Write the failing service and smoke tests**

Service test uses a simple grid and asserts `compile_service.compile(grid)` returns a `WeavePlan` with the expected number of picks. Smoke test starts `QApplication` with offscreen platform, constructs `MainWindow`, invokes a compile on an example grid, and asserts the report label contains the card count. The smoke test must not require manual interaction.

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_smoke -v
```

Expected: failure because `CompileService`, `MainWindow`, or entry point does not exist.

- [ ] **Step 3: Write minimal implementation**

`CompileService` delegates to `compile_pattern`; do not duplicate the algorithm. `MainWindow` contains a toolbar with “画笔”, “橡皮” and “编译花本”, a central `PatternCanvas`, and a right panel with `QLabel` compile summary. The compile action calls the service and displays original rows, unique cards, compression ratio, and warnings. If the grid changes after compile, mark the summary as “结果已过期”.

`__main__.py` creates `QApplication`, constructs `MainWindow`, and calls `app.exec()`. `--smoke-test` constructs the window, performs a deterministic example compile, processes events, and exits with code 0.

- [ ] **Step 4: Run smoke test to verify it passes**

Run:

```powershell
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_smoke -v
```

Expected: PASS.

- [ ] **Step 5: Run the application manually**

Run: `$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m jingwei`  
Expected: a desktop window opens, drawing works, and compile summary appears. This manual run is not a substitute for the automated smoke test.

- [ ] **Step 6: Commit**

```bash
git add src/jingwei/application src/jingwei/ui/main_window.py src/jingwei/__main__.py tests/test_smoke.py
git commit -m "feat: wire minimal drawing and compile workflow"
```

### Task 7: README、测试入口与AI记录

**Files:**
- Create: `README.md`
- Create: `tests/README.md`
- Modify: `docs/ai-log/2026-10-04.md`
- Modify: `docs/ai-log/ai-usage.jsonl`

**Interfaces:**
- Produces: setup, test, run, and project structure instructions.
- Produces: AI participation log entries for the implementation tasks.

- [ ] **Step 1: Write the documentation tests/checklist**

Add a checklist in `tests/README.md` covering:

- `PatternGrid` boundary rules;
- card reuse and ordering;
- weave matrix invariants;
- offscreen GUI smoke test;
- Windows-only manual check.

- [ ] **Step 2: Run the full test suite**

Run:

```powershell
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected: all tests PASS.

- [ ] **Step 3: Write README and AI log**

Document exact setup and run commands. Record which code and tests were AI-assisted, the user's requirements, and the human review status.

- [ ] **Step 4: Run the complete verification command one final time**

Run the same full test command as Step 2.  
Expected: all tests PASS, 0 failures.

- [ ] **Step 5: Commit**

```bash
git add README.md tests/README.md docs/ai-log
git commit -m "docs: document MVP setup and AI usage"
```

### Task 8: GitHub同步准备

**Files:**
- Modify: `.gitignore` if required.

**Interfaces:**
- Produces: a clean local Git history ready for GitHub push.
- Requires: a GitHub remote URL or authenticated `gh` CLI; do not invent one.

- [ ] **Step 1: Verify no secrets or generated environments are tracked**

Run: `git status --short` and `git ls-files`.  
Expected: `.venv/`, caches and build outputs are ignored; no credentials appear.

- [ ] **Step 2: Create or identify the remote**

If a remote already exists, verify it with `git remote -v`. If it does not, stop and ask the project owner for the exact GitHub repository URL or authentication method. Do not create a public repository without explicit approval.

- [ ] **Step 3: Push and verify**

Run: `git push -u origin <branch-name>` after approval.  
Expected: push succeeds and `git status` reports the branch is up to date.
