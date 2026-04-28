#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极修复脚本：正确处理 <name> 子元素和 Name 属性
"""

import xml.etree.ElementTree as ET
import shutil
from datetime import datetime

def main():
    print("=" * 70)
    print("  NX12 MKE 终极修复工具 v3.0")
    print("=" * 70)
    print()
    
    target_file = "machining_knowledge.xml"
    source_file = "factory_plate_rules_complete.xml"
    output_file = "machining_knowledge_fixed.xml"
    
    # 备份
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{target_file}.backup_fix_{timestamp}"
    shutil.copy2(target_file, backup_path)
    print(f"✅ 已备份: {backup_path}")
    
    # 解析
    print("\n📖 解析 XML...")
    target_tree = ET.parse(target_file)
    target_root = target_tree.getroot()
    target_objects = target_root.find('Objects')
    
    source_tree = ET.parse(source_file)
    source_root = source_tree.getroot()
    source_objects = source_root.find('Objects')
    
    # 查找所有 Factory_Plate_General（检查属性 Name 和子元素 <name>）
    print("\n🔍 查找所有 Factory_Plate_General 库...")
    all_libs = []
    for obj in target_objects.findall('.//MachiningRuleLibrary'):
        name_attr = obj.get('Name')
        name_elem = obj.find('name')
        name_text = name_elem.text if name_elem is not None else None
        
        if name_attr == 'Factory_Plate_General' or name_text == 'Factory_Plate_General':
            ext_id = obj.get('ExternalId')
            all_libs.append((obj, ext_id, 'attr' if name_attr else 'elem'))
            print(f"  找到: ExternalId={ext_id}, 来源={'属性' if name_attr else '子元素'}")
    
    print(f"\n  共找到 {len(all_libs)} 个 Factory_Plate_General 库")
    
    # 删除所有旧库
    if len(all_libs) > 0:
        print("\n🧹 删除所有旧库...")
        for obj, ext_id, source_type in all_libs:
            target_objects.remove(obj)
            print(f"  ✅ 已删除: {ext_id}")
    
    # 提取新规则
    print("\n📥 提取新规则...")
    new_factory_lib = None
    for obj in source_objects.findall('.//MachiningRuleLibrary'):
        if obj.get('Name') == 'Factory_Plate_General':
            new_factory_lib = obj
            break
    
    if new_factory_lib is None:
        print("❌ 未找到新规则库")
        return
    
    # 注入
    print("\n💉 注入新规则...")
    target_objects.append(new_factory_lib)
    print(f"  ✅ 已注入: {new_factory_lib.get('ExternalId')}")
    
    # 更新父节点引用
    parent_node = None
    for obj in target_objects.findall('.//MachiningRuleLibrary'):
        collections = obj.find('collections')
        if collections is not None:
            for item in collections.findall('item'):
                if item.text == '#OOTB_EnvironmentLibraryEnvRuleRoot':
                    parent_node = obj
                    break
    
    if parent_node is not None:
        children = parent_node.find('children')
        if children is None:
            children = ET.SubElement(parent_node, 'children')
        
        existing_children = [item.text for item in children.findall('item')]
        new_ext_id = new_factory_lib.get('ExternalId')
        
        if new_ext_id and new_ext_id not in existing_children:
            ET.SubElement(children, 'item').text = new_ext_id
            print(f"  ✅ 已更新父节点引用")
    
    # 保存
    print(f"\n💾 保存到: {output_file}")
    target_tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    # 验证
    print("\n🔍 验证...")
    verify_tree = ET.parse(output_file)
    verify_root = verify_tree.getroot()
    verify_objects = verify_root.find('Objects')
    
    found_libs = []
    for obj in verify_objects.findall('.//MachiningRuleLibrary'):
        name_attr = obj.get('Name')
        name_elem = obj.find('name')
        name_text = name_elem.text if name_elem is not None else None
        
        if name_attr == 'Factory_Plate_General' or name_text == 'Factory_Plate_General':
            found_libs.append(obj)
    
    if len(found_libs) == 1:
        print(f"  ✅ 验证通过：只有 1 个 Factory_Plate_General")
        lib = found_libs[0]
        print(f"  ExternalId: {lib.get('ExternalId')}")
        
        # 统计规则
        rules_count = len(lib.findall('.//MachiningRule'))
        print(f"  规则数量: {rules_count}")
        
        # 检查第一条规则
        first_rule = lib.find('.//MachiningRule')
        if first_rule is not None:
            print(f"  第一条规则: {first_rule.get('Name')}")
    else:
        print(f"  ❌ 验证失败：找到 {len(found_libs)} 个 Factory_Plate_General")
    
    print("\n✨ 完成！")
    print(f"\n📋 下一步:")
    print(f"  1. 在 NX MKE 中测试加载: {output_file}")
    print(f"  2. 如果通过: Copy-Item {output_file} machining_knowledge.xml -Force")

if __name__ == "__main__":
    main()

