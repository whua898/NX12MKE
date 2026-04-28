## 1. 加工前准备：Machining Knowledge 规则库结构（建议）

```text
Machining Knowledge
└─ Factory_Plate_General (板类通用库)
├─ 01_Face_Milling (面加工库)
├─ 02_Pocket\_Slot (口袋与槽库)
├─ 03_Hole_Making (孔加工库)
│ ├─ 3.1_Spot (规则)
│ ├─ 3.2_Thread_Bottom (规则)
│ ├─ 3.3_Thread_Through (规则)
│ ├─ 3.4_Pin_Hole (规则)
│ ├─ 3.5_Large_Hole (规则)
└─ 04_Chamfer (倒角库 - 可选)
```

## 1.1 规则定义组件（必须明确）

每条规则请固定写清 6 个组件：

- Name（名称）
- OperationClass（工序类型）
- Priority（优先级）
- MWF（More Worked Feature）
- LWF（Less Worked Feature）
- ToolClass（刀具类型）

并且在 `Conditions/条件` 标签页中，**严格保留默认模板的所有注释与分段标题**，例如必须包含以下段落（不要删除/改名）：

```text
REM Application Criteria

$$ Rule rejected because condition FALSE

REM Tool Attributes

REM Less Worked Feature Attributes

REM Operation Attributes
```

## 1.2 NX12 Machining Knowledge Editor（MKE）语法边界 & 编写铁律（踩坑规范）

**一句话：** NX12 MKE 规则语言不是脚本语言，而是“声明式条件过滤器 +（有限的）工序属性赋值”。

### 1) 规则文件的固定结构（顺序不可改、标题不可删）

```text
REM Application Criteria
<只允许布尔条件，每行一个条件；多行自动 AND>

$$ Rule rejected because condition FALSE

REM Tool Attributes
<以筛选条件为主；你们环境测试通过：可对部分 tool.* 属性赋值>
<示例：tool.Diameter = 10.0>

REM Less Worked Feature Attributes
<可空>

REM Operation Attributes
<允许 oper.* 赋值>
```

### 2) Application Criteria：只能写条件（最常见报错来源）

- **允许：** 形如 `mwf.DIAMETER_1 >= 3.0` 的条件表达式；每行一个条件；多行自动 **AND**。
- **禁止：** `If/Then/Else/End If` 等脚本语句、以及任何赋值语句（含 `Rule_Validity = FALSE`）。
- **拒绝规则的方式：** 条件为 FALSE 即自动拒绝（无需、也不能写“reject”语句）。

### 3) Tool Attributes：可筛选刀具；你们环境也允许对部分 tool.* 赋值

- **允许（筛选）：** `tool.Diameter >= 9.5` / `tool.Diameter <= 10.5` 这类条件。
- **允许（赋值，已测试无语法错）：** `tool.Diameter = 10.0`。
- **注意：** `tool.SubType` 是否存在取决于你们模板/版本；没有该字段时会报错或被忽略。
- **刀具类别/类型：** 仍由 **OperationClass** 决定。

### 4) Operation Attributes：这里才允许 `=
（给 oper 赋值）`

- **允许：** `oper.name = "..."`、`oper.Feed_Cut = ...`（以你们模板实际支持字段为准）。
- **不建议：** 在这里写任何条件判断（一般不支持）。

## 2. 01_Face_Milling：面加工库（可直接落库）

**目标：** 建立板类零件的基准面加工与清根策略，覆盖粗加工、精加工和二次光面三层。

### 1) 推荐规则清单（板类通用）

```text
p{0.30}|>{}p{0.44}|>{}p{0.14}|}
Rule Name（规则名） & OpClass（建议） & Priority（建议）
1.1\_Face\_Top\_Rough & MillBase -> FaceMilling -> FACE\_MILLING & 1210
1.2\_Face\_Top\_Finish & MillBase -> FaceMilling -> FACE\_MILLING & 1220
1.3\_Face\_Bottom\_Finish & MillBase -> FaceMilling -> FACE\_MILLING & 1230
1.4\_Face\_ThinWall\_LightCut & MillBase -> FaceMilling -> FACE\_MILLING & 1240
```

**MWF/LWF/ToolClass（建议统一）：** `MWF=PLANAR_FACE`, `LWF=BLANK`, `ToolClass=FACE_MILL`。

### 2) 规则模板（以 1.1_Face_Top_Rough 为例）

```text
REM Application Criteria
mwf.AREA >= 400.0
mwf.AREA <= 200000.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 40.0
tool.Diameter <= 80.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "1.1_Face_Top_Rough"
```

**落地要点：**

- 1.1/1.2 使用同一 MWF 类型，靠 priority 与窗口区分粗精加工。
- 1.4 仅用于薄壁/薄板工况，避免对常规板类零件误命中。
- 面加工优先在库中预留“Top/Bottom”规则，减少人工翻面后重建工序。

### 3) 1.1\~1.4 完整 Conditions（可直接复制到 MKE）

```text
REM ----- 1.1_Face_Top_Rough -----
REM Application Criteria
mwf.AREA >= 400.0
mwf.AREA <= 200000.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 40.0
tool.Diameter <= 80.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "1.1_Face_Top_Rough"

REM ----- 1.2_Face_Top_Finish -----
REM Application Criteria
mwf.AREA >= 300.0
mwf.AREA <= 200000.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 32.0
tool.Diameter <= 63.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "1.2_Face_Top_Finish"

REM ----- 1.3_Face_Bottom_Finish -----
REM Application Criteria
mwf.AREA >= 300.0
mwf.AREA <= 200000.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 32.0
tool.Diameter <= 63.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "1.3_Face_Bottom_Finish"

REM ----- 1.4_Face_ThinWall_LightCut -----
REM Application Criteria
mwf.AREA >= 100.0
mwf.AREA <= 50000.0
mwf.THICKNESS <= 8.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 16.0
tool.Diameter <= 40.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "1.4_Face_ThinWall_LightCut"
```

**批量建规则参数表（Face）：**
```text
p{0.34}|>{}p{0.26}|>{}p{0.24}|}
Rule Name（规则名） & Application Criteria（示例） & Tool Attributes（tool.Diameter）
1.1\_Face\_Top\_Rough & AREA:[400,200000] & [40,80]
1.2\_Face\_Top\_Finish & AREA:[300,200000] & [32,63]
1.3\_Face\_Bottom\_Finish & AREA:[300,200000] & [32,63]
1.4\_Face\_ThinWall\_LightCut & AREA:[100,50000], THK8 & [16,40]
```

**4 条规则命名与优先级建议（可直接录库）：**
```text
Rule Name（规则名） & Priority（建议）
1.1\_Face\_Top\_Rough & 1210
1.2\_Face\_Top\_Finish & 1220
1.3\_Face\_Bottom\_Finish & 1230
1.4\_Face\_ThinWall\_LightCut & 1240
```

**录库检查清单（Face_Milling）：**

- Top Rough / Top Finish / Bottom Finish 命名必须与工序方向一致，避免镜像件误用。
- 1.4 仅用于薄板条件（如 `THICKNESS <= 8.0`），避免抢占常规面加工规则。
- 粗精加工建议成对存在，避免仅有粗加工导致基准面粗糙度不达标。

## 3. 02_Pocket_Slot：口袋与槽库（可直接落库）

**目标：** 对二维口袋、通槽、闭槽、窄长槽建立“粗-精-清角”分阶段规则，兼顾效率与可追溯性。

### 1) 推荐规则清单（板类通用）

```text
p{0.30}|>{}p{0.44}|>{}p{0.14}|}
Rule Name（规则名） & OperationClass（建议） & Priority（建议）
2.1\_Pocket\_Rough\_General & CavityMilling / CAVITY\_MILL & 2410
2.2\_Pocket\_Finish\_Wall & ProfileMilling / PROFILE & 2420
2.3\_Pocket\_Finish\_Floor & PlanarMilling / PLANAR\_MILL & 2430
2.4\_Slot\_Open\_Rough & SlotMilling / SLOT\_MILL & 2440
2.5\_Slot\_Closed\_Finish & SlotMilling / SLOT\_MILL & 2450
2.6\_Corner\_Rest\_Mill & RestMilling / REST\_MILL & 2460
```

### 2) 口袋规则模板（2.1_Pocket_Rough_General）

```text
REM Application Criteria
mwf.DEPTH >= 1.0
mwf.DEPTH <= 40.0
mwf.MIN_CORNER_RADIUS >= 2.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 8.0
tool.Diameter <= 20.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "2.1_Pocket_Rough_General"
```

### 3) 槽规则模板（2.4_Slot_Open_Rough）

```text
REM Application Criteria
mwf.WIDTH >= 6.0
mwf.WIDTH <= 24.0
mwf.DEPTH <= 20.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 5.0
tool.Diameter <= 16.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "2.4_Slot_Open_Rough"
```

**落地要点：**

- Pocket 与 Slot 建议拆库管理，但保持统一命名前缀 `2.x_`。
- 清角规则（2.6）优先级应高于精加工轮廓，避免残料未清导致边角超差。
- 对超窄槽（宽度 $<6$）建议单独建微径刀规则，避免在通用槽规则中误匹配。

### 4) 2.1\~2.6 完整 Conditions（可直接复制到 MKE）

```text
REM ----- 2.1_Pocket_Rough_General -----
REM Application Criteria
mwf.DEPTH >= 1.0
mwf.DEPTH <= 40.0
mwf.MIN_CORNER_RADIUS >= 2.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 8.0
tool.Diameter <= 20.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "2.1_Pocket_Rough_General"

REM ----- 2.2_Pocket_Finish_Wall -----
REM Application Criteria
mwf.DEPTH >= 1.0
mwf.DEPTH <= 40.0
mwf.WALL_ANGLE <= 2.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 6.0
tool.Diameter <= 16.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "2.2_Pocket_Finish_Wall"

REM ----- 2.3_Pocket_Finish_Floor -----
REM Application Criteria
mwf.DEPTH >= 1.0
mwf.DEPTH <= 40.0
mwf.BOTTOM_RADIUS <= 1.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 6.0
tool.Diameter <= 20.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "2.3_Pocket_Finish_Floor"

REM ----- 2.4_Slot_Open_Rough -----
REM Application Criteria
mwf.WIDTH >= 6.0
mwf.WIDTH <= 24.0
mwf.DEPTH <= 20.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 5.0
tool.Diameter <= 16.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "2.4_Slot_Open_Rough"

REM ----- 2.5_Slot_Closed_Finish -----
REM Application Criteria
mwf.WIDTH >= 4.0
mwf.WIDTH <= 16.0
mwf.DEPTH <= 20.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 3.0
tool.Diameter <= 10.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "2.5_Slot_Closed_Finish"

REM ----- 2.6_Corner_Rest_Mill -----
REM Application Criteria
mwf.MIN_CORNER_RADIUS <= 2.0
mwf.DEPTH <= 30.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 2.0
tool.Diameter <= 8.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "2.6_Corner_Rest_Mill"
```

**批量建规则参数表（Pocket_Slot）：**
```text
p{0.34}|>{}p{0.26}|>{}p{0.24}|}
规则名 & Application Criteria（示例） & Tool Attributes（tool.Diameter）
2.1\_Pocket\_Rough\_General & DEPTH:[1,40], R_{min}2 & [8,20]
2.2\_Pocket\_Finish\_Wall & DEPTH:[1,40], WALL\_ANGLE2 & [6,16]
2.3\_Pocket\_Finish\_Floor & DEPTH:[1,40], BOTTOM\_R1 & [6,20]
2.4\_Slot\_Open\_Rough & WIDTH:[6,24], DEPTH20 & [5,16]
2.5\_Slot\_Closed\_Finish & WIDTH:[4,16], DEPTH20 & [3,10]
2.6\_Corner\_Rest\_Mill & R_{min}2, DEPTH30 & [2,8]
```

**6 条规则命名与优先级建议（可直接录库）：**
```text
Rule Name（规则名） & Priority（建议）
2.1\_Pocket\_Rough\_General & 2410
2.2\_Pocket\_Finish\_Wall & 2420
2.3\_Pocket\_Finish\_Floor & 2430
2.4\_Slot\_Open\_Rough & 2440
2.5\_Slot\_Closed\_Finish & 2450
2.6\_Corner\_Rest\_Mill & 2460
```

**录库检查清单（Pocket_Slot）：**

- 口袋与槽规则窗口应互斥（尤其按 `WIDTH` 条件），避免同一特征双命中。
- 2.6 清角规则应保留最高优先级，确保角部残料不会遗留到后续工序。
- 闭槽规则（2.5）建议绑定更小刀径窗口，避免大刀误匹配导致过切。

# 4. 03_Hole_Making：板类零件基于特征的孔加工

使用操作类型模板 `hole_making`，可以创建以下“手动的、基于特征（feature-based）”的孔加工操作：

- 定位钻（Spot Drilling）
- 钻孔（Drilling）
- 沉头（Countersinking）
- 攻丝（Tapping）
- 孔铣（Hole Milling）
- 凸台铣（Boss Milling）
- 螺纹铣（Thread Milling）
- 凸台螺纹铣（Boss Thread Milling）

待加工板类零件可以包含：特征、带属性的几何实体、带属性的特征，或以上三者的任意组合。

## 孔径归一化（示例）

**螺纹底孔（钻）归一化：**
```text
p{0.30}|>{}p{0.28}|>{}p{0.28}|}
螺纹代号 & 钻头直径 / mm & 归一范围 / mm
M4 & 3.4 & [3.10,\ 3.50]
M5 & 4.3 & [4.10,\ 4.50]
M6 & 5.2 & [5.10,\ 5.50]
M8 & 6.9 & [6.50,\ 6.98]
M10 & 8.7 & [8.10,\ 8.98]
M12 & 10.5 & [10.10,\ 10.80]
M16 & 14.3 & [13.50,\ 14.50]
M20 & 17.8 & [17.10,\ 17.98]
```

**螺纹过孔（钻）：** 9、11、13、17、21（mm）。

**销孔（钻+铰，铰前留量 $+0.3$）：**
```text
p{0.30}|>{}p{0.28}|>{}p{0.28}|}
销孔直径 D / mm & 预钻目标 D-0.3 / mm（抓取窗口） & 铰孔 D / mm（抓取窗口）
4 & [3.68,\ 3.72] & [3.98,\ 4.02]
5 & [4.68,\ 4.72] & [4.98,\ 5.02]
6 & [5.68,\ 5.72] & [5.98,\ 6.02]
8 & [7.68,\ 7.72] & [7.98,\ 8.02]
10 & [9.68,\ 9.72] & [9.98,\ 10.02]
12 & [11.68,\ 11.72] & [11.98,\ 12.02]
16 & [15.68,\ 15.72] & [15.98,\ 16.02]
20 & [19.68,\ 19.72] & [19.98,\ 20.02]
```

## 4.0 03_Hole_Making 规则：2.1_Spot_Drilling_All（示例）

**提示：** 你们环境已验证：**Application Criteria 不支持 If/Then**，建议用“每行一个布尔条件（多行默认 AND）”来写。

```text
REM ---------------------------------------------------------
REM Rule: spot drilling all holes (single operation)
REM Range: D3.0 - D22.0
REM Strategy: force one spot drill (example: D10)
REM ---------------------------------------------------------

REM Application Criteria
mwf.DIAMETER_1 >= 3.0
mwf.DIAMETER_1 <= 22.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter = 10.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "2.1_Spot_D10"
```

14

## 4.1 03_Hole_Making：规则清单（按你的窗口表落地）

**说明：** 下述代码块仅在默认模板对应的段落中“填肉”，不删除任何既有注释。

### 3.1_Spot（定位钻，全孔单一程序）

**定义：**

- Name：`3.1_Spot`
- OperationClass：`DrillBase -> HoleMaking -> SPOT_DRILLING`
- Priority：`1`
- MWF：`HOLE`（按你们环境的孔特征类）
- LWF：`BLANK`
- ToolClass：`SPOT_DRILL`

**Conditions（按 NX12 默认模板“只填肉、不删注释”的写法）：**
```text
REM Application Criteria

mwf.DIAMETER_1 >= 3.0
mwf.DIAMETER_1 <= 22.0

$$ Rule rejected because condition FALSE

REM Tool Attributes

tool.Diameter >= 9.5
tool.Diameter <= 10.5

REM Less Worked Feature Attributes

REM Operation Attributes

oper.name = "3.1_Spot"
```

### 3.2_Thread_Bottom（螺纹底孔：只钻不攻，8 条规则）

**OperationClass：** `DrillBase -> HoleMaking -> DRILLING`

**MWF/LWF/ToolClass：** `MWF=HOLE`, `LWF=BLANK`, `ToolClass=TWIST_DRILL`

**规则列表（直径窗口 + 强制刀径）：**

- `3.2_Thread_Bottom_D3p4`：$[3.10,\ 3.50]$，刀具 $ 3.4$
- `3.2_Thread_Bottom_D4p3`：$[4.10,\ 4.50]$，刀具 $ 4.3$
- `3.2_Thread_Bottom_D5p2`：$[5.10,\ 5.50]$，刀具 $ 5.2$
- `3.2_Thread_Bottom_D6p9`：$[6.50,\ 6.98]$，刀具 $ 6.9$
- `3.2_Thread_Bottom_D8p7`：$[8.10,\ 8.98]$，刀具 $ 8.7$
- `3.2_Thread_Bottom_D10p5`：$[10.10,\ 10.80]$，刀具 $ 10.5$
- `3.2_Thread_Bottom_D14p3`：$[13.50,\ 14.50]$，刀具 $ 14.3$
- `3.2_Thread_Bottom_D17p8`：$[17.10,\ 17.98]$，刀具 $ 17.8$

**Conditions 模板（以 D3p4 为例；其余规则只改“窗口 + 刀具直径筛选”）：**
```text
REM Application Criteria

mwf.DIAMETER_1 >= 3.10
mwf.DIAMETER_1 <= 3.50

$$ Rule rejected because condition FALSE

REM Tool Attributes

tool.Diameter >= 3.35
tool.Diameter <= 3.45

REM Less Worked Feature Attributes

REM Operation Attributes

oper.name = "3.2_Thread_Bottom_D3p4"
```

**8 条规则命名与优先级建议（可直接录库）：**
```text
Rule Name（规则名） & Priority（建议）
3.2\_Thread\_Bottom\_D3p4 & 2210
3.2\_Thread\_Bottom\_D4p3 & 2220
3.2\_Thread\_Bottom\_D5p2 & 2230
3.2\_Thread\_Bottom\_D6p9 & 2240
3.2\_Thread\_Bottom\_D8p7 & 2250
3.2\_Thread\_Bottom\_D10p5 & 2260
3.2\_Thread\_Bottom\_D14p3 & 2270
3.2\_Thread\_Bottom\_D17p8 & 2280
```

**录库检查清单（Thread_Bottom）：**

- 规则名、窗口和刀具直径一一对应，避免“名称是 D8p7 但窗口/刀具仍是旧值”。
- 8 条规则都应属于同一 OperationClass（`DRILLING`）与 ToolClass（`TWIST_DRILL`）。
- Priority 连续递增，便于排查冲突时快速定位候选规则。
- 每条规则保留默认模板分段标题，不删 `REM ...` 与拒绝注释行。

### 3.3_Thread_Through（螺纹过孔：5 条规则，先用精确窗口）

**OperationClass：** `DrillBase -> HoleMaking -> DRILLING`

**规则列表（精确抓取窗口）：**

- `3.3_Thread_Through_D9`：$[8.98,\ 9.02]$，刀具 $ 9$
- `3.3_Thread_Through_D11`：$[10.98,\ 11.02]$，刀具 $ 11$
- `3.3_Thread_Through_D13`：$[12.98,\ 13.02]$，刀具 $ 13$
- `3.3_Thread_Through_D17`：$[16.98,\ 17.02]$，刀具 $ 17$
- `3.3_Thread_Through_D21`：$[20.98,\ 21.02]$，刀具 $ 21$

**完整 Conditions（5 条可直接复制到 MKE）：**
```text
REM ----- 3.3_Thread_Through_D9 -----
REM Application Criteria
mwf.DIAMETER_1 >= 8.98
mwf.DIAMETER_1 <= 9.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 8.95
tool.Diameter <= 9.05

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.3_Thread_Through_D9"

REM ----- 3.3_Thread_Through_D11 -----
REM Application Criteria
mwf.DIAMETER_1 >= 10.98
mwf.DIAMETER_1 <= 11.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 10.95
tool.Diameter <= 11.05

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.3_Thread_Through_D11"

REM ----- 3.3_Thread_Through_D13 -----
REM Application Criteria
mwf.DIAMETER_1 >= 12.98
mwf.DIAMETER_1 <= 13.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 12.95
tool.Diameter <= 13.05

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.3_Thread_Through_D13"

REM ----- 3.3_Thread_Through_D17 -----
REM Application Criteria
mwf.DIAMETER_1 >= 16.98
mwf.DIAMETER_1 <= 17.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 16.95
tool.Diameter <= 17.05

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.3_Thread_Through_D17"

REM ----- 3.3_Thread_Through_D21 -----
REM Application Criteria
mwf.DIAMETER_1 >= 20.98
mwf.DIAMETER_1 <= 21.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 20.95
tool.Diameter <= 21.05

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.3_Thread_Through_D21"
```

**批量建规则参数表（5 条）：**
```text
p{0.36}|>{}p{0.24}|>{}p{0.24}|}
规则名 & Application Criteria（mwf.DIAMETER\_1） & Tool Attributes（tool.Diameter）
3.3\_Thread\_Through\_D9 & [8.98,\ 9.02] & [8.95,\ 9.05]
3.3\_Thread\_Through\_D11 & [10.98,\ 11.02] & [10.95,\ 11.05]
3.3\_Thread\_Through\_D13 & [12.98,\ 13.02] & [12.95,\ 13.05]
3.3\_Thread\_Through\_D17 & [16.98,\ 17.02] & [16.95,\ 17.05]
3.3\_Thread\_Through\_D21 & [20.98,\ 21.02] & [20.95,\ 21.05]
```

**5 条规则命名与优先级建议（可直接录库）：**
```text
Rule Name（规则名） & Priority（建议）
3.3\_Thread\_Through\_D9 & 2310
3.3\_Thread\_Through\_D11 & 2320
3.3\_Thread\_Through\_D13 & 2330
3.3\_Thread\_Through\_D17 & 2340
3.3\_Thread\_Through\_D21 & 2350
```

**录库检查清单（Thread_Through）：**

- 规则窗口保持窄窗，避免与 Thread Bottom 窗口重叠导致双命中。
- Tool Attributes 推荐保持目标直径附近窄窗（如 $ 0.05$），便于稳定匹配刀具。
- 5 条规则统一 OperationClass（`DRILLING`）与 ToolClass（钻削类）。
- Priority 连续递增，便于冲突排查与版本对比。

### 3.4_Pin_Hole（销孔：钻+铰，留量 +0.3，每孔径两条）

**钻（预钻）OperationClass：**
`DrillBase -> HoleMaking -> DRILLING`。

**铰 OperationClass：**
`DrillBase -> HoleMaking -> REAMING`（按你们系统的铰孔策略类名）。

**抓取窗口：**

- 预钻目标 $D-0.3$：$[3.68,\ 3.72]$、$[4.68,\ 4.72]$、$[5.68,\ 5.72]$、$[7.68,\ 7.72]$、$[9.68,\ 9.72]$、$[11.68,\ 11.72]$、$[15.68,\ 15.72]$、$[19.68,\ 19.72]$。
- 铰孔 $D$：$[3.98,\ 4.02]$、$[4.98,\ 5.02]$、$[5.98,\ 6.02]$、$[7.98,\ 8.02]$、$[9.98,\ 10.02]$、$[11.98,\ 12.02]$、$[15.98,\ 16.02]$、$[19.98,\ 20.02]$。

**完整 Conditions（16 条可直接复制到 MKE）：**
```text
REM ----- 3.4_Pin_Pre_D4 -----
REM Application Criteria
mwf.DIAMETER_1 >= 3.68
mwf.DIAMETER_1 <= 3.72

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 3.95
tool.Diameter <= 4.05

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Pre_D4"

REM ----- 3.4_Pin_Ream_D4 -----
REM Application Criteria
mwf.DIAMETER_1 >= 3.98
mwf.DIAMETER_1 <= 4.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 3.98
tool.Diameter <= 4.02

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Ream_D4"

REM ----- 3.4_Pin_Pre_D5 -----
REM Application Criteria
mwf.DIAMETER_1 >= 4.68
mwf.DIAMETER_1 <= 4.72

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 4.65
tool.Diameter <= 4.75

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Pre_D5"

REM ----- 3.4_Pin_Ream_D5 -----
REM Application Criteria
mwf.DIAMETER_1 >= 4.98
mwf.DIAMETER_1 <= 5.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 4.98
tool.Diameter <= 5.02

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Ream_D5"

REM ----- 3.4_Pin_Pre_D6 -----
REM Application Criteria
mwf.DIAMETER_1 >= 5.68
mwf.DIAMETER_1 <= 5.72

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 5.65
tool.Diameter <= 5.75

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Pre_D6"

REM ----- 3.4_Pin_Ream_D6 -----
REM Application Criteria
mwf.DIAMETER_1 >= 5.98
mwf.DIAMETER_1 <= 6.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 5.98
tool.Diameter <= 6.02

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Ream_D6"

REM ----- 3.4_Pin_Pre_D8 -----
REM Application Criteria
mwf.DIAMETER_1 >= 7.68
mwf.DIAMETER_1 <= 7.72

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 7.65
tool.Diameter <= 7.75

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Pre_D8"

REM ----- 3.4_Pin_Ream_D8 -----
REM Application Criteria
mwf.DIAMETER_1 >= 7.98
mwf.DIAMETER_1 <= 8.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 7.98
tool.Diameter <= 8.02

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Ream_D8"

REM ----- 3.4_Pin_Pre_D10 -----
REM Application Criteria
mwf.DIAMETER_1 >= 9.68
mwf.DIAMETER_1 <= 9.72

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 9.65
tool.Diameter <= 9.75

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Pre_D10"

REM ----- 3.4_Pin_Ream_D10 -----
REM Application Criteria
mwf.DIAMETER_1 >= 9.98
mwf.DIAMETER_1 <= 10.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 9.98
tool.Diameter <= 10.02

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Ream_D10"

REM ----- 3.4_Pin_Pre_D12 -----
REM Application Criteria
mwf.DIAMETER_1 >= 11.68
mwf.DIAMETER_1 <= 11.72

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 11.65
tool.Diameter <= 11.75

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Pre_D12"

REM ----- 3.4_Pin_Ream_D12 -----
REM Application Criteria
mwf.DIAMETER_1 >= 11.98
mwf.DIAMETER_1 <= 12.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 11.98
tool.Diameter <= 12.02

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Ream_D12"

REM ----- 3.4_Pin_Pre_D16 -----
REM Application Criteria
mwf.DIAMETER_1 >= 15.68
mwf.DIAMETER_1 <= 15.72

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 15.65
tool.Diameter <= 15.75

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Pre_D16"

REM ----- 3.4_Pin_Ream_D16 -----
REM Application Criteria
mwf.DIAMETER_1 >= 15.98
mwf.DIAMETER_1 <= 16.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 15.98
tool.Diameter <= 16.02

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Ream_D16"

REM ----- 3.4_Pin_Pre_D20 -----
REM Application Criteria
mwf.DIAMETER_1 >= 19.68
mwf.DIAMETER_1 <= 19.72

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 19.65
tool.Diameter <= 19.75

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Pre_D20"

REM ----- 3.4_Pin_Ream_D20 -----
REM Application Criteria
mwf.DIAMETER_1 >= 19.98
mwf.DIAMETER_1 <= 20.02

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 19.98
tool.Diameter <= 20.02

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "3.4_Pin_Ream_D20"
```

**批量建规则参数表（销孔 D=4/5/6/8/10/12/16/20）：**
```text
p{0.20}|>{}p{0.35}|>{}p{0.35}|}
成品孔径 D / mm & 预钻窗口（D-0.3） & 铰孔窗口（D）
4 & [3.68,\ 3.72] & [3.98,\ 4.02]
5 & [4.68,\ 4.72] & [4.98,\ 5.02]
6 & [5.68,\ 5.72] & [5.98,\ 6.02]
8 & [7.68,\ 7.72] & [7.98,\ 8.02]
10 & [9.68,\ 9.72] & [9.98,\ 10.02]
12 & [11.68,\ 11.72] & [11.98,\ 12.02]
16 & [15.68,\ 15.72] & [15.98,\ 16.02]
20 & [19.68,\ 19.72] & [19.98,\ 20.02]
```

**16 条规则命名与优先级建议（可直接录库）：**
```text
Rule Name（规则名） & Priority（建议）
3.4\_Pin\_Pre\_D4 & 2110
3.4\_Pin\_Ream\_D4 & 3110
3.4\_Pin\_Pre\_D5 & 2120
3.4\_Pin\_Ream\_D5 & 3120
3.4\_Pin\_Pre\_D6 & 2130
3.4\_Pin\_Ream\_D6 & 3130
3.4\_Pin\_Pre\_D8 & 2140
3.4\_Pin\_Ream\_D8 & 3140
3.4\_Pin\_Pre\_D10 & 2150
3.4\_Pin\_Ream\_D10 & 3150
3.4\_Pin\_Pre\_D12 & 2160
3.4\_Pin\_Ream\_D12 & 3160
3.4\_Pin\_Pre\_D16 & 2170
3.4\_Pin\_Ream\_D16 & 3170
3.4\_Pin\_Pre\_D20 & 2180
3.4\_Pin\_Ream\_D20 & 3180
```

**录库检查清单（Pin Hole）：**

- Pre 与 Ream 必须同孔径成对存在，命名仅后缀不同（`Pre`/`Ream`）。
- Ream 的优先级必须高于同孔径 Pre（确保工序链路可被正确接续）。
- 每条规则保留默认模板分段标题，不删除 `REM ...` 与拒绝注释行。
- ToolClass 与 OperationClass 对齐：Pre 用钻削类、Ream 用铰孔类。

### 3.5_Large_Hole（大孔/异形孔）

**说明：** 圆孔 $D>21$ 可走孔铣（Hole Milling）策略；方孔/条孔建议走型腔/轮廓类铣削策略（不适合用钻削规则去覆盖）。

## 统一优先级总表（3.1\~3.5）

**建议分带：** Spot=1000 段；Thread Bottom=2200 段；Thread Through=2300 段；Pin Pre=2100 段；Pin Ream=3100 段；兜底人工检查规则使用最低优先级。

```text
模块 & 规则数量 & Priority 建议区间
3.1\_Spot & 1 & 1100
3.2\_Thread\_Bottom & 8 & 2210\~2280
3.3\_Thread\_Through & 5 & 2310\~2350
3.4\_Pin\_Pre & 8 & 2110\~2180
3.4\_Pin\_Ream & 8 & 3110\~3180
3.5\_Large\_Hole & 1\~N & 3200+
Fallback\_ManualCheck & 1 & 100
```

**落地规则：**

- 同一特征类型下，优先级越高越先尝试；命中则不再尝试低优先级同类规则。
- Ream 优先级应高于对应 Pre，确保序列条件满足时优先生成精加工路径。
- Fallback 必须最低，避免吞掉本应由专用规则处理的特征。

## 5. 04_Chamfer：倒角库（可选但建议标准化）

**目标：** 对孔口倒角与外轮廓倒角建立统一规则，减少人工补刀与漏倒角。

### 1) 推荐规则清单（板类通用）

```text
Rule Name（规则名） & OperationClass（建议） & Priority（建议）
4.1\_Hole\_Chamfer\_C0p5 & ChamferMilling / CHAMFER\_MILL & 3310
4.2\_Hole\_Chamfer\_C1p0 & ChamferMilling / CHAMFER\_MILL & 3320
4.3\_Outer\_Chamfer\_General & ChamferMilling / CHAMFER\_MILL & 3330
4.4\_Deburr\_Light\_Pass & ChamferMilling / CHAMFER\_MILL & 3340
```

### 2) 规则模板（4.1_Hole_Chamfer_C0p5）

```text
REM Application Criteria
mwf.DIAMETER_1 >= 3.0
mwf.DIAMETER_1 <= 20.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 5.0
tool.Diameter <= 16.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "4.1_Hole_Chamfer_C0p5"
```

**落地要点：**

- 倒角建议在孔加工与轮廓精加工之后执行，避免后续工序二次破坏倒角面。
- 若现场主要目的是去毛刺，优先使用 `4.4_Deburr_Light_Pass` 降低切削负载。
- 对关键装配孔建议保持倒角规则与孔径窗口绑定，避免过大倒角影响配合。

### 3) 4.1\~4.4 完整 Conditions（可直接复制到 MKE）

```text
REM ----- 4.1_Hole_Chamfer_C0p5 -----
REM Application Criteria
mwf.DIAMETER_1 >= 3.0
mwf.DIAMETER_1 <= 20.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 5.0
tool.Diameter <= 16.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "4.1_Hole_Chamfer_C0p5"

REM ----- 4.2_Hole_Chamfer_C1p0 -----
REM Application Criteria
mwf.DIAMETER_1 >= 6.0
mwf.DIAMETER_1 <= 30.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 8.0
tool.Diameter <= 20.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "4.2_Hole_Chamfer_C1p0"

REM ----- 4.3_Outer_Chamfer_General -----
REM Application Criteria
mwf.EDGE_LENGTH >= 20.0
mwf.EDGE_LENGTH <= 5000.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 8.0
tool.Diameter <= 25.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "4.3_Outer_Chamfer_General"

REM ----- 4.4_Deburr_Light_Pass -----
REM Application Criteria
mwf.EDGE_LENGTH >= 5.0
mwf.EDGE_LENGTH <= 8000.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
tool.Diameter >= 6.0
tool.Diameter <= 20.0

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "4.4_Deburr_Light_Pass"
```

**批量建规则参数表（Chamfer）：**
```text
p{0.36}|>{}p{0.24}|>{}p{0.24}|}
Rule Name（规则名） & Application Criteria（示例） & Tool Attributes（tool.Diameter）
4.1\_Hole\_Chamfer\_C0p5 & D:[3,20] & [5,16]
4.2\_Hole\_Chamfer\_C1p0 & D:[6,30] & [8,20]
4.3\_Outer\_Chamfer\_General & EDGE:[20,5000] & [8,25]
4.4\_Deburr\_Light\_Pass & EDGE:[5,8000] & [6,20]
```

**4 条规则命名与优先级建议（可直接录库）：**
```text
Rule Name（规则名） & Priority（建议）
4.1\_Hole\_Chamfer\_C0p5 & 3310
4.2\_Hole\_Chamfer\_C1p0 & 3320
4.3\_Outer\_Chamfer\_General & 3330
4.4\_Deburr\_Light\_Pass & 3340
```

**录库检查清单（Chamfer）：**

- 孔倒角规则（4.1/4.2）应按孔径窗口明确分流，避免同孔同时触发两条倒角规则。
- Deburr 规则（4.4）优先级应低于功能性倒角（4.1\~4.3）。
- 倒角规则必须放在孔加工/轮廓精加工之后执行，防止后续切削破坏倒角边。

## 6. 板类标准工艺卡（工序号+刀具+质量控制点）

**适用范围：** 板类零件常规 2.5 轴加工（面、口袋/槽、孔系、倒角）。

```text
{1.12}
p{0.26}|>{}p{0.24}|>{}p{0.30}|}
**工序号** & **工序内容** & **刀具建议** & **质量控制点**
OP10 & 上料找正、装夹校准 & 百分表/寻边器（工装） & 基准边与坐标系一致；装夹不翘曲，首件找正记录可追溯。
OP20 & 基准面粗铣（Face Rough） & 面铣刀 D40 D80 & 去除毛坯余量均匀；保留精加工余量；无明显振纹。
OP30 & 基准面精铣（Face Finish） & 面铣刀 D32 D63 & 平面度、厚度基准达标；与后续孔系基准关系稳定。
OP40 & 口袋/槽粗加工（Pocket/Slot Rough） & 立铣刀 D6 D20 & 不残留大块余料；拐角不过切；刀具负载稳定无异常报警。
OP50 & 口袋/槽精加工+清角（Finish/Rest） & 精铣刀+小径清角刀 D2 D10 & 轮廓尺寸与角部残料受控；侧壁与底面粗糙度满足图纸要求。
OP60 & 孔系定位钻（Spot） & 定位钻（Spot Drill） & 孔位不漂移；后续钻孔入口无偏摆。
OP70 & 钻孔/扩孔（Thread Bottom/Through） & 麻花钻（Twist Drill） & 孔径窗口命中正确；底孔与通孔规则互斥；无漏孔。
OP80 & 铰孔/攻丝（Ream/Tap） & 铰刀/丝锥 & Pin 孔链路完整（Pre+Ream）；螺纹有效圈与通止规合格。
OP90 & 倒角去毛刺（Chamfer/Deburr） & 倒角刀 D5 D25 & 倒角尺寸一致、无毛刺翻边；倒角顺序晚于关键尺寸精加工。
OP100 & 终检与归档 & 检具/CMM（按图） & 关键尺寸、形位、公差、外观全检/抽检合格；版本、回归、签核记录齐全。
{1.0}
```

**执行要求：**

- 工序顺序遵循“先基准、后特征；先粗、后精；先主体、后倒角”。
- 若出现双命中或无刀具匹配，先启用 `Fallback_ManualCheck` 保产线，再闭环规则。
- 每次换版必须同步更新工艺卡版本、规则版本与发布签核页。

## 7. 1页速查讲义（培训/现场打印版）

**适用对象：** 新上手工程师、现场工艺员、规则库维护人员。

### A) 建库四步

- 建父库：`Factory_Plate_General`
- 建子库：`01/02/03/04`
- 录规则：先 01，再 02，再 03，最后 04
- 加兜底：`Fallback_ManualCheck`（最低优先级）

### B) 每条规则必填 6 项

```text
字段 & 填写要求
Name & 与模块前缀一致（如 3.2\_Thread\_Bottom\_D8p7）
OperationClass & 与工艺一致（Drill/Mill/Chamfer）
Priority & 同模块连续、特化规则更高
MWF & 特征类型准确（HOLE/PLANAR\_FACE/...）
LWF & 通常 BLANK 或上游规则输出
ToolClass & 与刀具库类型严格一致
```

### C) Conditions 三条铁律

- **Application Criteria** 只能写布尔条件（每行一条，多行 AND）。
- **Tool Attributes** 先窄窗筛选，缺刀时再放宽到业务允许范围。
- **Operation Attributes** 只放必要赋值（如 `oper.name`），复杂参数放 Add-On（附加工艺模板）。

### D) 优先级口诀（避免冲突）

```text
窄窗优先 > 宽窗兜底；特化优先 > 通用规则；人工兜底永远最低。
```

### E) 上线前最小回归（必跑）

```text
测试项 & 最低通过要求
Face & 顶/底面粗精顺序正确
Pocket\_Slot & 不双命中，清角可触发
Hole & 底孔/过孔互斥，Pin 具备 Pre+Ream
Chamfer & 倒角在精加工后执行
```

### F) 失败时先做什么

- 保产线：启用 `ManualCheck` 占位，不让特征漏加工。
- 查语法与字段：确认模板分段、字段名可用。
- 查窗口与优先级：先放宽命中，再回收精度。
- 留痕：更新 Change Log，记录 Owner/Date/Delta。

## 8. 跨模块统一命名、优先级与发布流程（建议直接采用）

### 1) 全库优先级分带（Factory_Plate_General）

```text
模块 & Priority 建议区间
01\_Face\_Milling & 1200\~1299
02\_Pocket\_Slot & 2400\~2499
03\_Hole\_Making & 2100\~3399（详见 3.1\~3.5）
04\_Chamfer & 3300\~3399
Fallback\_ManualCheck & 0100
```

### 2) 统一命名模板（建议）

```text
`模块\_工艺\_特征\_窗口\_刀具\_R版本`
```

**示例：**

- `FM_Face_Top_A400-200k_D63_R01`
- `PS_Pocket_Rough_Dep1-40_D12_R01`
- `CF_HoleChamfer_D3-20_C0p5_R01`

### 3) 发布与回归最小流程（每次改库必跑）

- 在验证库新增/修改规则，版本号递增（`R03 -> R04`）。
- 执行最小回归样件（面、口袋、槽、孔、倒角各至少 1 组）。
- 检查是否出现“多规则重复命中”与“无刀具可用”两类关键故障。
- 通过后再同步生产库，并记录变更摘要与责任人。

## 8.1 基于 MachiningKnowledgeEditor.pdf 的补充约束（NX12 手册对齐）

### 1) Priority 的官方语义（必须统一）

根据培训手册附录 E（Tips and Tricks）：**priority 数值越大，规则越先尝试**。但该优先级只在**同一 More Worked Feature 类型**的竞争规则间有意义。

**落地建议：**

- 对同一孔特征类型（如 HOLE）建立统一优先级带，避免跨团队随意取值。
- 成本更低的工艺给更高优先级，但必须配套严格条件，防止误命中。
- 不同特征类型（如 HOLE vs POCKET）之间不必强行对齐 priority。

### 2) 用 MACHINING_RULE 串联工序顺序（钻 $$ 攻丝/铰孔）

手册示例强调可通过 `mwf.MACHINING_RULE` / `lwf.MACHINING_RULE` 约束工序链路，用于防止“跳工序”或“串错工序”。

**模板（思路）：**
```text
REM Drilling rule (producer)
mwf.MACHINING_RULE = "TWIST_DRILL"

REM Tapping/Reaming rule (consumer)
lwf.MACHINING_RULE = "TWIST_DRILL"
```

**建议：** 销孔的铰孔规则可要求`lwf.MACHINING_RULE = "TWIST_DRILL"`，确保先有预钻再铰孔。

### 3) Tool Attributes 的选择逻辑（避免误解）

手册在 Conditions 章节说明：规则可通过 Tool Attributes 进行刀具筛选；若某刀具不满足，NX 会继续尝试下一条规则。对铣削类场景，常不必设置严格下限；对钻削类，通常应保留下限以避免错配。

**落地建议：**

- 钻削规则保留上下限，且窗口略宽于目标值（例如 $ 0.05$）。
- 铣削规则优先保证上限（避免过切），下限仅在必要时添加。
- 在 Customization 中确保已正确设置 Cutter Diameter / Cutter Length 映射，否则筛选结果会异常。

### 4) Operation Attributes 的放置位置（减少副作用）

手册建议：复杂操作参数尽量放到 Add-On（附加工艺模板）中，而不是 Conditions 中连续重算。你当前文档采用 `oper.name = "..."` 的轻量赋值是可行的；若后续加切削参数（进给、转速、切深），建议迁移至 Add-On（附加工艺模板）。

## 8.2 规则冲突与回归测试（生产化增强）

### A) 规则冲突与优先级设计

**推荐分层优先级：**

- `P1000`：基础识别（Spot、通用钻）
- `P2000`：工艺分流（螺纹底孔/过孔/销孔）
- `P3000`：高精度与特化（铰孔、大孔孔铣、特殊刀具）

**冲突处理原则：**

- 同一特征若命中多条规则，优先执行 **高优先级** + **窄窗口** 的规则。
- 底孔与过孔必须显式互斥，避免同一孔同时生成两条钻孔工序。
- 销孔“预钻/铰孔”使用成对命名（同一 ID），便于追踪缺失工序。

**互斥条件示例（思路）：**
```text
REM Thread bottom rule: only in bottom-hole window
mwf.DIAMETER_1 >= 8.10
mwf.DIAMETER_1 <= 8.98

REM Thread through rule: only in through-hole exact window
mwf.DIAMETER_1 >= 8.98
mwf.DIAMETER_1 <= 9.02
```

### B) 命中日志与可追溯命名

**命名规范建议：**
```text
`模块\_工艺\_孔型\_直径窗\_刀径\_R版本`
```

**示例：**

- `HM_Drill_ThreadBottom_D8p10-8p98_T8p7_R01`
- `HM_Ream_Pin_D9p98-10p02_T10_R01`

**Operation Attributes 建议：**
```text
REM Operation Attributes
oper.name = "HM_Drill_ThreadBottom_D8p10-8p98_T8p7_R01"
```

**目的：** 现场只看工序名即可反查“规则来源 + 直径窗口 + 刀具选择”。

### C) 回归测试样件与通过标准

**建议最小样件集（每次改规则后必跑）：**

- 螺纹底孔：M4/M6/M10 各 1 个。
- 螺纹过孔：$ 9/11/13$ 各 1 个。
- 销孔：$ 6/10/16$ 各 1 组（预钻 + 铰孔）。
- 大孔：$ 24$（验证走 Hole Milling，不走 Drilling）。
- 边界孔：如 $8.98$、$9.02$（验证窗口边界命中稳定性）。

**通过标准（建议量化）：**

- 每个测试孔仅生成预期工序；不得出现多余工序。
- 关键工序命名必须包含规则 ID（便于审计）。
- 刀具直径与窗口期望一致；无“无刀具可用”报错。

### D) 无匹配刀具的兜底策略

**建议采用“宽窗筛选 + 精窗命名”双层策略：**

- 第 1 层（刀具筛选）：例如 `tool.Diameter >= 8.6` 且 `<= 8.8`。
- 第 2 层（特征识别）：仍用精确或业务认可的孔径窗口。

**推荐容差带（可直接套用）：**
```text
用途 & 建议窗口
特征识别（精窗） & 目标值 0.02
刀具筛选（宽窗） & 目标值 0.05
边界不稳定时的临时放宽 & 目标值 0.08
```

**双层策略模板（示例：目标孔径 8.70）：**
```text
REM Application Criteria (feature exact window)
mwf.DIAMETER_1 >= 8.68
mwf.DIAMETER_1 <= 8.72

$$ Rule rejected because condition FALSE

REM Tool Attributes (tool soft window)
tool.Diameter >= 8.65
tool.Diameter <= 8.75

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "HM_Drill_D8p70_ToolSoftWindow_R01"
```

**执行顺序建议：** 先用精窗规则，失败后再尝试同工艺的宽窗规则，最后再落到人工兜底规则。

**兜底规则（最低优先级）建议：**
```text
REM Application Criteria
mwf.DIAMETER_1 >= 3.0
mwf.DIAMETER_1 <= 30.0

$$ Rule rejected because condition FALSE

REM Tool Attributes
REM (no hard assignment)

REM Less Worked Feature Attributes

REM Operation Attributes
oper.name = "HM_ManualCheck_NoToolMatch_R01"
```

**作用：** 当精确规则都不命中时，保留可见占位工序，提醒人工处理，不让特征静默漏加工。

### E) 版本迁移（NX12 $$ 新版本）检查表

- 字段可用性：逐条核对 `mwf.*`、`tool.*`、`oper.*` 是否仍受支持。
- 模板结构：确认默认注释段（`REM ...`）是否必须保留、顺序是否变化。
- 规则行为：抽检 10 个标准样孔，比较 NX12 与新版本输出工序是否一致。
- 刀库映射：确认新版本刀库命名/类别未导致 ToolClass 失配。
- 发布策略：采用“验证库先行”，通过回归后再切换生产库。

**迁移结论记录模板：**
```text
版本 Version: NX12 -> NXxxxx
日期 Date: YYYY-MM-DD
范围 Scope: 03_Hole_Making
结论 Result: PASS / FAIL（通过/失败）
Delta Rules: <rule list>
责任人 Owner: <工艺负责人>
```

## 8.3 Factory_Plate_General：一键录库顺序（按 MKE 实操）

**目标：** 按固定顺序创建库节点、规则和优先级，减少“漏建规则”“优先级冲突”“工序顺序错乱”。

### A) 建库顺序（建议严格按序执行）

- 创建父库：`Factory_Plate_General`。
- 创建子库：`01_Face_Milling`、`02_Pocket_Slot`、`03_Hole_Making`、`04_Chamfer`。
- 先录 `01`（1.1\~1.4），完成后立即做面加工样件验证。
- 再录 `02`（2.1\~2.6），验证口袋/槽互斥是否生效。
- 再录 `03`（3.1\~3.5），重点核验 Thread Bottom / Thread Through 与 Pin Pre/Ream 链路。
- 最后录 `04`（4.1\~4.4），确认倒角在精加工后执行。
- 最后添加最低优先级兜底规则：`Fallback_ManualCheck`。

### B) 每条规则录入动作清单（复制即用）

- 填写 6 组件：`Name/OperationClass/Priority/MWF/LWF/ToolClass`。
- 打开 `Conditions` 页，保留默认模板注释段，不删 `REM ...` 标题。
- 粘贴对应规则的 `Application Criteria` / `Tool Attributes` / `Operation Attributes`。
- 保存后立刻触发一次规则检查，确认无语法报错。
- 用单一测试特征验证命中是否符合预期（只命中目标规则）。

### C) 按模块的最小回归执行单（现场版）

```text
p{0.18}|>{}p{0.34}|>{}p{0.36}|}
模块 & 最小测试特征 & 通过判据
01\_Face\_Milling & 顶面+底面各 1 个 & 粗/精面工序顺序正确，命名可追溯
02\_Pocket\_Slot & 口袋 1 个 + 开槽 1 个 + 闭槽 1 个 & 口袋/槽不双命中，清角规则可触发
03\_Hole\_Making & 底孔/过孔/销孔各 1 组 & 过孔与底孔互斥；Pre->Ream 链路完整
04\_Chamfer & 孔口 1 个 + 外轮廓 1 条边 & 倒角不早于精加工，尺寸在窗口内
```

### D) 交付前最终闸门（Release Gate）

- **规则完整性：** 01/02/03/04 对应规则数量与本文档一致。
- **优先级完整性：** 无重复 priority；同模块按建议区间连续分布。
- **命中稳定性：** 边界值特征（如孔径窗口边界）命中结果可复现。
- **可追溯性：** 关键工序名包含模块、特征与版本号（`R03`）。
- **发布纪律：** 先验证库，后生产库；保留变更记录与责任人。

## 8.4 规则导入模板页（空白表单，可复用）

**用途：** 新增规则时先填表，再录入 MKE，确保跨人协作时字段齐全、命名统一、可审计。

### 模板 A：单条规则定义卡（复制后填写）

```text
[Rule Card]
Module: <01_Face_Milling / 02_Pocket\_Slot / 03_Hole_Making / 04_Chamfer>
Rule Name: <e.g. 2.7_Slot_Micro_D3>
版本 Version: <R01>

OperationClass: <...>
Priority: <...>
MWF: <...>
LWF: <...>
ToolClass: <...>

Application Criteria:
- <cond_1>
- <cond_2>

Tool Attributes:
- <cond_1>
- <cond_2>

Operation Attributes:
- oper.name = "<...>"

Expected Hit Feature:
- <which geometry should hit>

Expected Non-Hit Feature:
- <which geometry must not hit>

责任人 Owner: <工艺负责人>
日期 Date: YYYY-MM-DD
Review: <Pending/Approved>
```

### 模板 B：批量导入清单（建议先填此表）

```text
Module & Rule Name & Priority & Window/Criteria 摘要 & Version
01\_Face\_Milling & <...> & <...> & <...> & R..
02\_Pocket\_Slot & <...> & <...> & <...> & R..
03\_Hole\_Making & <...> & <...> & <...> & R..
04\_Chamfer & <...> & <...> & <...> & R..
```

### 模板 C：变更记录（Change Log）

```text
Date & Module & Delta Rules & Result & Owner
YYYY-MM-DD & 03\_Hole\_Making & +2 / -0 / \~1 & PASS/FAIL（通过/失败） & <Owner>
YYYY-MM-DD & 02\_Pocket\_Slot & +1 / -1 / \~0 & PASS/FAIL（通过/失败） & <Owner>
```

**使用建议：**

- 每次上线前，先更新模板 B 与模板 C，再执行本文件的 Release Gate 检查。
- 若规则窗口改动（如孔径窗、刀径窗），务必同步更新 Rule Name 或版本号 `R03 -> R04`。
- 对生产库仅允许 `Approved` 状态规则进入，避免实验规则误发布。

## 8.5 常见报错与修复对照表（现场排障）

**用途：** 当 MKE 规则无法保存、无法命中或命中异常时，按“现象 $$ 原因 $$ 修复”快速定位。

```text
p{0.21}|>{}p{0.26}|>{}p{0.43}|}
现场现象 & 常见原因 & 建议修复动作
规则保存时报语法错 & 在 Application Criteria 写了赋值/If Then & 仅保留布尔条件，每行一个；删除赋值与脚本语句
规则始终不命中 & 窗口过窄或字段名不受支持 & 先放宽窗口（如 0.08）并核对字段可用性
同一特征命中多条规则 & 窗口重叠或优先级冲突 & 收紧窗口并拉开 priority，确保互斥
命中后找不到合适刀具 & Tool Attributes 过严或刀库映射错误 & 放宽刀径窗并检查 Cutter Diameter 映射
仅生成粗加工不生成精加工 & 精加工规则 priority/条件设置不当 & 提高精加工优先级并核对命中条件
先倒角后精加工（顺序错） & 倒角规则优先级过高 & 下调倒角规则优先级，放到精加工后
Pin 孔只有 Ream 没有 Pre & 链路条件未绑定（MACHINING\_RULE） & 在 Ream 规则增加 `lwf.MACHINING\_RULE` 约束
规则名可读性差难追溯 & 未执行统一命名模板 & 按 `模块\_工艺\_特征\_窗口\_刀具\_R版本` 重命名
```

### 快速排障流程（建议 5 步）

- **先查语法：** 确保模板分段完整，尤其 `REM Application Criteria` 与拒绝注释行。
- **再查字段：** 抽检 `mwf.* / tool.* / oper.*` 在当前版本是否可用。
- **再查窗口：** 先扩大到业务可接受宽窗，确认能命中后再逐步收紧。
- **再查优先级：** 同类规则按“窄窗优先、特化优先、兜底最低”排序。
- **最后回归：** 用本文最小样件集复跑，记录到 Change Log。

### 现场兜底口令（建议保留在团队 SOP）

```text
若规则异常：先保产线（启用 ManualCheck 占位）-> 再复盘窗口/优先级 -> 最后发版。
```

## 附录A：术语中英对照与缩写表（NX12/MKE）

### A) 核心术语中英对照

```text
中文术语 & 英文术语
加工知识库 & Machining Knowledge
规则编辑器 & Machining Knowledge Editor (MKE)
规则优先级 & Priority
更多加工特征 & More Worked Feature (MWF)
更少加工特征 & Less Worked Feature (LWF)
工序类型 & OperationClass
刀具类型 & ToolClass
应用条件 & Application Criteria
刀具属性条件 & Tool Attributes
工序属性赋值 & Operation Attributes
孔加工 & Hole Making
面加工 & Face Milling
口袋加工 & Pocket Milling / Cavity Milling
槽加工 & Slot Milling
清角加工 & Rest Milling
倒角加工 & Chamfer Milling
兜底人工检查 & Fallback Manual Check
```

### B) 常用缩写（培训必背）

```text
缩写 & 含义
MKE & Machining Knowledge Editor
MK & Machining Knowledge
MWF & More Worked Feature
LWF & Less Worked Feature
THK & Thickness（厚度）
DEPTH & 特征深度
WIDTH & 特征宽度
DIA / DIAMETER & 直径
Rxx & 规则版本号（如 R03/R04）
SOP & Standard Operating Procedure（标准作业流程）
```

### C) 命名字段建议映射（便于跨团队统一）

```text
命名片段 & 推荐语义
HM / FM / PS / CF & 模块前缀（Hole/Face/Pocket\_Slot/Chamfer）
Drill / Ream / Face / Slot / Chamfer & 工艺动作
ThreadBottom / ThreadThrough / Pin & 特征子类
D8p10-8p98 & 特征窗口（直径区间）
T8p7 & 刀具关键参数（刀径）
R01 & 规则版本
```

**使用建议：**

- 新人培训先发“1页速查讲义 + 本附录”，再进 MKE 实操。
- 规则评审时，先核对术语与缩写是否统一，再核对窗口和优先级。
- 发布说明建议引用本附录术语，避免同义词导致跨团队误解。

## 附录B：实施里程碑与角色分工（项目落地版）

### A) 四周实施里程碑（建议）

```text
周次 & 目标 & 可交付物
第1周 Week 1 & 完成库结构与命名规范统一 & 规则库骨架 + 命名规范 v1
第2周 Week 2 & 完成 01/02/03/04 首版规则录入 & 可运行规则库 v1 + 小样件结果
第3周 Week 3 & 完成冲突修正与优先级优化 & 冲突清单关闭 + 回归通过报告
第4周 Week 4 & 完成生产发布与培训交接 & 生产库发布单 + 培训签到与考核记录
```

### B) 角色分工（RACI 简化版）

```text
角色 & 主要职责 & 关键产出
工艺负责人 & 规则策略与优先级审批 & 规则评审结论、发布许可
MKE 工程师 & 规则录入、调试、修复 & 规则文件、命中验证记录
CAM 程序员 & 试切路径核对与刀具适配 & 程序验证单、刀具问题清单
质量工程师 & 首件检验与偏差反馈 & 首件报告、偏差闭环单
生产主管 & 节拍与风险协调 & 生产切换确认单
```

### C) 发布门槛（Go/No-Go）

- **Go 条件：** 最小回归全通过，关键特征零漏加工，规则命名可追溯。
- **No-Go 条件：** 存在双命中未解、关键工序缺失、无刀具匹配未闭环。
- **灰度建议：** 先在单产线/单机床灰度 1 周，再全线放开。

### D) 交接包清单（上线必备）

- 规则库导出包（含版本号 `R03`）。
- 回归报告（样件、命中截图、异常闭环）。
- 变更记录（模板 C 已填写）。
- 现场速查讲义（本文件 1 页版）。
- 回滚方案（上一个稳定版本 + 恢复步骤）。

## 附录C：规则库审核评分表（上线验收可量化）

**目的：** 将“可用”变成“可量化可签字”，用于版本发布前评审与跨团队对齐。

### A) 评分维度与权重（100 分）

```text
维度 & 评分说明 & 权重
规则完整性 & 模块覆盖、规则数量、模板结构完整性 & 20
命中准确性 & 单特征单命中、互斥逻辑正确、边界稳定 & 25
刀具匹配性 & 刀具可用率、无误匹配、无无刀具报错 & 20
工序链路正确性 & Pre/Ream、粗/精、倒角顺序正确 & 20
可追溯与文档化 & 命名规范、变更记录、发布说明齐全 & 15
合计 & 发布建议阈值： 85 分 & 100
```

### B) 审核打分模板（复制即用）

```text
[发布评审表 Release Review Sheet]
版本 Version: <R03>
日期 Date: YYYY-MM-DD
范围 Scope: <01/02/03/04 or full（全量）>

1) 规则完整性 (20): __
2) 命中准确性 (25): __
3) 刀具匹配性 (20): __
4) 工序链路正确性 (20): __
5) 可追溯与文档化 (15): __

总分 Total Score: __ / 100
结论 Result: PASS / CONDITIONAL PASS / FAIL（通过/有条件通过/失败）

主要风险 Major Risks:
- <risk_1>
- <risk_2>

发布前必做项 Required Actions Before Release:
- <action_1>
- <action_2>

评审人 Reviewer: <质量负责人>
责任人 Owner: <工艺负责人>
```

### C) 评分解释建议

- **85\~100：** 可发布（建议先灰度）。
- **70\~84：** 条件发布（需完成限制项并复核）。
- **<70：** 不可发布（必须补齐关键缺陷后重评）。

## 附录D：风险清单与回滚预案（发布闭环模板）

### A) 风险分级与响应时限

```text
风险等级 & 判定标准（示例） & 处置时限
P0 & 关键特征漏加工/错加工，影响交付安全 & 立即回滚（**<30 min**）
P1 & 工序链路错误（如缺 Ream/倒角顺序错） & 当班修复（**<4 h**）
P2 & 命名/日志缺失、次要规则冲突 & 24 小时内闭环
P3 & 文档与培训项不一致、体验问题 & 版本迭代修复
```

### B) 回滚触发条件（建议）

- 连续出现 2 次及以上关键特征错加工。
- 同一批次出现“规则命中异常 + 无法人工快速兜底”。
- 评分表结果低于 `70` 分且存在 P0/P1 未关闭项。

### C) 回滚操作模板（复制即用）

```text
[回滚工单 Rollback Ticket]
日期 Date: YYYY-MM-DD HH:MM
当前版本 Current Version: <R03>
回滚目标 Rollback Target: <R02>

触发原因 Trigger Reason:
- <P0/P1 description>

立即措施 Immediate Actions:
1) 冻结当前发布 Freeze current release
2) 切换到上一稳定规则包 Switch to previous stable rule pack
3) 通知工艺/CAM/生产负责人 Notify process/CAM/production owners

回滚后验证 Verification After Rollback:
- 样件 A Sample part A: PASS/FAIL（通过/失败）
- 样件 B Sample part B: PASS/FAIL（通过/失败）
- 关键特征链 Key feature chain: PASS/FAIL（通过/失败）

责任人 Owner: <工艺负责人>
审批人 Approver: <生产负责人>
状态 Status: CLOSED / MONITORING（已关闭/监控中）
```

### D) 复盘最小模板（上线后 24h 内）

```text
复盘项 & 必答问题 & 输出物
触发原因 & 是窗口、优先级还是刀库映射问题？ & 根因结论
影响范围 & 影响了哪些机型/板类零件/班次？ & 影响清单
防再发措施 & 下次如何提前拦截？ & 规则/流程改进项
验证证据 & 哪些样件已复测通过？ & 回归记录
```

## 附录E：运维监控看板与周报模板（持续改进）

### A) 核心监控指标（建议每周统计）

```text
指标 & 定义 & 目标值（建议）
规则命中成功率 & 成功生成预期工序的特征数 / 总特征数 & 98\%
双命中冲突率 & 单特征命中多条互斥规则比例 & 1\%
无刀具失败率 & 因刀具条件不满足导致失败比例 & 2\%
人工兜底触发率 & ManualCheck 占位触发比例 & 3\%
回滚发生次数 & 单周回滚次数 & =0（目标）
```

### B) 周报模板（复制即用）

```text
[周度规则运营报告 Weekly RuleOps Report]
周次 Week: YYYY-WW
生产版本 Version in Production: <R03>

1) 命中成功率 Hit Success Rate: __ %
2) 冲突率 Conflict Rate: __ %
3) 无刀具失败率 No-Tool Failure Rate: __ %
4) 人工兜底触发率 ManualCheck Trigger Rate: __ %
5) 回滚次数 Rollback Count: __

前三问题 Top 3 Issues:
- <issue_1>
- <issue_2>
- <issue_3>

下周行动 Actions for Next Week:
- <action_1>
- <action_2>

责任人 Owner: <工艺负责人>
评审人 Reviewer: <质量负责人>
```

### C) 持续改进节奏（PDCA）

- **Plan：** 根据周报确定优先修复的窗口冲突与刀具匹配问题。
- **Do：** 在验证库调整规则并执行最小回归。
- **Check：** 对比调整前后关键指标（命中率、冲突率、兜底率）。
- **Act：** 通过评审后发布生产库，并更新 Change Log 与评分表。

## 9. 文档元信息（版本管理）

```text
p{0.24}|>{}p{0.66}|}
文档名称 & Factory\_Plate\_General 加工规则库落地手册
文档版本 & v1.3
发布编号 & R03
最后修订日期 & 2026-03-15
维护人 & <工艺负责人>
状态 & 待签核（Ready for Signoff）
本次统一范围摘要 & 术语口径、模板字段、双语表头、板类语境、版本规则、工艺顺序重排、标题层级统一
```

**修订规则建议：**

- 规则窗口、优先级或命名模板发生变化时，文档版本至少递增小版本号（如 v1.1 -> v1.2）。
- 跨模块结构调整（新增/删减模块）时，递增大版本号（如 v1.x -> v2.0）。
- 每次发布必须同步更新“最后修订日期”和 Change Log。

## Change Log（本次修订）

```text
p{0.52}|}
版本 & 日期 & 修订说明
v1.3（R03） & 2026-03-15 & 按板类工艺顺序重排章节；统一主干编号；优化工艺卡版式（表头浅灰、表格间距）；统一标题层级样式与间距。
```

## 发布签核结论（Rule Priority 审核摘要）

**审核日期：** 2026-03-15

**审核口径：** 同路径 + 同 Priority + 同 OperationClass（全量口径）与窗口重叠口径（有效口径）双轨核查，并完成 XML 写回复核。

- **规则总数：** 79
- **初始全量同组：** 7 组
- **初始有效同组：** 5 组
- **最终 XML 全量同组：** 0 组（已清零）

**处理说明：**

- 先按有效口径处理 5 组（66 条规则），再处理剩余 2 组（10 条规则）。
- 对同组内规则采用细粒度优先级拆分（`base + 0.001...`），消除并列优先级抢占风险。

**结论：** 当前 `machining_knowledge.xml` 已实现同路径、同 Priority、同 OperationClass 的冲突清零。

**归档依据：** `RULE_XML_POSTCHECK.md`、`RULE_XML_UPDATE_LOG.md`、`RULE_PRIORITY_DIFF.md`。

### 入库 Priority 明细（本次写回结果）

**说明：** 以下为本次冲突清零后写回 `machining_knowledge.xml` 的 Priority 规则；同组内采用 `base+0.001` 递增。

```text
p{0.46}|>{}p{0.28}|>{}p{0.18}|}
Group(Path) & OperationClass & Priority（入库）
2.1\_SpotDrill & `hole\_making.SPOT\_DRILLING` & 1, 8, 10.001~10.005
2.2\_Thread\_Bottom & `hole\_making.DRILLING` & 10.001~10.016
2.3\_Clearance\_Drill & `hole\_making.DRILLING` & 10.001~10.005
2.4\_Ream\&Pre-Drill（Ream） & `hole\_making.DRILLING` & 5.001~5.016
2.4\_Ream\&Pre-Drill（Pre-Drill） & `hole\_making.DRILLING` & 10.001~10.016
2.5\_Counterbore & `hole\_making.HOLE\_MILLING` & 5.001~5.016
03\_Pocket\_Slot & `mill\_planar.FLOOR\_WALL` & 0.12, 3.101, 3.102
```

## 发布签核页模板（归档用）

- 发布版本：R03 / v1.3
- 发布日期：2026-03-15
- 变更范围：Full
- 回归结果：PASS / CONDITIONAL PASS / FAIL
- 评分结果：__ / 100

## 签核文档导航（建议阅读顺序）

- `RULE_XML_POSTCHECK.md`：确认 XML 回读后冲突是否清零（最终结论）。
- `RULE_XML_UPDATE_LOG.md`：查看优先级写回过程、分组明细与最终审计表。
- `RULE_RELEASE_SUMMARY.md`：一页评审摘要（管理层快速阅读）。
- `RULE_PRIORITY_DIFF.md`：了解全量口径与有效口径差异来源。

# 协作

点击``Share''菜单即可邀请协作者。你编辑时，他们会实时看到你的更新。你也可以通过高亮文本并选择“Leave a comment.”来添加批注。