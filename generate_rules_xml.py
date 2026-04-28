#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NX12 MKE 板类零件自动化加工规则库生成器

功能：根据规则定义自动生成板类零件加工规则库XML文件（factory_plate_rules_complete.xml）
版本：v2.0
日期：2026-04-27
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime


class RuleGenerator:
    """MKE规则库生成器"""
    
    def __init__(self):
        self.rules = []
        self.rule_library = None
        
    def create_rule_library(self):
        """创建规则库根节点"""
        self.rule_library = ET.Element("MachiningRuleLibrary")
        self.rule_library.set("Name", "Factory_Plate_General")
        # Use a unique ExternalId to avoid conflicts
        self.rule_library.set("ExternalId", "#Factory_Plate_General_Lib")
        self.rule_library.set("Description", "板类零件通用加工规则库 v2.0")
        
    def add_face_milling_rules(self):
        """添加面加工规则 (01_Face_Milling)"""
        parent = ET.SubElement(self.rule_library, "MachiningRuleLibrary")
        parent.set("Name", "01_Face_Milling")
        parent.set("Description", "面加工库")
        
        rules_data = [
            {
                "name": "1.1_Face_Top_Rough",
                "priority": "1210",
                "op_class": "face_milling.FACE_MILLING",
                "mwf": "PLANAR_FACE",
                "lwf": "BLANK",
                "tool_class": "FACE_MILL",
                "criteria": [
                    ("mwf.AREA", ">=", "400.0"),
                    ("mwf.AREA", "<=", "200000.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "40.0"),
                    ("tool.Diameter", "<=", "80.0")
                ]
            },
            {
                "name": "1.2_Face_Top_Finish",
                "priority": "1220",
                "op_class": "face_milling.FACE_MILLING",
                "mwf": "PLANAR_FACE",
                "lwf": "BLANK",
                "tool_class": "FACE_MILL",
                "criteria": [
                    ("mwf.AREA", ">=", "300.0"),
                    ("mwf.AREA", "<=", "200000.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "32.0"),
                    ("tool.Diameter", "<=", "63.0")
                ]
            },
            {
                "name": "1.3_Face_Bottom_Finish",
                "priority": "1230",
                "op_class": "face_milling.FACE_MILLING",
                "mwf": "PLANAR_FACE",
                "lwf": "BLANK",
                "tool_class": "FACE_MILL",
                "criteria": [
                    ("mwf.AREA", ">=", "300.0"),
                    ("mwf.AREA", "<=", "200000.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "32.0"),
                    ("tool.Diameter", "<=", "63.0")
                ]
            },
            {
                "name": "1.4_Face_ThinWall_LightCut",
                "priority": "1240",
                "op_class": "face_milling.FACE_MILLING",
                "mwf": "PLANAR_FACE",
                "lwf": "BLANK",
                "tool_class": "FACE_MILL",
                "criteria": [
                    ("mwf.AREA", ">=", "100.0"),
                    ("mwf.AREA", "<=", "50000.0"),
                    ("mwf.THICKNESS", "<=", "8.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "16.0"),
                    ("tool.Diameter", "<=", "40.0")
                ]
            }
        ]
        
        for rule_data in rules_data:
            self._create_rule(parent, rule_data)
            
    def add_pocket_slot_rules(self):
        """添加型腔与槽规则 (02_Pocket_Slot)"""
        parent = ET.SubElement(self.rule_library, "MachiningRuleLibrary")
        parent.set("Name", "02_Pocket_Slot")
        parent.set("Description", "型腔与槽库")
        
        rules_data = [
            {
                "name": "2.1_Pocket_Rough_General",
                "priority": "2410",
                "op_class": "cavity_milling.CAVITY_MILL",
                "mwf": "POCKET",
                "lwf": "BLANK",
                "tool_class": "END_MILL",
                "criteria": [
                    ("mwf.DEPTH", ">=", "1.0"),
                    ("mwf.DEPTH", "<=", "40.0"),
                    ("mwf.R_min", ">=", "2.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "8.0"),
                    ("tool.Diameter", "<=", "20.0")
                ]
            },
            {
                "name": "2.2_Pocket_Finish_Wall",
                "priority": "2420",
                "op_class": "planar_milling.PROFILE",
                "mwf": "POCKET",
                "lwf": "BLANK",
                "tool_class": "END_MILL",
                "criteria": [
                    ("mwf.DEPTH", ">=", "1.0"),
                    ("mwf.DEPTH", "<=", "40.0"),
                    ("mwf.WALL_ANGLE", "<=", "2.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "6.0"),
                    ("tool.Diameter", "<=", "16.0")
                ]
            },
            {
                "name": "2.3_Pocket_Finish_Floor",
                "priority": "2430",
                "op_class": "planar_milling.PLANAR_MILL",
                "mwf": "POCKET",
                "lwf": "BLANK",
                "tool_class": "END_MILL",
                "criteria": [
                    ("mwf.DEPTH", ">=", "1.0"),
                    ("mwf.DEPTH", "<=", "40.0"),
                    ("mwf.BOTTOM_R", "<=", "1.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "6.0"),
                    ("tool.Diameter", "<=", "20.0")
                ]
            },
            {
                "name": "2.4_Slot_Open_Rough",
                "priority": "2440",
                "op_class": "slot_milling.SLOT_MILL",
                "mwf": "SLOT",
                "lwf": "BLANK",
                "tool_class": "END_MILL",
                "criteria": [
                    ("mwf.WIDTH", ">=", "6.0"),
                    ("mwf.WIDTH", "<=", "24.0"),
                    ("mwf.DEPTH", "<=", "20.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "5.0"),
                    ("tool.Diameter", "<=", "16.0")
                ]
            },
            {
                "name": "2.5_Slot_Closed_Finish",
                "priority": "2450",
                "op_class": "slot_milling.SLOT_MILL",
                "mwf": "SLOT",
                "lwf": "BLANK",
                "tool_class": "END_MILL",
                "criteria": [
                    ("mwf.WIDTH", ">=", "4.0"),
                    ("mwf.WIDTH", "<=", "16.0"),
                    ("mwf.DEPTH", "<=", "20.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "3.0"),
                    ("tool.Diameter", "<=", "10.0")
                ]
            },
            {
                "name": "2.6_Corner_Rest_Mill",
                "priority": "2460",
                "op_class": "rest_milling.REST_MILL",
                "mwf": "POCKET",
                "lwf": "BLANK",
                "tool_class": "END_MILL",
                "criteria": [
                    ("mwf.R_min", "<=", "2.0"),
                    ("mwf.DEPTH", "<=", "30.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "2.0"),
                    ("tool.Diameter", "<=", "8.0")
                ]
            }
        ]
        
        for rule_data in rules_data:
            self._create_rule(parent, rule_data)
            
    def add_hole_making_rules(self):
        """添加孔加工规则 (03_Hole_Making)"""
        parent = ET.SubElement(self.rule_library, "MachiningRuleLibrary")
        parent.set("Name", "03_Hole_Making")
        parent.set("Description", "孔加工库")
        
        # 3.1 Spot Drill
        spot_lib = ET.SubElement(parent, "MachiningRuleLibrary")
        spot_lib.set("Name", "3.1_Spot")
        spot_lib.set("Description", "定位钻")
        
        spot_rule = {
            "name": "3.1_Spot_D10",
            "priority": "1100",
            "op_class": "hole_making.SPOT_DRILLING",
            "mwf": "HOLE",
            "lwf": "BLANK",
            "tool_class": "CENTER_DRILL",
            "criteria": [
                ("mwf.DIAMETER_1", ">=", "3.0"),
                ("mwf.DIAMETER_1", "<=", "22.0")
            ],
            "tool_attrs": [
                ("tool.Diameter", "=", "10.0")
            ]
        }
        self._create_rule(spot_lib, spot_rule)
        
        # 3.2 Thread Bottom Holes
        thread_bottom_lib = ET.SubElement(parent, "MachiningRuleLibrary")
        thread_bottom_lib.set("Name", "3.2_Thread_Bottom")
        thread_bottom_lib.set("Description", "螺纹底孔")
        
        thread_bottom_data = [
            ("3.2_Thread_Bottom_D3p4", "2210", 3.4, 3.10, 3.50),
            ("3.2_Thread_Bottom_D4p3", "2220", 4.3, 4.10, 4.50),
            ("3.2_Thread_Bottom_D5p2", "2230", 5.2, 5.10, 5.50),
            ("3.2_Thread_Bottom_D6p9", "2240", 6.9, 6.50, 6.98),
            ("3.2_Thread_Bottom_D8p7", "2250", 8.7, 8.10, 8.98),
            ("3.2_Thread_Bottom_D10p5", "2260", 10.5, 10.10, 10.80),
            ("3.2_Thread_Bottom_D14p3", "2270", 14.3, 13.50, 14.50),
            ("3.2_Thread_Bottom_D17p8", "2280", 17.8, 17.10, 17.98),
        ]
        
        for name, priority, drill_dia, dia_min, dia_max in thread_bottom_data:
            rule = {
                "name": name,
                "priority": priority,
                "op_class": "hole_making.DRILLING",
                "mwf": "HOLE",
                "lwf": "BLANK",
                "tool_class": "TWIST_DRILL",
                "criteria": [
                    ("mwf.DIAMETER_1", ">=", str(dia_min)),
                    ("mwf.DIAMETER_1", "<=", str(dia_max))
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", str(drill_dia - 0.05)),
                    ("tool.Diameter", "<=", str(drill_dia + 0.05))
                ]
            }
            self._create_rule(thread_bottom_lib, rule)
            
        # 3.3 Thread Through Holes
        thread_through_lib = ET.SubElement(parent, "MachiningRuleLibrary")
        thread_through_lib.set("Name", "3.3_Thread_Through")
        thread_through_lib.set("Description", "螺纹过孔")
        
        thread_through_data = [
            ("3.3_Thread_Through_D9", "2310", 9.0, 8.98, 9.02),
            ("3.3_Thread_Through_D11", "2320", 11.0, 10.98, 11.02),
            ("3.3_Thread_Through_D13", "2330", 13.0, 12.98, 13.02),
            ("3.3_Thread_Through_D17", "2340", 17.0, 16.98, 17.02),
            ("3.3_Thread_Through_D21", "2350", 21.0, 20.98, 21.02),
        ]
        
        for name, priority, drill_dia, dia_min, dia_max in thread_through_data:
            rule = {
                "name": name,
                "priority": priority,
                "op_class": "hole_making.DRILLING",
                "mwf": "HOLE",
                "lwf": "STEP1HOLE",
                "tool_class": "TWIST_DRILL",
                "criteria": [
                    ("mwf.DIAMETER_1", ">=", str(dia_min)),
                    ("mwf.DIAMETER_1", "<=", str(dia_max))
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", str(drill_dia - 0.05)),
                    ("tool.Diameter", "<=", str(drill_dia + 0.05))
                ]
            }
            self._create_rule(thread_through_lib, rule)
            
        # 3.4 Pin Holes (Pre-Drill + Ream)
        pin_hole_lib = ET.SubElement(parent, "MachiningRuleLibrary")
        pin_hole_lib.set("Name", "3.4_Pin_Hole")
        pin_hole_lib.set("Description", "销孔")
        
        # Pre-Drill rules
        pre_drill_lib = ET.SubElement(pin_hole_lib, "MachiningRuleLibrary")
        pre_drill_lib.set("Name", "3.4_Pin_Pre")
        pre_drill_lib.set("Description", "预钻孔")
        
        pin_pre_data = [
            ("3.4_Pin_Pre_D4", "2110", 4.0, 3.7, 3.68, 3.72),
            ("3.4_Pin_Pre_D5", "2120", 5.0, 4.7, 4.68, 4.72),
            ("3.4_Pin_Pre_D6", "2130", 6.0, 5.7, 5.68, 5.72),
            ("3.4_Pin_Pre_D8", "2140", 8.0, 7.7, 7.68, 7.72),
            ("3.4_Pin_Pre_D10", "2150", 10.0, 9.7, 9.68, 9.72),
            ("3.4_Pin_Pre_D12", "2160", 12.0, 11.7, 11.68, 11.72),
            ("3.4_Pin_Pre_D16", "2170", 16.0, 15.7, 15.68, 15.72),
            ("3.4_Pin_Pre_D20", "2180", 20.0, 19.7, 19.68, 19.72),
        ]
        
        for name, priority, final_dia, pre_dia, dia_min, dia_max in pin_pre_data:
            rule = {
                "name": name,
                "priority": priority,
                "op_class": "hole_making.DRILLING",
                "mwf": "HOLE",
                "lwf": "BLANK",
                "tool_class": "TWIST_DRILL",
                "criteria": [
                    ("mwf.DIAMETER_1", ">=", str(dia_min)),
                    ("mwf.DIAMETER_1", "<=", str(dia_max))
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", str(pre_dia - 0.05)),
                    ("tool.Diameter", "<=", str(pre_dia + 0.05))
                ]
            }
            self._create_rule(pre_drill_lib, rule)
            
        # Ream rules
        ream_lib = ET.SubElement(pin_hole_lib, "MachiningRuleLibrary")
        ream_lib.set("Name", "3.4_Pin_Ream")
        ream_lib.set("Description", "铰孔")
        
        pin_ream_data = [
            ("3.4_Pin_Ream_D4", "3110", 4.0, 3.98, 4.02),
            ("3.4_Pin_Ream_D5", "3120", 5.0, 4.98, 5.02),
            ("3.4_Pin_Ream_D6", "3130", 6.0, 5.98, 6.02),
            ("3.4_Pin_Ream_D8", "3140", 8.0, 7.98, 8.02),
            ("3.4_Pin_Ream_D10", "3150", 10.0, 9.98, 10.02),
            ("3.4_Pin_Ream_D12", "3160", 12.0, 11.98, 12.02),
            ("3.4_Pin_Ream_D16", "3170", 16.0, 15.98, 16.02),
            ("3.4_Pin_Ream_D20", "3180", 20.0, 19.98, 20.02),
        ]
        
        for name, priority, final_dia, dia_min, dia_max in pin_ream_data:
            rule = {
                "name": name,
                "priority": priority,
                "op_class": "hole_making.REAMING",
                "mwf": "HOLE",
                "lwf": "BLANK",
                "tool_class": "REAMER",
                "criteria": [
                    ("mwf.DIAMETER_1", ">=", str(dia_min)),
                    ("mwf.DIAMETER_1", "<=", str(dia_max)),
                    ("lwf.MACHINING_RULE", "=", "TWIST_DRILL")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", str(final_dia - 0.05)),
                    ("tool.Diameter", "<=", str(final_dia + 0.05))
                ]
            }
            self._create_rule(ream_lib, rule)
            
    def add_chamfer_rules(self):
        """添加倒角规则 (04_Chamfer)"""
        parent = ET.SubElement(self.rule_library, "MachiningRuleLibrary")
        parent.set("Name", "04_Chamfer")
        parent.set("Description", "倒角库")
        
        rules_data = [
            {
                "name": "4.1_Hole_Chamfer_C0p5",
                "priority": "3310",
                "op_class": "mill_planar.CHAMFER_MILLING",
                "mwf": "HOLE",
                "lwf": "BLANK",
                "tool_class": "CHAMFER_MILL",
                "criteria": [
                    ("mwf.DIAMETER_1", ">=", "3.0"),
                    ("mwf.DIAMETER_1", "<=", "20.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "5.0"),
                    ("tool.Diameter", "<=", "16.0")
                ]
            },
            {
                "name": "4.2_Hole_Chamfer_C1p0",
                "priority": "3320",
                "op_class": "mill_planar.CHAMFER_MILLING",
                "mwf": "HOLE",
                "lwf": "BLANK",
                "tool_class": "CHAMFER_MILL",
                "criteria": [
                    ("mwf.DIAMETER_1", ">=", "6.0"),
                    ("mwf.DIAMETER_1", "<=", "30.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "8.0"),
                    ("tool.Diameter", "<=", "20.0")
                ]
            },
            {
                "name": "4.3_Outer_Chamfer_General",
                "priority": "3330",
                "op_class": "mill_planar.CHAMFER_MILLING",
                "mwf": "EDGE",
                "lwf": "BLANK",
                "tool_class": "CHAMFER_MILL",
                "criteria": [
                    ("mwf.LENGTH", ">=", "20.0"),
                    ("mwf.LENGTH", "<=", "5000.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "8.0"),
                    ("tool.Diameter", "<=", "25.0")
                ]
            },
            {
                "name": "4.4_Deburr_Light_Pass",
                "priority": "3340",
                "op_class": "mill_planar.CHAMFER_MILLING",
                "mwf": "EDGE",
                "lwf": "BLANK",
                "tool_class": "CHAMFER_MILL",
                "criteria": [
                    ("mwf.LENGTH", ">=", "5.0"),
                    ("mwf.LENGTH", "<=", "8000.0")
                ],
                "tool_attrs": [
                    ("tool.Diameter", ">=", "6.0"),
                    ("tool.Diameter", "<=", "20.0")
                ]
            }
        ]
        
        for rule_data in rules_data:
            self._create_rule(parent, rule_data)
            
    def _create_rule(self, parent, rule_data):
        """创建单个规则"""
        rule = ET.SubElement(parent, "MachiningRule")
        rule.set("Name", rule_data["name"])
        rule.set("ExternalId", f"#{rule_data['name']}")
        rule.set("Priority", rule_data["priority"])
        rule.set("OperationClass", rule_data["op_class"])
        rule.set("MWF", rule_data["mwf"])
        rule.set("LWF", rule_data["lwf"])
        rule.set("ToolClass", rule_data["tool_class"])
        rule.set("Description", rule_data.get("description", ""))
        
        # Conditions
        conditions = ET.SubElement(rule, "Conditions")
        
        # Application Criteria - use CDATA or proper formatting
        app_criteria = ET.SubElement(conditions, "ApplicationCriteria")
        criteria_lines = []
        criteria_lines.append("REM Application Criteria")
        for field, op, value in rule_data["criteria"]:
            criteria_lines.append(f"{field} {op} {value}")
        criteria_lines.append("")
        criteria_lines.append("$$ Rule rejected because condition FALSE")
        app_criteria.text = "\n".join(criteria_lines)
        
        # Tool Attributes
        tool_attrs = ET.SubElement(conditions, "ToolAttributes")
        tool_lines = ["REM Tool Attributes"]
        for field, op, value in rule_data["tool_attrs"]:
            tool_lines.append(f"{field} {op} {value}")
        tool_attrs.text = "\n".join(tool_lines)
        
        # Less Worked Feature Attributes
        lwf_attrs = ET.SubElement(conditions, "LessWorkedFeatureAttributes")
        lwf_attrs.text = "REM Less Worked Feature Attributes"
        
        # Operation Attributes
        oper_attrs = ET.SubElement(conditions, "OperationAttributes")
        oper_lines = [
            "REM Operation Attributes",
            f'oper.name = "{rule_data["name"]}"',
            f'oper.description = "{rule_data.get("description", rule_data["name"])}"'
        ]
        oper_attrs.text = "\n".join(oper_lines)
        
    def generate_xml(self, output_file="factory_plate_rules_complete.xml"):
        """生成 XML 文件"""
        if not self.rule_library:
            self.create_rule_library()
            
        # Add all rules
        self.add_face_milling_rules()
        self.add_pocket_slot_rules()
        self.add_hole_making_rules()
        self.add_chamfer_rules()
        
        # Wrap in standard NX Data/Objects structure
        root = ET.Element("Data")
        root.set("PpXmlVer", "1.0")
        
        # DO NOT include Customization section - it causes Class conflicts
        # NX MKE already has these classes defined
        
        objects = ET.SubElement(root, "Objects")
        
        # Add collections reference - point to OOTB root
        collections = ET.SubElement(self.rule_library, "collections")
        ET.SubElement(collections, "item").text = "#OOTB_EnvironmentLibraryEnvRuleRoot"
        
        # Add NodeInfo with Id
        node_info = ET.Element("NodeInfo")
        ET.SubElement(node_info, "Id").text = "819"
        self.rule_library.insert(0, node_info)
        
        # Add children references for sub-libraries ONLY (not individual rules)
        children = ET.SubElement(self.rule_library, "children")
        for lib in self.rule_library.findall("MachiningRuleLibrary"):
            ext_id = lib.get("ExternalId", "")
            if ext_id:
                ET.SubElement(children, "item").text = ext_id
        
        objects.append(self.rule_library)
        
        # Pretty print XML
        rough_string = ET.tostring(root, encoding='utf-8', xml_declaration=False)
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8')
        
        # Write to file
        with open(output_file, 'wb') as f:
            f.write(pretty_xml)
            
        print(f"✅ 规则库 XML 文件已生成：{output_file}")
        print(f"📊 文件大小：{os.path.getsize(output_file) / 1024:.2f} KB")
        print(f" 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """主函数"""
    print("=" * 60)
    print("  NX12 MKE 板类零件自动化加工规则库生成器 v2.0")
    print("=" * 60)
    print()
    
    generator = RuleGenerator()
    generator.generate_xml()
    
    print()
    print("📖 使用说明:")
    print("  1. 打开 NX Machining Knowledge Editor")
    print("  2. 在规则树根节点右键 → Import")
    print("  3. 选择生成的 factory_plate_rules_complete.xml")
    print("  4. 导入后验证规则树结构")
    print()
    print("✨ 完成！")


if __name__ == "__main__":
    main()
