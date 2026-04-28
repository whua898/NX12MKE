# 规则库XML文件生成与导入指南

**版本**: v2.0  
**更新日期**: 2026-04-27  
**适用软件**: Siemens NX 12.0 Machining Knowledge Editor

---

## 📋 概述

本文档说明如何使用Python脚本自动生成NX12 MKE规则库XML文件，并将其导入到Machining Knowledge Editor中。

---

## 🔧 生成规则库XML文件

### 方法一：使用Python脚本（推荐）

#### 前置条件
- Python 3.6+ 已安装
- 项目根目录下有 `generate_rules_xml.py` 脚本

#### 执行步骤

1. **打开终端/命令行**
   ```bash
   cd D:\Users\wh898\PycharmProjects\NX12MKE
   ```

2. **运行生成脚本**
   ```bash
   python generate_rules_xml.py
   ```

3. **查看输出**
   ```
   ============================================================
     NX12 MKE 板类零件自动化加工规则库生成器 v2.0
   ============================================================

   ✅ 规则库XML文件已生成: factory_plate_rules_complete.xml
   📊 文件大小: 34.06 KB
   📅 生成时间: 2026-04-28 07:00:19

   📖 使用说明:
     1. 打开 NX Machining Knowledge Editor
     2. 在规则树根节点右键 → Import
     3. 选择生成的 factory_plate_rules_complete.xml
     4. 导入后验证规则树结构

   ✨ 完成！
   ```

4. **验证生成结果**
   - 检查项目根目录是否生成 `factory_plate_rules_complete.xml`
   - 文件大小约 34KB
   - 包含约870行XML代码

---

## 📥 导入规则库到MKE

### 步骤1：打开Machining Knowledge Editor

1. 启动 Siemens NX 12.0
2. 进入加工模块（Manufacturing）
3. 点击菜单：**工具(Tools)** → **加工知识编辑器(Machining Knowledge Editor)**

### 步骤2：导入XML文件

1. 在MKE界面左侧的**规则树(Rule Tree)**中
2. 右键点击**根节点(Root)**
3. 选择 **导入(Import)**
4. 浏览并选择 `factory_plate_rules_complete.xml`
5. 点击 **打开(Open)**

### 步骤3：验证导入结果

导入成功后，规则树应显示以下结构：

```
Factory_Plate_General (板类通用库)
├─ 01_Face_Milling (面加工库) [4条规则]
│   ├─ 1.1_Face_Top_Rough
│   ├─ 1.2_Face_Top_Finish
│   ├─ 1.3_Face_Bottom_Finish
│   └─ 1.4_Face_ThinWall_LightCut
├─ 02_Pocket_Slot (型腔与槽库) [6条规则]
│   ├─ 2.1_Pocket_Rough_General
│   ├─ 2.2_Pocket_Finish_Wall
│   ├─ 2.3_Pocket_Finish_Floor
│   ├─ 2.4_Slot_Open_Rough
│   ├─ 2.5_Slot_Closed_Finish
│   └─ 2.6_Corner_Rest_Mill
├─ 03_Hole_Making (孔加工库) [~30条规则]
│   ├─ 3.1_Spot (定位钻) [1条规则]
│   ├─ 3.2_Thread_Bottom (螺纹底孔) [8条规则]
│   ├─ 3.3_Thread_Through (螺纹过孔) [5条规则]
│   ├─ 3.4_Pin_Hole (销孔) [16条规则]
│   │   ├─ 3.4_Pin_Pre (预钻孔) [8条规则]
│   │   └─ 3.4_Pin_Ream (铰孔) [8条规则]
│   └─ 3.5_Large_Hole (大孔) [按需添加]
└─ 04_Chamfer (倒角库) [4条规则]
    ├─ 4.1_Hole_Chamfer_C0p5
    ├─ 4.2_Hole_Chamfer_C1p0
    ├─ 4.3_Outer_Chamfer_General
    └─ 4.4_Deburr_Light_Pass
```

**总计**: 约50条规则

---

## ✅ 导入后验证测试

### 测试1：规则数量检查

- [ ] 01_Face_Milling: 4条规则
- [ ] 02_Pocket_Slot: 6条规则
- [ ] 03_Hole_Making: ~30条规则
- [ ] 04_Chamfer: 4条规则
- [ ] **总计**: 约50条规则

### 测试2：优先级检查

随机抽查几条规则，确认Priority值正确：
- [ ] 1.1_Face_Top_Rough: Priority = 1210
- [ ] 3.2_Thread_Bottom_D8p7: Priority = 2250
- [ ] 3.4_Pin_Ream_D10: Priority = 3150
- [ ] 4.1_Hole_Chamfer_C0p5: Priority = 3310

### 测试3：工序链路检查

检查销孔铰孔规则的LWF条件：
- [ ] 打开 3.4_Pin_Ream_D10 规则
- [ ] 查看 Conditions → LessWorkedFeatureAttributes
- [ ] 确认包含: `lwf.MACHINING_RULE = "TWIST_DRILL"`

### 测试4：实际应用测试

1. 打开一个板类零件模型
2. 应用基于特征加工(FBM)
3. 检查是否自动识别以下特征：
   - [ ] 平面 → 生成面铣工序
   - [ ] 型腔 → 生成型腔铣工序
   - [ ] M8螺纹孔 → 生成底孔钻削工序
   - [ ] Ø10销孔 → 生成预钻+铰孔工序

---

## ⚠️ 常见问题与解决

### 问题1：导入失败，提示"XML格式错误"

**原因**: XML文件可能在传输过程中损坏

**解决**:
1. 重新运行 `python generate_rules_xml.py` 生成新文件
2. 确保使用UTF-8编码保存
3. 检查XML文件开头是否有 `<?xml version="1.0" encoding="utf-8"?>`

### 问题2：规则导入后不生效

**原因**: 刀具库中没有匹配的刀具规格

**解决**:
1. 检查 `tool_database.dat` 中是否有对应直径的刀具
2. 在MKE中检查规则的 ToolClass 是否与刀具库匹配
3. 调整规则的 Tool Attributes 窗口范围

### 问题3：同一特征命中多条规则

**原因**: 优先级设计不合理或窗口重叠

**解决**:
1. 检查冲突规则的Priority值
2. 确保窄范围规则优先级高于宽范围规则
3. 调整Application Criteria窗口，避免重叠

### 问题4：销孔铰孔规则不触发

**原因**: LWF条件未满足（缺少预钻工序）

**解决**:
1. 确认预钻规则已正确配置
2. 检查预钻规则的 MWF.MACHINING_RULE 是否设置为 "TWIST_DRILL"
3. 确保工序顺序正确：先预钻，后铰孔

---

## 🔄 更新与维护

### 修改规则后重新生成

1. 编辑 `generate_rules_xml.py` 中的规则数据
2. 重新运行脚本: `python generate_rules_xml.py`
3. 在MKE中删除旧规则库
4. 导入新生成的XML文件

### 版本管理建议

- 每次修改后递增版本号（如 v2.0 → v2.1）
- 保留历史版本的XML文件备份
- 记录变更日志（Change Log）

### 备份策略

```bash
# 备份当前版本
copy factory_plate_rules_complete.xml factory_plate_rules_complete_v2.0_backup.xml

# 生成新版本
python generate_rules_xml.py

# 验证新版本
# ... 执行验证测试 ...
```

---

## 📚 相关文档

- [NX12MKE.md](../NX12MKE.md) - 主规范文档
- [factory_plate_rules_complete_README.md](../factory_plate_rules_complete_README.md) - 规则库详细说明
- [docs/README.md](../docs/README.md) - 文档报告目录说明

---

## 📞 技术支持

如遇问题，请参考：
1. NX官方帮助文档: Machining Knowledge Editor
2. 项目文档: `docs/` 目录下的相关报告
3. 工艺工程团队

---

**最后更新**: 2026-04-27  
**维护人**: 工艺工程团队  
**状态**: ✅ 生产就绪
