# 板类零件自动化加工规则库使用说明

## 文件说明

完整的规则库XML文件(`factory_plate_rules_complete.xml`)包含以下模块:

### 01_Face_Milling (面加工库) - Priority: 1200~1299
- 1.1_Face_Top_Rough (顶面粗铣)
- 1.2_Face_Top_Finish (顶面精铣)  
- 1.3_Face_Bottom_Finish (底面精铣)
- 1.4_Face_ThinWall_LightCut (薄壁轻切)

### 02_Pocket_Slot (型腔与槽库) - Priority: 2400~2499
- 2.1_Pocket_Rough_General (型腔粗加工)
- 2.2_Pocket_Finish_Wall (型腔壁精加工)
- 2.3_Pocket_Finish_Floor (型腔底精加工)
- 2.4_Slot_Open_Rough (开通槽粗加工)
- 2.5_Slot_Closed_Finish (闭槽精加工)
- 2.6_Corner_Rest_Mill (清角加工)

### 03_Hole_Making (孔加工库) - Priority: 2100~3399

#### 3.1_Spot (定位钻) - Priority: 1100
- 3.1_Spot_D10 (D10中心钻，适用孔径3-22mm)

#### 3.2_Thread_Bottom (螺纹底孔) - Priority: 2210~2280
- 3.2_Thread_Bottom_D3p4 (M4底孔，窗口[3.10,3.50])
- 3.2_Thread_Bottom_D4p3 (M5底孔，窗口[4.10,4.50])
- 3.2_Thread_Bottom_D5p2 (M6底孔，窗口[5.10,5.50])
- 3.2_Thread_Bottom_D6p9 (M8底孔，窗口[6.50,6.98])
- 3.2_Thread_Bottom_D8p7 (M10底孔，窗口[8.10,8.98])
- 3.2_Thread_Bottom_D10p5 (M12底孔，窗口[10.10,10.80])
- 3.2_Thread_Bottom_D14p3 (M16底孔，窗口[13.50,14.50])
- 3.2_Thread_Bottom_D17p8 (M20底孔，窗口[17.10,17.98])

#### 3.3_Thread_Through (螺纹过孔) - Priority: 2310~2350
- 3.3_Thread_Through_D9 (窗口[8.98,9.02])
- 3.3_Thread_Through_D11 (窗口[10.98,11.02])
- 3.3_Thread_Through_D13 (窗口[12.98,13.02])
- 3.3_Thread_Through_D17 (窗口[16.98,17.02])
- 3.3_Thread_Through_D21 (窗口[20.98,21.02])

#### 3.4_Pin_Hole (销孔) - Priority: 2110~3180
预钻孔 (Pre):
- 3.4_Pin_Pre_D4 (窗口[3.68,3.72], 刀具D3.7)
- 3.4_Pin_Pre_D5 (窗口[4.68,4.72], 刀具D4.7)
- 3.4_Pin_Pre_D6 (窗口[5.68,5.72], 刀具D5.7)
- 3.4_Pin_Pre_D8 (窗口[7.68,7.72], 刀具D7.7)
- 3.4_Pin_Pre_D10 (窗口[9.68,9.72], 刀具D9.7)
- 3.4_Pin_Pre_D12 (窗口[11.68,11.72], 刀具D11.7)
- 3.4_Pin_Pre_D16 (窗口[15.68,15.72], 刀具D15.7)
- 3.4_Pin_Pre_D20 (窗口[19.68,19.72], 刀具D19.7)

铰孔 (Ream):
- 3.4_Pin_Ream_D4 (窗口[3.98,4.02], 刀具D4.0)
- 3.4_Pin_Ream_D5 (窗口[4.98,5.02], 刀具D5.0)
- 3.4_Pin_Ream_D6 (窗口[5.98,6.02], 刀具D6.0)
- 3.4_Pin_Ream_D8 (窗口[7.98,8.02], 刀具D8.0)
- 3.4_Pin_Ream_D10 (窗口[9.98,10.02], 刀具D10.0)
- 3.4_Pin_Ream_D12 (窗口[11.98,12.02], 刀具D12.0)
- 3.4_Pin_Ream_D16 (窗口[15.98,16.02], 刀具D16.0)
- 3.4_Pin_Ream_D20 (窗口[19.98,20.02], 刀具D20.0)

#### 3.5_Large_Hole (大孔) - Priority: 3200+
- 适用于孔径>21mm的孔，建议使用孔铣(Hole Milling)策略

### 04_Chamfer (倒角库) - Priority: 3300~3399
- 4.1_Hole_Chamfer_C0p5 (孔倒角C0.5，孔径[3,20])
- 4.2_Hole_Chamfer_C1p0 (孔倒角C1.0，孔径[6,30])
- 4.3_Outer_Chamfer_General (外轮廓倒角)
- 4.4_Deburr_Light_Pass (去毛刺轻加工)

## 导入步骤

1. 打开NX Machining Knowledge Editor
2. 在规则树根节点右键 → Import
3. 选择`factory_plate_rules_complete.xml`
4. 导入后验证规则树结构:
   - Factory_Plate_General
     - 01_Face_Milling (4条规则)
     - 02_Pocket_Slot (6条规则)
     - 03_Hole_Making
       - 3.1_Spot (1条规则)
       - 3.2_Thread_Bottom (8条规则)
       - 3.3_Thread_Through (5条规则)
       - 3.4_Pin_Hole (16条规则)
       - 3.5_Large_Hole (按需添加)
     - 04_Chamfer (4条规则)

## 规则统计

- **总计规则数**: 约50条
- **模块数**: 4个主模块，孔加工库含5个子模块
- **优先级范围**: 1100 ~ 3399
- **规则命名规范**: 模块_工艺_特征_范围_刀具_R版本

## 注意事项

1. **优先级设计**:
   - 同一特征类型下，优先级越高越先尝试
   - Ream优先级必须高于对应Pre (确保工序链路正确)
   - Fallback规则使用最低优先级

2. **范围互斥**:
   - Thread Bottom与Thread Through范围互斥，避免同一孔双命中
   - Pin孔Pre与Ream成对存在，命名仅后缀不同

3. **刀具匹配**:
   - Tool Attributes窗口应略宽于目标值(约±0.05mm)
   - 确保刀具库中有对应规格的刀具

4. **验证测试**:
   - 导入后执行最小回归测试(面、口袋、槽、孔、倒角各至少1组)
   - 检查是否出现"多规则重复命中"与"无刀具可用"故障

## 参考资料

- NX12MKE.md - 项目规范文档
- tool_database.dat - 刀具库定义
- holder_database.dat - 刀柄库定义
- machining_knowledge.xml - 原始知识库文件
- mke_extracted_rules.json - 提取的工艺常量

## 版本历史

- V1.0 (2026-04-27): 初始版本，包含完整的板类零件加工规则
