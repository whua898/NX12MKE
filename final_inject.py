#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终注入脚本：处理 <name> 标签
"""

import xml.etree.ElementTree as ET
import shutil
from datetime import datetime

def main():
    print("🚀 开始最终注入...")
    
    target = "machining_knowledge.xml"
    source = "factory_plate_rules_complete.xml"
    output = "machining_knowledge_final.xml"
    
    shutil.copy2(target, f"{target}.backup_final2")
    
    t_tree = ET.parse(target)
    t_root = t_tree.getroot()
    t_objects = t_root.find('Objects')
    
    s_tree = ET.parse(source)
    s_root = s_tree.getroot()
    s_objects = s_root.find('Objects')
    
    # Find source lib by <name> tag
    src_lib = None
    for obj in s_objects.findall('.//MachiningRuleLibrary'):
        name_elem = obj.find('name')
        if name_elem is not None and name_elem.text == 'Factory_Plate_General':
            src_lib = obj
            break
            
    if src_lib is None:
        print("❌ 找不到源规则库")
        return
        
    # Append
    t_objects.append(src_lib)
    print("✅ 已追加新规则库")
    
    # Update Parent Reference
    parent = None
    for obj in t_objects.findall('.//MachiningRuleLibrary'):
        colls = obj.find('collections')
        if colls is not None:
            for item in colls.findall('item'):
                if item.text == '#OOTB_EnvironmentLibraryEnvRuleRoot':
                    parent = obj
                    break
    
    if parent is not None:
        children = parent.find('children')
        if children is None:
            children = ET.SubElement(parent, 'children')
        
        existing = [i.text for i in children.findall('item')]
        new_id = src_lib.get('ExternalId')
        
        if new_id not in existing:
            ET.SubElement(children, 'item').text = new_id
            print("✅ 已更新父节点引用")
            
    t_tree.write(output, encoding='utf-8', xml_declaration=True)
    print(f"💾 已保存: {output}")
    
    # Verify
    v_tree = ET.parse(output)
    v_objects = v_tree.getroot().find('Objects')
    count = 0
    for obj in v_objects.findall('.//MachiningRuleLibrary'):
        name_elem = obj.find('name')
        if name_elem is not None and name_elem.text == 'Factory_Plate_General':
            count += 1
            
    print(f"🔍 验证: 找到 {count} 个 Factory_Plate_General 库")
    print("✨ 完成！请在 NX MKE 中加载 machining_knowledge_final.xml")

if __name__ == "__main__":
    main()
