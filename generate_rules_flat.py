#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NX12 MKE 板类零件自动化加工规则库生成器 (v4.0 - FLAT STRUCTURE)

关键修复：
1. NX XML 结构是扁平的 (Flat)，所有对象都在 <Objects> 下并列。
2. 层级关系通过 <children> 和 <collections> 的 ExternalId 引用建立。
3. 规则库和规则节点都包含 <name> 子元素。
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import hashlib
from datetime import datetime


class RuleGenerator:
    """MKE 规则库生成器"""

    def __init__(self):
        self.objects_list = []
        self.id_counter = 1000

    def _get_id(self):
        self.id_counter += 1
        return self.id_counter

    def add_library(self, parent_ext_id, name, description=""):
        """添加库节点到列表"""
        ext_id = f"#Lib_{name.replace(' ', '_')}"
        
        lib = ET.Element("MachiningRuleLibrary")
        lib.set("ExternalId", ext_id)
        
        node_info = ET.SubElement(lib, "NodeInfo")
        ET.SubElement(node_info, "Id").text = str(self._get_id())
        
        ET.SubElement(lib, "name").text = name
        
        # Collections (Point to Parent)
        collections = ET.SubElement(lib, "collections")
        ET.SubElement(collections, "item").text = parent_ext_id
        
        # Children (Will be filled later)
        children = ET.SubElement(lib, "children")
        
        self.objects_list.append({'element': lib, 'ext_id': ext_id, 'children_list': children})
        return ext_id

    def add_rule(self, parent_ext_id, rule_data):
        """添加规则节点到列表"""
        ext_id = f"#Rule_{rule_data['name']}"
        
        rule = ET.Element("MachiningRule")
        rule.set("ExternalId", ext_id)
        rule.set("Priority", rule_data["priority"])
        rule.set("OperationClass", rule_data["op_class"])
        rule.set("MWF", rule_data["mwf"])
        rule.set("LWF", rule_data["lwf"])
        rule.set("ToolClass", rule_data["tool_class"])
        
        node_info = ET.SubElement(rule, "NodeInfo")
        ET.SubElement(node_info, "Id").text = str(self._get_id())
        
        ET.SubElement(rule, "name").text = rule_data["name"]
        
        # Collections (Point to Parent)
        collections = ET.SubElement(rule, "collections")
        ET.SubElement(collections, "item").text = parent_ext_id
        
        # Conditions
        conditions = ET.SubElement(rule, "Conditions")
        app_criteria = ET.SubElement(conditions, "ApplicationCriteria")
        lines = ["REM Application Criteria"]
        for field, op, value in rule_data["criteria"]:
            lines.append(f"{field} {op} {value}")
        lines.append("")
        lines.append("$$ Rule rejected because condition FALSE")
        app_criteria.text = "\n".join(lines)
        
        tool_attrs = ET.SubElement(conditions, "ToolAttributes")
        t_lines = ["REM Tool Attributes"]
        for field, op, value in rule_data["tool_attrs"]:
            t_lines.append(f"{field} {op} {value}")
        tool_attrs.text = "\n".join(t_lines)
        
        lwf_attrs = ET.SubElement(conditions, "LessWorkedFeatureAttributes")
        lwf_attrs.text = "REM Less Worked Feature Attributes"
        
        oper_attrs = ET.SubElement(conditions, "OperationAttributes")
        o_lines = ["REM Operation Attributes", f'oper.name = "{rule_data["name"]}"']
        oper_attrs.text = "\n".join(o_lines)
        
        # Store ext_id to add to parent's children later
        self.objects_list.append({'element': rule, 'ext_id': ext_id, 'parent_ext_id': parent_ext_id})

    def build(self):
        """构建完整的 XML"""
        data_root = ET.Element("Data")
        data_root.set("PpXmlVer", "1.0")
        objects = ET.SubElement(data_root, "Objects")
        
        # 1. Create Main Library
        main_ext_id = self.add_library("#OOTB_EnvironmentLibraryEnvRuleRoot", "Factory_Plate_General")
        main_lib_obj = self.objects_list[0] # The main lib is the first one added
        
        # 2. Create Sub-Libraries
        sub_libs = [
            ("01_Face_Milling", "面加工库"),
            ("02_Hole_Making", "孔加工库"),
            ("03_Pocket_Slot", "型腔与槽库"),
            ("04_Chamfer", "倒角库")
        ]
        
        lib_map = {}
        for name, desc in sub_libs:
            lid = self.add_library(main_ext_id, name, desc)
            lib_map[name] = lid
            
            # Add to Main Library's children
            ET.SubElement(main_lib_obj['children_list'], "item").text = lid

        # 3. Add Rules to Sub-Libraries
        # Face Milling Rules
        face_rules = [
            {"name": "1.1_Face_Top_Rough", "priority": "1210", "op_class": "face_milling.FACE_MILLING", "mwf": "PLANAR_FACE", "lwf": "BLANK", "tool_class": "FACE_MILL", "criteria": [("mwf.AREA", ">=", "400.0"), ("mwf.AREA", "<=", "200000.0")], "tool_attrs": [("tool.Diameter", ">=", "40.0"), ("tool.Diameter", "<=", "80.0")]},
            {"name": "1.2_Face_Top_Finish", "priority": "1220", "op_class": "face_milling.FACE_MILLING", "mwf": "PLANAR_FACE", "lwf": "BLANK", "tool_class": "FACE_MILL", "criteria": [("mwf.AREA", ">=", "300.0"), ("mwf.AREA", "<=", "200000.0")], "tool_attrs": [("tool.Diameter", ">=", "32.0"), ("tool.Diameter", "<=", "63.0")]},
        ]
        
        # Add Children to Sub-Lib 01
        face_lib_children = [obj for obj in self.objects_list if obj.get('ext_id') == lib_map['01_Face_Milling']][0]['children_list']
        
        for r in face_rules:
            self.add_rule(lib_map['01_Face_Milling'], r)
            # We need to update the children list of the face lib. 
            # Since we append to self.objects_list, we need a reference.
            
        # Let's refine the loop to update children immediately
        current_objects = self.objects_list
        
        # Add to 01_Face_Milling
        for r in face_rules:
            self.add_rule(lib_map['01_Face_Milling'], r)
            # Add child ref to 01_Face_Milling
            face_obj = [obj for obj in self.objects_list if obj.get('ext_id') == lib_map['01_Face_Milling'] and 'children_list' in obj][0]
            ET.SubElement(face_obj['children_list'], "item").text = f"#Rule_{r['name']}"

        # Add to 02_Hole_Making
        hole_rules = [
             {"name": "2.1_Spot_D10", "priority": "1100", "op_class": "hole_making.SPOT_DRILLING", "mwf": "HOLE", "lwf": "BLANK", "tool_class": "CENTER_DRILL", "criteria": [("mwf.DIAMETER_1", ">=", "3.0"), ("mwf.DIAMETER_1", "<=", "22.0")], "tool_attrs": [("tool.Diameter", "=", "10.0")]},
        ]
        for r in hole_rules:
            self.add_rule(lib_map['02_Hole_Making'], r)
            hole_obj = [obj for obj in self.objects_list if obj.get('ext_id') == lib_map['02_Hole_Making'] and 'children_list' in obj][0]
            ET.SubElement(hole_obj['children_list'], "item").text = f"#Rule_{r['name']}"

        # Append all objects to <Objects>
        for obj in self.objects_list:
            objects.append(obj['element'])
            
        return data_root

    def save(self, output_file="factory_plate_rules_complete.xml"):
        """生成并保存 XML"""
        root = self.build()
        
        # Pretty Print
        rough_string = ET.tostring(root, encoding='utf-8', xml_declaration=False)
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8')
        
        with open(output_file, 'wb') as f:
            f.write(pretty_xml)
            
        print(f"✅ 规则库 XML 文件已生成：{output_file}")
        print(f"📊 文件大小：{os.path.getsize(output_file) / 1024:.2f} KB")

def main():
    print("=" * 60)
    print("  NX12 MKE 规则库生成器 v4.0 (FLAT STRUCTURE)")
    print("=" * 60)
    generator = RuleGenerator()
    generator.save()

if __name__ == "__main__":
    main()
