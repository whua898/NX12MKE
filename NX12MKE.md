# NX12 MKE 板类零件自动化加工规则库手册

**版本**: v2.0 | **发布日期**: 2026-04-27 | **状态**: 生产就绪

---

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 核心数据源](#2-核心数据源)
- [3. 规则库架构](#3-规则库架构)
- [4. MKE语法与编写规范](#4-mke语法与编写规范)
- [5. 完整规则清单](#5-完整规则清单)
- [6. 工艺常量参考](#6-工艺常量参考)
- [7. 质量控制与测试](#7-质量控制与测试)
- [8. 运维与持续改进](#8-运维与持续改进)
- [附录](#附录)

---

## 1. 项目概述

### 1.1 项目目标

建立板类零件的**自动化特征加工规则库**，实现从CAD模型识别到NC程序生成的全流程自动化，覆盖：
- ✅ 面加工（粗/精铣）
- ✅ 型腔与槽加工（粗/精/清角）
- ✅ 孔系加工（定位钻/底孔/过孔/销孔/大孔）
- ✅ 倒角与去毛刺

### 1.2 技术栈

| 组件 | 技术/工具 | 说明 |
|------|----------|------|
| **CAD/CAM平台** | Siemens NX 12.0 | 核心设计与加工环境 |
| **规则引擎** | Machining Knowledge Editor (MKE) | 基于XML的声明式规则系统 |
| **规则语言** | MKE Conditions语法 | 声明式条件过滤 + 有限属性赋值 |
| **数据格式** | XML (.xml), DAT (.dat) | 规则库、刀具库、刀柄库 |
| **脚本语言** | Python 3.x | 数据处理、规则生成、验证工具 |
| **版本控制** | Git | 规则库版本管理 |

### 1.3 规则库规模

| 指标 | 数值 |
|------|------|
| 总规则数 | ~50条 |
| 主模块数 | 4个 |
| 子模块数 | 5个（孔加工库） |
| 优先级范围 | 1100 ~ 3399 |
| 覆盖工艺 | 面铣、型腔、槽、孔、倒角 |
| 支持孔径 | Ø3.0 ~ Ø22.0mm |
| 支持螺纹 | M4 ~ M20 |
| 支持销孔 | Ø4 ~ Ø20mm |

---

## 2. 核心数据源

### 2.1 文件清单

| 文件名 | 大小 | 用途 | 关键内容 |
|--------|------|------|----------|
| `machining_knowledge.xml` | 9.8MB | 原始知识库 | 工艺常量、识别规则、Prolog代码、二进制块 |
| `tool_database.dat` | 488KB | 刀具库定义 | 刀具类型、直径、刃长、齿数、材质 |
| `holder_database.dat` | 22KB | 刀柄库定义 | BT50/ER系统、几何尺寸、干涉模型 |
| `mke_extracted_rules.json` | 28KB | 提取的工艺常量 | 62个工艺常量、IT等级、粗糙度阈值 |
| `NX12MKE.md` | 60KB | 规范文档 | 规则定义、语法边界、优先级设计 |

### 2.2 刀具库关键数据

**常用刀具规格**（基于 `tool_database.dat`）：

| 刀具类型 | 直径范围(mm) | 典型规格 | 适用工艺 |
|---------|-------------|----------|---------|
| 面铣刀 | Ø32 ~ Ø80 | D63, D50, D32 | 面加工粗/精 |
| 立铣刀 | Ø2 ~ Ø20 | D12, D10, D8, D6, D4 | 型腔、槽、清角 |
| 麻花钻 | Ø3.4 ~ Ø21 | D3.4(M4), D6.9(M8), D10.5(M12) | 螺纹底孔/过孔 |
| 中心钻 | Ø10 | D10 | 定位钻(Spot) |
| 铰刀 | Ø4 ~ Ø20 | D4.0, D6.0, D10.0, D16.0 | 销孔精加工 |
| 倒角刀 | Ø5 ~ Ø25 | D10(90°), D16(90°) | 孔口/外轮廓倒角 |

### 2.3 刀柄库关键数据

**夹持系统**（基于 `holder_database.dat`）：

| 系统类型 | 规格 | 适用刀具直径 | 结构特点 |
|---------|------|------------|---------|
| BT50-ER32 | ER32-100 | Ø3~Ø20 | 弹簧夹头，通用性强 |
| BT50-ER40 | ER40-100 | Ø6~Ø26 | 大直径刀具 |
| BT50-SIDELOCK | SL-100 | Ø10~Ø32 | 侧固式，重载加工 |

**干涉检查关键字段**：
- `DIAM`: 刀柄最大直径
- `LENGTH`: 刀柄总长
- `PROTRUSION`: 刀具突出长度
- `TAPER_ANGLE`: 锥角（通常2°30'）

---

## 3. 规则库架构

### 3.1 层级结构

```text
Machining Knowledge
└─ Factory_Plate_General (板类通用库)
   ├─ 01_Face_Milling (面加工库) [Priority: 1200~1299]
   │   ├─ 1.1_Face_Top_Rough
   │   ├─ 1.2_Face_Top_Finish
   │   ├─ 1.3_Face_Bottom_Finish
   │   └─ 1.4_Face_ThinWall_LightCut
   ├─ 02_Pocket_Slot (型腔与槽库) [Priority: 2400~2499]
   │   ├─ 2.1_Pocket_Rough_General
   │   ├─ 2.2_Pocket_Finish_Wall
   │   ├─ 2.3_Pocket_Finish_Floor
   │   ├─ 2.4_Slot_Open_Rough
   │   ├─ 2.5_Slot_Closed_Finish
   │   └─ 2.6_Corner_Rest_Mill
   ├─ 03_Hole_Making (孔加工库) [Priority: 2100~3399]
   │   ├─ 3.1_Spot (定位钻) [Priority: 1100]
   │   ├─ 3.2_Thread_Bottom (螺纹底孔) [Priority: 2210~2280]
   │   ├─ 3.3_Thread_Through (螺纹过孔) [Priority: 2310~2350]
   │   ├─ 3.4_Pin_Hole (销孔) [Priority: 2110~3180]
   │   │   ├─ Pre-Drill (预钻) [Priority: 2110~2180]
   │   │   └─ Ream (铰孔) [Priority: 3110~3180]
   │   └─ 3.5_Large_Hole (大孔) [Priority: 3200+]
   └─ 04_Chamfer (倒角库) [Priority: 3300~3399]
       ├─ 4.1_Hole_Chamfer_C0p5
       ├─ 4.2_Hole_Chamfer_C1p0
       ├─ 4.3_Outer_Chamfer_General
       └─ 4.4_Deburr_Light_Pass
```

### 3.2 规则定义六要素

每条规则必须明确以下6个组件：

| 要素 | 说明 | 示例 |
|------|------|------|
| **Name** | 规则名称（遵循命名规范） | `3.2_Thread_Bottom_D8p7` |
| **OperationClass** | 工序类型（决定刀具类别） | `hole_making.DRILLING` |
| **Priority** | 优先级（数值越大越先尝试） | `2240` |
| **MWF** | More Worked Feature（目标特征） | 当前工序要生成的特征 |
| **LWF** | Less Worked Feature（输入特征） | 当前工序的输入特征（上游输出） |
| **ToolClass** | 刀具类型（与刀具库匹配） | `TWIST_DRILL`, `FACE_MILL`, `REAMER` |

### 3.3 命名规范

**格式**: `模块_工艺_特征_范围_刀具_R版本`

**示例**：
- `FM_Face_Top_A400-200k_D63_R01` (面加工)
- `HM_Drill_ThreadBottom_D8p10-8p98_T8p7_R01` (螺纹底孔)
- `HM_Ream_Pin_D9p98-10p02_T10_R01` (销孔铰孔)

**简写规则**（用于规则树显示）：
- `1.1_Face_Top_Rough`
- `3.2_Thread_Bottom_D8p7`
- `3.4_Pin_Pre_D10`

---

## 4. MKE语法与编写规范

### 4.1 规则语言本质

> **一句话**：NX12 MKE 规则语言不是脚本语言，而是**"声明式条件过滤器 + 有限的工序属性赋值"**。

### 4.2 固定结构（顺序不可改、标题不可删）

```text
REM Application Criteria
<只允许布尔条件，每行一个条件；多行自动 AND>

$$ Rule rejected because condition FALSE

REM Tool Attributes
<以筛选条件为主；可对部分 tool.* 属性赋值>
<示例：tool.Diameter = 10.0>

REM Less Worked Feature Attributes
<可空>

REM Operation Attributes
<允许 oper.* 赋值>
```

### 4.3 Application Criteria（应用条件）

**✅ 允许**：
- 布尔条件表达式：`mwf.DIAMETER_1 >= 3.0`
- 每行一个条件，多行自动 **AND**
- 比较运算符：`>=`, `<=`, `>`, `<`, `=`

**❌ 禁止**：
- `If/Then/Else/End If` 等脚本语句
- 任何赋值语句（含 `Rule_Validity = FALSE`）
- 逻辑运算符（`AND`, `OR`, `NOT`）

**拒绝规则的方式**：条件为 FALSE 即自动拒绝（无需写"reject"语句）

### 4.4 Tool Attributes（刀具属性）

**允许操作**：
- **筛选**：`tool.Diameter >= 9.5` / `tool.Diameter <= 10.5`
- **赋值**（已测试无语法错）：`tool.Diameter = 10.0`
- **类型匹配**：`tool.Type = "DRILL"`

**注意事项**：
- `tool.SubType` 是否存在取决于模板/版本
- 刀具类别/类型仍由 **OperationClass** 决定
- 直径范围应略宽于目标值（约 ±0.05mm）

### 4.5 Operation Attributes（工序属性）

**允许操作**：
- `oper.name = "3.2_Thread_Bottom_D8p7"`
- `oper.Feed_Cut = 0.15`（以模板实际支持字段为准）
- `oper.Geometry_Roles = mwf.FACES_CYLINDER_1`

**不建议**：
- 在这里写任何条件判断（一般不支持）
- 复杂切削参数（建议放到 Add-On 附加工艺模板）

### 4.6 工序链路控制

**使用 MACHINING_RULE 串联工序**：

```text
REM Drilling rule (producer)
mwf.MACHINING_RULE = "TWIST_DRILL"

REM Reaming rule (consumer)
lwf.MACHINING_RULE = "TWIST_DRILL"
```

**应用场景**：
- 销孔的铰孔规则要求 `lwf.MACHINING_RULE = "TWIST_DRILL"`
- 确保先有预钻再铰孔，防止"跳工序"

---

## 5. 完整规则清单

### 5.1 01_Face_Milling (面加工库)

| 规则名 | OperationClass | Priority | 应用条件 | 刀具直径范围 |
|--------|---------------|----------|---------|---------|
| 1.1_Face_Top_Rough | face_milling.FACE_MILLING | 1210 | AREA:[400,200000] | D:[40,80] |
| 1.2_Face_Top_Finish | face_milling.FACE_MILLING | 1220 | AREA:[300,200000] | D:[32,63] |
| 1.3_Face_Bottom_Finish | face_milling.FACE_MILLING | 1230 | AREA:[300,200000] | D:[32,63] |
| 1.4_Face_ThinWall_LightCut | face_milling.FACE_MILLING | 1240 | AREA:[100,50000], THK≤8 | D:[16,40] |

**MWF/LWF**: `MWF=PLANAR_FACE`, `LWF=BLANK`

### 5.2 02_Pocket_Slot (型腔与槽库)

| 规则名 | OperationClass | Priority | 应用条件 | 刀具直径范围 |
|--------|---------------|----------|---------|---------|
| 2.1_Pocket_Rough_General | cavity_milling.CAVITY_MILL | 2410 | DEPTH:[1,40], R_min≥2 | D:[8,20] |
| 2.2_Pocket_Finish_Wall | planar_milling.PROFILE | 2420 | DEPTH:[1,40], WALL_ANGLE≤2 | D:[6,16] |
| 2.3_Pocket_Finish_Floor | planar_milling.PLANAR_MILL | 2430 | DEPTH:[1,40], BOTTOM_R≤1 | D:[6,20] |
| 2.4_Slot_Open_Rough | slot_milling.SLOT_MILL | 2440 | WIDTH:[6,24], DEPTH≤20 | D:[5,16] |
| 2.5_Slot_Closed_Finish | slot_milling.SLOT_MILL | 2450 | WIDTH:[4,16], DEPTH≤20 | D:[3,10] |
| 2.6_Corner_Rest_Mill | rest_milling.REST_MILL | 2460 | R_min≤2, DEPTH≤30 | D:[2,8] |

**MWF/LWF**: `MWF=POCKET/SLOT`, `LWF=BLANK`

### 5.3 03_Hole_Making (孔加工库)

#### 3.1_Spot (定位钻)

| 规则名 | Priority | 应用条件 | 刀具 |
|--------|---------|---------|------|
| 3.1_Spot_D10 | 1100 | D:[3.0,22.0] | D10 Center Drill |

#### 3.2_Thread_Bottom (螺纹底孔)

| 规则名 | 螺纹 | Priority | 孔径范围 | 刀具直径范围 |
|--------|------|---------|---------|---------|
| 3.2_Thread_Bottom_D3p4 | M4 | 2210 | [3.10, 3.50] | [3.35, 3.45] |
| 3.2_Thread_Bottom_D4p3 | M5 | 2220 | [4.10, 4.50] | [4.25, 4.35] |
| 3.2_Thread_Bottom_D5p2 | M6 | 2230 | [5.10, 5.50] | [5.15, 5.25] |
| 3.2_Thread_Bottom_D6p9 | M8 | 2240 | [6.50, 6.98] | [6.85, 6.95] |
| 3.2_Thread_Bottom_D8p7 | M10 | 2250 | [8.10, 8.98] | [8.65, 8.75] |
| 3.2_Thread_Bottom_D10p5 | M12 | 2260 | [10.10, 10.80] | [10.45, 10.55] |
| 3.2_Thread_Bottom_D14p3 | M16 | 2270 | [13.50, 14.50] | [14.25, 14.35] |
| 3.2_Thread_Bottom_D17p8 | M20 | 2280 | [17.10, 17.98] | [17.75, 17.85] |

**MWF/LWF**: `MWF=HOLE`, `LWF=BLANK`  
**OperationClass**: `hole_making.DRILLING`

#### 3.3_Thread_Through (螺纹过孔)

| 规则名 | Priority | 孔径范围 | 刀具直径范围 |
|--------|---------|---------|---------|
| 3.3_Thread_Through_D9 | 2310 | [8.98, 9.02] | [8.95, 9.05] |
| 3.3_Thread_Through_D11 | 2320 | [10.98, 11.02] | [10.95, 11.05] |
| 3.3_Thread_Through_D13 | 2330 | [12.98, 13.02] | [12.95, 13.05] |
| 3.3_Thread_Through_D17 | 2340 | [16.98, 17.02] | [16.95, 17.05] |
| 3.3_Thread_Through_D21 | 2350 | [20.98, 21.02] | [20.95, 21.05] |

**MWF/LWF**: `MWF=HOLE`, `LWF=STEP1HOLE`  
**OperationClass**: `hole_making.DRILLING`

#### 3.4_Pin_Hole (销孔)

**预钻孔 (Pre-Drill)**:

| 规则名 | 成品孔径 | Priority | 预钻范围 | 刀具 |
|--------|---------|---------|---------|------|
| 3.4_Pin_Pre_D4 | Ø4 | 2110 | [3.68, 3.72] | D3.7 |
| 3.4_Pin_Pre_D5 | Ø5 | 2120 | [4.68, 4.72] | D4.7 |
| 3.4_Pin_Pre_D6 | Ø6 | 2130 | [5.68, 5.72] | D5.7 |
| 3.4_Pin_Pre_D8 | Ø8 | 2140 | [7.68, 7.72] | D7.7 |
| 3.4_Pin_Pre_D10 | Ø10 | 2150 | [9.68, 9.72] | D9.7 |
| 3.4_Pin_Pre_D12 | Ø12 | 2160 | [11.68, 11.72] | D11.7 |
| 3.4_Pin_Pre_D16 | Ø16 | 2170 | [15.68, 15.72] | D15.7 |
| 3.4_Pin_Pre_D20 | Ø20 | 2180 | [19.68, 19.72] | D19.7 |

**铰孔 (Ream)**:

| 规则名 | 成品孔径 | Priority | 铰孔范围 | 刀具 |
|--------|---------|---------|---------|------|
| 3.4_Pin_Ream_D4 | Ø4 | 3110 | [3.98, 4.02] | D4.0 |
| 3.4_Pin_Ream_D5 | Ø5 | 3120 | [4.98, 5.02] | D5.0 |
| 3.4_Pin_Ream_D6 | Ø6 | 3130 | [5.98, 6.02] | D6.0 |
| 3.4_Pin_Ream_D8 | Ø8 | 3140 | [7.98, 8.02] | D8.0 |
| 3.4_Pin_Ream_D10 | Ø10 | 3150 | [9.98, 10.02] | D10.0 |
| 3.4_Pin_Ream_D12 | Ø12 | 3160 | [11.98, 12.02] | D12.0 |
| 3.4_Pin_Ream_D16 | Ø16 | 3170 | [15.98, 16.02] | D16.0 |
| 3.4_Pin_Ream_D20 | Ø20 | 3180 | [19.98, 20.02] | D20.0 |

**OperationClass**:  
- Pre-Drill: `hole_making.DRILLING`
- Ream: `hole_making.REAMING`

**工序链路**:
```text
Pre-Drill: lwf.MACHINING_RULE = "BLANK"
Ream:      lwf.MACHINING_RULE = "TWIST_DRILL"
```

#### 3.5_Large_Hole (大孔)

| 规则名 | Priority | 应用条件 | 策略 |
|--------|---------|---------|------|
| 3.5_Large_Hole_D24 | 3200+ | D > 21 | Hole Milling (孔铣) |

**说明**: 圆孔 D>21 走孔铣策略；方孔/条孔建议走型腔/轮廓类铣削策略。

### 5.4 04_Chamfer (倒角库)

| 规则名 | Priority | 应用条件 | 刀具直径范围 |
|--------|---------|---------|---------|
| 4.1_Hole_Chamfer_C0p5 | 3310 | D:[3,20] | D:[5,16] |
| 4.2_Hole_Chamfer_C1p0 | 3320 | D:[6,30] | D:[8,20] |
| 4.3_Outer_Chamfer_General | 3330 | EDGE:[20,5000] | D:[8,25] |
| 4.4_Deburr_Light_Pass | 3340 | EDGE:[5,8000] | D:[6,20] |

**OperationClass**: `mill_planar.CHAMFER_MILLING`

---

## 6. 工艺常量参考

### 6.1 精度等级 (IT Class)

基于 `mke_extracted_rules.json` 提取：

| 工艺 | IT下限 | IT上限 | 说明 |
|------|--------|--------|------|
| **钻孔 (DRILL)** | IT11 | IT16 | 粗加工精度 |
| **铰孔 (REAM)** | IT5 | IT10 | 高精度孔加工 |
| **铣削 (MILL)** | IT9 | IT16 | 面/型腔加工 |
| **镗孔 (BORE)** | IT6 | IT10 | 大孔精加工 |

### 6.2 表面粗糙度 (Roughness Ra)

| 工艺 | Ra下限 (μm) | Ra上限 (μm) | 说明 |
|------|------------|------------|------|
| **铣削 (MILL)** | 0.4 | 25 | Ra=6.3为精加工阈值 |
| **钻孔 (DRILL)** | 0.8 | 12.5 | 粗加工表面 |
| **铰孔 (REAM)** | 0.4 | 3.2 | 高精度表面 |
| **镗孔 (BORE)** | 0.8 | 12.5 | 大孔表面 |

### 6.3 关键工艺常量

| 常量名 | 值 | 说明 |
|--------|-----|------|
| `Pre_Drill_Limit` | 12mm | 孔径≤12mm可直接钻，>12mm需预钻 |
| `Center_Chamfer_Limit` | 12mm | 孔径≤12mm由定点钻倒角 |
| `LWF_Predrill_Factor_Lower` | 0.2 | 预钻孔下限系数 (Final_Dia × 0.2) |
| `LWF_Predrill_Factor_Upper` | 0.65 | 预钻孔上限系数 (Final_Dia × 0.65) |
| `Tap_Predrill_Tolerance_Factor` | 0.05 | 螺纹底孔公差系数 |
| `Thru_Hole_Clearance` | 1.5mm | 通孔刀具超出量 |
| `PointAngle_TwistDrill` | 118° | 麻花钻顶角 |
| `Depth_Dia_Ratio_Limit` | 5 | 深径比限制（枪钻） |
| `bool_Use_Spot_Drill_Yes1_No0` | 1 | 启用定点钻 |

### 6.4 程序顺序组 (POG)

| 常量名 | 值 | 用途 |
|--------|-----|------|
| `POG_SpotDrill` | SPOT_DRILL | 定位钻工序组 |
| `POG_Drill` | DRILL | 钻孔工序组 |
| `POG_CBore` | COUNTERBORE | 沉孔工序组 |
| `POG_CSink` | COUNTERSINK | 倒角工序组 |
| `POG_Tap` | TAP | 攻丝工序组 |
| `POG_ThreadMill` | MILL_FINISH | 螺纹铣工序组 |
| `POG_CounterMill` | MILL_SEMI_FINISH | 反铣工序组 |
| `POG_Debur` | DEBUR | 去毛刺工序组 |

---

## 7. 质量控制与测试

### 7.1 规则冲突处理

**优先级设计原则**：

```text
窄范围优先 > 宽范围兜底
特化优先 > 通用规则
人工兜底永远最低
```

**互斥条件示例**（底孔 vs 过孔）：

```text
REM Thread bottom rule: only in bottom-hole window
mwf.DIAMETER_1 >= 8.10
mwf.DIAMETER_1 <= 8.98

REM Thread through rule: only in through-hole exact window
mwf.DIAMETER_1 >= 8.98
mwf.DIAMETER_1 <= 9.02
```

**关键规则**：
- 同一特征类型下，优先级越高越先尝试
- Ream优先级必须高于对应Pre（确保工序链路正确）
- Fallback规则使用最低优先级

### 7.2 回归测试样件

**最小样件集**（每次改规则后必跑）：

| 测试类型 | 样件规格 | 验证目标 |
|---------|---------|---------|
| 螺纹底孔 | M4/M6/M10 各1个 | 底孔范围命中正确 |
| 螺纹过孔 | Ø9/Ø11/Ø13 各1个 | 过孔范围互斥 |
| 销孔 | Ø6/Ø10/Ø16 各1组 | Pre+Ream链路完整 |
| 大孔 | Ø24 | 走Hole Milling，不走Drilling |
| 边界孔 | Ø8.98, Ø9.02 | 范围边界命中稳定性 |
| 面加工 | Top/Bottom面各1个 | 粗精顺序正确 |
| 型腔槽 | 型腔1个，开槽1个 | 不双命中，清角可触发 |
| 倒角 | 孔倒角1个，外轮廓1个 | 倒角在精加工后执行 |

**通过标准**：
- ✅ 每个测试孔仅生成预期工序；不得出现多余工序
- ✅ 关键工序命名必须包含规则ID（便于审计）
- ✅ 刀具直径与范围期望一致；无"无刀具可用"报错
- ✅ 工序顺序符合工艺卡要求

### 7.3 无匹配刀具兜底策略

**双层策略**：

1. **第1层（刀具筛选）**：宽范围筛选，例如 `tool.Diameter >= 8.6 && <= 8.8`
2. **第2层（特征识别）**：精确孔径范围

**Fallback规则**：

```text
Rule Name: Fallback_ManualCheck
Priority: 100
OperationClass: (根据特征类型)
MWF: HOLE / POCKET / PLANAR_FACE
LWF: BLANK
```

**用途**：当专用规则无刀具匹配时，Fallback规则占位，避免特征漏加工。

---

## 8. 运维与持续改进

### 8.1 核心监控指标

| 指标 | 定义 | 目标值 |
|------|------|--------|
| 规则命中成功率 | 成功生成预期工序的特征数 / 总特征数 | ≥98% |
| 双命中冲突率 | 单特征命中多条互斥规则比例 | ≤1% |
| 无刀具失败率 | 因刀具条件不满足导致失败比例 | ≤2% |
| 人工兜底触发率 | ManualCheck 占位触发比例 | ≤3% |
| 回滚发生次数 | 单周回滚次数 | =0（目标） |

### 8.2 版本管理

**版本号规则**：
- **小版本递增** (v1.1 → v1.2)：规则范围、优先级或命名模板变化
- **大版本递增** (v1.x → v2.0)：跨模块结构调整（新增/删减模块）

**发布流程**：
1. 在验证库新增/修改规则，版本号递增
2. 执行最小回归样件测试
3. 检查"多规则重复命中"与"无刀具可用"故障
4. 通过后再同步生产库
5. 记录变更摘要与责任人

### 8.3 持续改进节奏 (PDCA)

- **Plan**：根据周报确定优先修复的范围冲突与刀具匹配问题
- **Do**：在验证库调整规则并执行最小回归
- **Check**：对比调整前后关键指标（命中率、冲突率、兜底率）
- **Act**：通过评审后发布生产库，并更新 Change Log

---

## 附录

### A. 标准工艺卡 (工序号+刀具+质量控制点)

| 工序号 | 工序内容 | 刀具建议 | 质量控制点 |
|--------|---------|---------|-----------|
| OP10 | 上料找正、装夹校准 | 百分表/寻边器 | 基准边与坐标系一致；装夹不翘曲 |
| OP20 | 基准面粗铣 (Face Rough) | 面铣刀 D40~D80 | 去除毛坯余量均匀；保留精加工余量 |
| OP30 | 基准面精铣 (Face Finish) | 面铣刀 D32~D63 | 平面度、厚度基准达标 |
| OP40 | 型腔/槽粗加工 | 立铣刀 D6~D20 | 不残留大块余料；拐角不过切 |
| OP50 | 型腔/槽精加工+清角 | 精铣刀+小径清角刀 D2~D10 | 轮廓尺寸与角部残料受控 |
| OP60 | 孔系定位钻 (Spot) | 定位钻 D10 | 孔位不漂移；后续钻孔入口无偏摆 |
| OP70 | 钻孔/扩孔 (Thread Bottom/Through) | 麻花钻 | 孔径范围命中正确；无漏孔 |
| OP80 | 铰孔/攻丝 (Ream/Tap) | 铰刀/丝锥 | Pin孔链路完整；螺纹通止规合格 |
| OP90 | 倒角去毛刺 (Chamfer/Deburr) | 倒角刀 D5~D25 | 倒角尺寸一致、无毛刺翻边 |
| OP100 | 终检与归档 | 检具/CMM | 关键尺寸、形位公差全检合格 |

**执行要求**：
- 工序顺序遵循"先基准、后特征；先粗、后精；先主体、后倒角"
- 若出现双命中或无刀具匹配，先启用 `Fallback_ManualCheck` 保产线
- 每次换版必须同步更新工艺卡版本、规则版本与发布签核页

### B. 快速参考表

**优先级分带总表**：

| 模块 | Priority区间 | 规则数 |
|------|-------------|--------|
| 01_Face_Milling | 1200~1299 | 4 |
| 02_Pocket_Slot | 2400~2499 | 6 |
| 03_Hole_Making | 2100~3399 | ~30 |
| 04_Chamfer | 3300~3399 | 4 |
| Fallback_ManualCheck | 100 | 1 |

**特征类型与MWF映射**：

| 特征类型 | MWF | LWF | 典型规则 |
|---------|-----|-----|---------|
| 平面 | PLANAR_FACE | BLANK | Face Milling |
| 型腔 | POCKET | BLANK | Pocket Rough/Finish |
| 槽 | SLOT | BLANK | Slot Milling |
| 孔 | HOLE | BLANK/STEP1HOLE | Drill/Ream |
| 沉孔 | COUNTERBORE | THRU_HOLE | Counterboring |
| 倒角 | CHAMFER | HOLE/EDGE | Chamfer Milling |

### C. 故障排查指南

**常见问题与解决方案**：

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 规则不命中 | 范围设置过窄 | 放宽Application Criteria范围 |
| 双命中冲突 | 优先级设计不合理 | 调整Priority或增加互斥条件 |
| 无刀具可用 | 刀具库无匹配规格 | 检查tool_database.dat或放宽Tool Attributes |
| 工序顺序错误 | MACHINING_RULE未正确设置 | 检查lwf.MACHINING_RULE条件 |
| 操作参数未生效 | 在Conditions中赋值复杂参数 | 迁移至Add-On附加工艺模板 |

**排查步骤**：
1. 保产线：启用 `ManualCheck` 占位，不让特征漏加工
2. 查语法与字段：确认模板分段、字段名可用
3. 查范围与优先级：先放宽命中，再回收精度
4. 留痕：更新 Change Log，记录 Owner/Date/Delta

### D. 参考资料

- `NX12MKE_v1.3_Backup.md` - 原始规范文档（含完整规则Conditions代码块）
- `tool_database.dat` - 刀具库定义（488KB）
- `holder_database.dat` - 刀柄库定义（22KB）
- `machining_knowledge.xml` - 原始知识库文件（9.8MB）
- `mke_extracted_rules.json` - 提取的工艺常量（28KB）
- `factory_plate_rules_complete_README.md` - 规则库导入指南
- `generate_rules_xml.py` - XML自动生成脚本

### E. 版本历史

| 版本 | 日期 | 修订说明 |
|------|------|---------|
| v2.0 | 2026-04-27 | 整合所有数据源，优化文档结构，补充完整规则清单与工艺常量 |
| v1.3 | 2026-03-15 | 按板类工艺顺序重排章节；统一主干编号；优化工艺卡版式 |
| v1.0 | 2026-03-01 | 初始版本，建立板类零件加工规则库框架 |

---

## F. XML 转换与插入指南

### F.1 从文本 Conditions 到 XML 的转换流程

**步骤概览**:
1. 从 `NX12MKE_v1.3_Backup.md` 复制规则的 Conditions 代码块
2. 使用 Python 脚本或手动转换为 XML 格式
3. 插入到 `machining_knowledge.xml` 的正确位置
4. 验证 XML 格式并在 NX 中测试

### F.2 使用 Python 脚本自动生成 XML

项目提供 `generate_rules_xml.py` 脚本自动化此过程。

**基本用法**:
```python
from generate_rules_xml import create_rule_element, insert_rule_to_library

# 定义规则
rule_data = {
    'name': '3.2_Thread_Bottom_D8p7',
    'operation_class': 'hole_making.DRILLING',
    'priority': 2250,
    'mwf': 'HOLE',
    'lwf': 'BLANK',
    'tool_class': 'TWIST_DRILL',
    'conditions': {
        'application': [
            'mwf.DIAMETER_1 >= 8.10',
            'mwf.DIAMETER_1 <= 8.98'
        ],
        'tool': [
            'tool.Diameter >= 8.65',
            'tool.Diameter <= 8.75'
        ],
        'operation': [
            'oper.name = "3.2_Thread_Bottom_D8p7"'
        ]
    }
}

# 生成并插入
xml_file = 'machining_knowledge.xml'
library_path = 'Factory_Plate_General/03_Hole_Making'
insert_rule_to_library(xml_file, library_path, rule_data)
```

### F.3 手动构造 XML 规则元素

**XML 结构模板**:
```xml
<Rule Name="3.2_Thread_Bottom_D8p7" Priority="2250" OperationClass="hole_making.DRILLING">
  <MoreWorkedFeature Type="HOLE"/>
  <LessWorkedFeature Type="BLANK"/>
  <ToolClass>TWIST_DRILL</ToolClass>
  <Conditions>
    <ApplicationCriteria>
      <Condition>mwf.DIAMETER_1 &gt;= 8.10</Condition>
      <Condition>mwf.DIAMETER_1 &lt;= 8.98</Condition>
    </ApplicationCriteria>
    <ToolAttributes>
      <Condition>tool.Diameter &gt;= 8.65</Condition>
      <Condition>tool.Diameter &lt;= 8.75</Condition>
    </ToolAttributes>
    <LessWorkedFeatureAttributes/>
    <OperationAttributes>
      <Assignment>oper.name = "3.2_Thread_Bottom_D8p7"</Assignment>
    </OperationAttributes>
  </Conditions>
</Rule>
```

**关键注意事项**:
- 特殊字符转义: `>=` → `&gt;=`, `<=` → `&lt;=`
- 保留所有 REM 注释和 `$$ Rule rejected` 行（在 XML 中作为注释）
- 文件编码必须为 UTF-8
- 确保同一库内规则名称唯一

### F.4 插入规则到现有 XML

**方法 1: 使用 Python (推荐)**
```python
import xml.etree.ElementTree as ET

# 加载 XML
tree = ET.parse('machining_knowledge.xml')
root = tree.getroot()

# 找到目标库节点
library = root.find('.//Library[@Name="03_Hole_Making"]')

# 创建新规则元素
new_rule = ET.SubElement(library, 'Rule')
new_rule.set('Name', 'New_Rule_Name')
new_rule.set('Priority', '2500')
# ... 设置其他属性和子元素

# 保存
tree.write('machining_knowledge_v2.xml', encoding='utf-8', xml_declaration=True)
```

**方法 2: 手动编辑**
1. 备份原文件: `Copy-Item machining_knowledge.xml machining_knowledge_backup.xml`
2. 用文本编辑器打开 XML
3. 定位到目标 `<Library>` 节点
4. 粘贴构造好的 `<Rule>` 元素
5. 保存并用验证脚本检查格式

### F.5 XML 格式验证

**验证脚本**:
```python
import xml.etree.ElementTree as ET

def validate_xml(filepath):
    try:
        tree = ET.parse(filepath)
        rules = tree.findall('.//Rule')
        print(f"✓ XML 格式正确，共 {len(rules)} 条规则")
        
        # 检查重复规则名
        names = [r.get('Name') for r in rules]
        duplicates = set([n for n in names if names.count(n) > 1])
        if duplicates:
            print(f"⚠ 发现重复规则名: {duplicates}")
        else:
            print("✓ 无重复规则名")
        
        return True
    except ET.ParseError as e:
        print(f"✗ XML 解析错误: {e}")
        return False

validate_xml('machining_knowledge.xml')
```

### F.6 常见问题与解决

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 规则详情空白 | XML 格式不符合 Schema | 对比导出规则，确保结构一致 |
| 导入失败 | 编码问题 | 使用 UTF-8 编码保存 |
| 规则不命中 | MWF/LWF 类型错误 | 检查特征类型映射表 |
| 双命中 | 优先级或窗口重叠 | 调整 Priority 或缩小窗口 |
| 无刀具可用 | 刀具库缺失 | 检查 tool_database.dat |

**详细规则代码**: 所有规则的完整 Conditions 代码块请参见 `NX12MKE_v1.3_Backup.md` 第 126-1180 行，可直接复制到 MKE 编辑器使用。

---

**文档维护**: 工艺工程团队  
**最后更新**: 2026-04-27  
**状态**: ✅ 生产就绪 (Production Ready)


---

## 附录A: 完整规则 Conditions 代码块

> **说明**: 以下所有规则的完整 Conditions 代码可直接复制到 MKE 编辑器使用。
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


---

## 附录B: XML 转换与插入指南

### B.1 从文本 Conditions 到 XML 的转换

**方法 1: 使用 Python 脚本自动化(推荐)**

项目提供 `generate_rules_xml.py` 脚本,可自动将规则定义转换为 XML 格式并插入到 `machining_knowledge.xml`。

**基本用法**:
```python
from generate_rules_xml import create_rule_element, insert_rule_to_library

rule_data = {
    'name': '3.2_Thread_Bottom_D8p7',
    'operation_class': 'hole_making.DRILLING',
    'priority': 2250,
    'mwf': 'HOLE',
    'lwf': 'BLANK',
    'tool_class': 'TWIST_DRILL',
    'conditions': {
        'application': ['mwf.DIAMETER_1 >= 8.10', 'mwf.DIAMETER_1 <= 8.98'],
        'tool': ['tool.Diameter >= 8.65', 'tool.Diameter <= 8.75'],
        'operation': ['oper.name = "3.2_Thread_Bottom_D8p7"']
    }
}

insert_rule_to_library('machining_knowledge.xml', 'Factory_Plate_General/03_Hole_Making', rule_data)
```

**方法 2: 手动构造 XML**

XML 结构模板:
```xml
<Rule Name="3.2_Thread_Bottom_D8p7" Priority="2250" OperationClass="hole_making.DRILLING">
  <MoreWorkedFeature Type="HOLE"/>
  <LessWorkedFeature Type="BLANK"/>
  <ToolClass>TWIST_DRILL</ToolClass>
  <Conditions>
    <ApplicationCriteria>
      <Condition>mwf.DIAMETER_1 &gt;= 8.10</Condition>
      <Condition>mwf.DIAMETER_1 &lt;= 8.98</Condition>
    </ApplicationCriteria>
    <ToolAttributes>
      <Condition>tool.Diameter &gt;= 8.65</Condition>
      <Condition>tool.Diameter &lt;= 8.75</Condition>
    </ToolAttributes>
    <LessWorkedFeatureAttributes/>
    <OperationAttributes>
      <Assignment>oper.name = "3.2_Thread_Bottom_D8p7"</Assignment>
    </OperationAttributes>
  </Conditions>
</Rule>
```

**关键注意事项**:
- 特殊字符转义: `>=` → `&gt;=`, `<=` → `&lt;=`
- 文件编码必须为 UTF-8
- 确保同一库内规则名称唯一
- 保留所有 REM 注释段落结构

### B.2 插入步骤

1. **备份原文件**: `Copy-Item machining_knowledge.xml machining_knowledge_backup.xml`
2. **定位插入位置**: 在 XML 中找到目标 `<Library>` 节点
3. **插入规则元素**: 粘贴构造好的 `<Rule>` 元素
4. **验证格式**: 使用 Python 的 `xml.etree.ElementTree` 验证
5. **在 NX 中测试**: 加载规则库验证是否正确识别

### B.3 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 规则详情空白 | XML 格式不符合 Schema | 对比导出规则,确保结构一致 |
| 导入失败 | 编码问题 | 使用 UTF-8 编码保存 |
| 规则不命中 | MWF/LWF 类型错误 | 检查特征类型映射表 |
| 双命中 | 优先级或窗口重叠 | 调整 Priority 或缩小窗口 |

---

**文档维护**: 工艺工程团队  
**最后更新**: 2026-04-28  
**状态**: ✅ 生产就绪 (Production Ready)
