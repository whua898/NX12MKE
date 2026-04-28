#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接修改 machining_knowledge.xml，添加 Factory_Plate_General 规则库
"""

import xml.etree.ElementTree as ET
from datetime import datetime
import os

def create_machining_rules():
    """创建板类零件加工规则"""
    rules = []
    
    # 01_Face_Milling
    face_lib = {
        'type': 'MachiningRuleLibrary',
        'name': '01_Face_Milling',
        'external_id': 'Factory_Plate_01_Face_Milling',
        'description': '面加工库',
        'children': [
            {
                'type': 'MachiningRule',
                'name': '1.1_Face_Top_Rough',
                'priority': '1210',
                'op_class': 'face_milling.FACE_MILLING',
                'mwf': 'PLANAR_FACE',
                'lwf': 'BLANK',
                'tool_class': 'FACE_MILL',
                'criteria': [
                    ('mwf.AREA', '>=', '400.0'),
                    ('mwf.AREA', '<=', '200000.0')
                ],
                'tool_attrs': [
                    ('tool.Diameter', '>=', '40.0'),
                    ('tool.Diameter', '<=', '80.0')
                ]
            },
            {
                'type': 'MachiningRule',
                'name': '1.2_Face_Top_Finish',
                'priority': '1220',
                'op_class': 'face_milling.FACE_MILLING',
                'mwf': 'PLANAR_FACE',
                'lwf': 'BLANK',
                'tool_class': 'FACE_MILL',
                'criteria': [
                    ('mwf.AREA', '>=', '300.0'),
                    ('mwf.AREA', '<=', '200000.0')
                ],
                'tool_attrs': [
                    ('tool.Diameter', '>=', '32.0'),
                    ('tool.Diameter', '<=', '63.0')
                ]
            }
        ]
    }
    
    # 02_Pocket_Slot
    pocket_lib = {
        'type': 'MachiningRuleLibrary',
        'name': '02_Pocket_Slot',
        'external_id': 'Factory_Plate_02_Pocket_Slot',
        'description': '型腔与槽库',
        'children': [
            {
                'type': 'MachiningRule',
                'name': '2.1_Pocket_Rough_General',
                'priority': '2410',
                'op_class': 'cavity_milling.CAVITY_MILL',
                'mwf': 'POCKET',
                'lwf': 'BLANK',
                'tool_class': 'END_MILL',
                'criteria': [
                    ('mwf.DEPTH', '>=', '1.0'),
                    ('mwf.DEPTH', '<=', '40.0'),
                    ('mwf.R_min', '>=', '2.0')
                ],
                'tool_attrs': [
                    ('tool.Diameter', '>=', '8.0'),
                    ('tool.Diameter', '<=', '20.0')
                ]
            }
        ]
    }
    
    # 03_Hole_Making
    hole_lib = {
        'type': 'MachiningRuleLibrary',
        'name': '03_Hole_Making',
        'external_id': 'Factory_Plate_03_Hole_Making',
        'description': '孔加工库',
        'children': [
            {
                'type': 'MachiningRule',
                'name': '3.1_Spot_D10',
                'priority': '1100',
                'op_class': 'hole_making.SPOT_DRILLING',
                'mwf': 'HOLE',
                'lwf': 'BLANK',
                'tool_class': 'CENTER_DRILL',
                'criteria': [
                    ('mwf.DIAMETER_1', '>=', '3.0'),
                    ('mwf.DIAMETER_1', '<=', '22.0')
                ],
                'tool_attrs': [
                    ('tool.Diameter', '=', '10.0')
                ]
            }
        ]
    }
    
    rules.append(face_lib)
    rules.append(pocket_lib)
    rules.append(hole_lib)
    
    return rules

def build_rule_element(parent, rule_data, id_counter):
    """构建规则元素"""
    rule = ET.SubElement(parent, 'MachiningRule')
    rule.set('Name', rule_data['name'])
    rule.set('Priority', rule_data['priority'])
    rule.set('OperationClass', rule_data['op_class'])
    rule.set('MWF', rule_data['mwf'])
    rule.set('LWF', rule_data['lwf'])
    rule.set('ToolClass', rule_data['tool_class'])
    
    # Conditions
    conditions = ET.SubElement(rule, 'Conditions')
    
    # Application Criteria
    app_criteria = ET.SubElement(conditions, 'ApplicationCriteria')
    criteria_text = "REM Application Criteria\n"
    for field, op, value in rule_data['criteria']:
        criteria_text += f"{field} {op} {value}\n"
    criteria_text += "\n$$ Rule rejected because condition FALSE\n"
    app_criteria.text = criteria_text
    
    # Tool Attributes
    tool_attrs = ET.SubElement(conditions, 'ToolAttributes')
    tool_text = "REM Tool Attributes\n"
    for field, op, value in rule_data['tool_attrs']:
        tool_text += f"{field} {op} {value}\n"
    tool_attrs.text = tool_text
    
    # Less Worked Feature Attributes
    lwf_attrs = ET.SubElement(conditions, 'LessWorkedFeatureAttributes')
    lwf_attrs.text = "REM Less Worked Feature Attributes\n"
    
    # Operation Attributes
    oper_attrs = ET.SubElement(conditions, 'OperationAttributes')
    oper_text = f'REM Operation Attributes\noper.name = "{rule_data["name"]}"\n'
    oper_attrs.text = oper_text
    
    return id_counter + 1

def build_library_element(parent, lib_data, objects_elem, id_counter):
    """构建规则库元素"""
    lib = ET.SubElement(parent, 'MachiningRuleLibrary')
    lib.set('Name', lib_data['name'])
    lib.set('Description', lib_data['description'])
    
    # NodeInfo
    node_info = ET.SubElement(lib, 'NodeInfo')
    ET.SubElement(node_info, 'Id').text = str(id_counter)
    id_counter += 1
    
    # collections
    collections = ET.SubElement(lib, 'collections')
    ET.SubElement(collections, 'item').text = '#OOTB_EnvironmentLibraryEnvRuleRoot'
    
    # children
    children = ET.SubElement(lib, 'children')
    for child_data in lib_data['children']:
        if child_data['type'] == 'MachiningRule':
            child_ext_id = f"#{lib_data['external_id']}_{child_data['name']}"
            ET.SubElement(children, 'item').text = child_ext_id
            
            # Create rule in Objects
            rule_ext_id = child_ext_id.lstrip('#')
            rule_elem = ET.SubElement(objects_elem, 'MachiningRule')
            rule_elem.set('ExternalId', child_ext_id)
            rule_elem.set('Name', child_data['name'])
            rule_elem.set('Priority', child_data['priority'])
            rule_elem.set('OperationClass', child_data['op_class'])
            rule_elem.set('MWF', child_data['mwf'])
            rule_elem.set('LWF', child_data['lwf'])
            rule_elem.set('ToolClass', child_data['tool_class'])
            
            # Conditions
            conditions = ET.SubElement(rule_elem, 'Conditions')
            
            app_criteria = ET.SubElement(conditions, 'ApplicationCriteria')
            criteria_text = "REM Application Criteria\n"
            for field, op, value in child_data['criteria']:
                criteria_text += f"{field} {op} {value}\n"
            criteria_text += "\n$$ Rule rejected because condition FALSE\n"
            app_criteria.text = criteria_text
            
            tool_attrs = ET.SubElement(conditions, 'ToolAttributes')
            tool_text = "REM Tool Attributes\n"
            for field, op, value in child_data['tool_attrs']:
                tool_text += f"{field} {op} {value}\n"
            tool_attrs.text = tool_text
            
            lwf_attrs = ET.SubElement(conditions, 'LessWorkedFeatureAttributes')
            lwf_attrs.text = "REM Less Worked Feature Attributes\n"
            
            oper_attrs = ET.SubElement(conditions, 'OperationAttributes')
            oper_text = f'REM Operation Attributes\noper.name = "{child_data["name"]}"\n'
            oper_attrs.text = oper_text
    
    return lib, id_counter

def main():
    input_file = 'machining_knowledge.xml'
    backup_file = 'machining_knowledge.xml.backup'
    output_file = 'machining_knowledge_modified.xml'
    
    print("=" * 60)
    print("  NX12 MKE machining_knowledge.xml 直接修改工具")
    print("=" * 60)
    print()
    
    # Backup original file
    print(f"📦 备份原始文件: {backup_file}")
    import shutil
    shutil.copy2(input_file, backup_file)
    
    # Parse XML
    print(f"📖 读取文件: {input_file}")
    tree = ET.parse(input_file)
    root = tree.getroot()
    objects = root.find('Objects')
    
    if objects is None:
        print("❌ 错误：找不到 <Objects> 节点")
        return
    
    # Find RuleRootLibrary
    rule_root = None
    for elem in objects:
        if elem.tag == 'RuleRootLibrary' and elem.get('ExternalId') == 'OOTB_EnvironmentLibraryEnvRuleRoot':
            rule_root = elem
            break
    
    if rule_root is None:
        print("❌ 错误：找不到 RuleRootLibrary 节点")
        return
    
    print("✅ 找到 RuleRootLibrary (Machining Knowledge)")
    
    # Get next ID
    max_id = 0
    for elem in objects.iter('Id'):
        try:
            id_val = int(elem.text)
            if id_val > max_id:
                max_id = id_val
        except:
            pass
    
    next_id = max_id + 1
    print(f"🔢 下一个可用 ID: {next_id}")
    
    # Create rules
    rules = create_machining_rules()
    
    # Add Factory_Plate_General library
    factory_lib = ET.SubElement(rule_root, 'MachiningRuleLibrary')
    factory_lib.set('Name', 'Factory_Plate_General')
    factory_lib.set('Description', '板类零件通用加工规则库 v2.0')
    
    # NodeInfo
    node_info = ET.SubElement(factory_lib, 'NodeInfo')
    ET.SubElement(node_info, 'Id').text = str(next_id)
    next_id += 1
    
    # collections
    collections = ET.SubElement(factory_lib, 'collections')
    ET.SubElement(collections, 'item').text = '#OOTB_EnvironmentLibraryEnvRuleRoot'
    
    # children
    children = ET.SubElement(factory_lib, 'children')
    
    # Add sub-libraries
    for rule_lib in rules:
        sub_lib, next_id = build_library_element(factory_lib, rule_lib, objects, next_id)
        children_ext_id = f"#{rule_lib['external_id']}"
        ET.SubElement(children, 'item').text = children_ext_id
    
    # Write modified XML
    print(f"💾 保存修改后的文件: {output_file}")
    tree.write(output_file, encoding='UTF-8', xml_declaration=True)
    
    print()
    print("✅ 修改完成！")
    print()
    print("📋 下一步操作:")
    print("  1. 备份原文件（已自动备份为 machining_knowledge.xml.backup）")
    print("  2. 将 machining_knowledge_modified.xml 重命名为 machining_knowledge.xml")
    print("  3. 重启 NX MKE 查看效果")
    print()
    print("⚠️  警告：直接修改原文件有风险，请确保已备份！")

if __name__ == '__main__':
    main()
