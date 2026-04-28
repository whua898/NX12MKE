#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全注入脚本：使用 XML 解析器精确删除旧规则，注入新规则
"""

import xml.etree.ElementTree as ET
import shutil
from datetime import datetime

def main():
    print("=" * 70)
    print("  NX12 MKE 安全规则注入工具 v2.0")
    print("  使用 XML 解析器精确操作")
    print("=" * 70)
    print()
    
    target_file = "machining_knowledge.xml"
    source_file = "factory_plate_rules_complete.xml"
    output_file = "machining_knowledge_new.xml"
    
    # 备份
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{target_file}.backup_safe_{timestamp}"
    shutil.copy2(target_file, backup_path)
    print(f"✅ 已备份: {backup_path}")
    
    # 解析文件
    print("\n📖 解析 XML 文件...")
    target_tree = ET.parse(target_file)
    target_root = target_tree.getroot()
    target_objects = target_root.find('Objects')
    
    source_tree = ET.parse(source_file)
    source_root = source_tree.getroot()
    source_objects = source_root.find('Objects')
    
    # 查找并删除旧的 Factory_Plate_General
    print("\n🧹 查找旧规则...")
    old_libs = []
    for obj in target_objects.findall('.//MachiningRuleLibrary'):
        name = obj.get('Name')
        if name == 'Factory_Plate_General':
            old_libs.append(obj)
            print(f"  找到旧库: {obj.get('ExternalId')}")
    
    # 删除旧库
    for old_lib in old_libs:
        target_objects.remove(old_lib)
        print(f"  ✅ 已删除旧库")
    
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
    
    # 注入新规则
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
    
    new_libs = []
    for obj in verify_objects.findall('.//MachiningRuleLibrary'):
        if obj.get('Name') == 'Factory_Plate_General':
            new_libs.append(obj)
    
    if len(new_libs) == 1:
        print(f"  ✅ 验证通过：只有一个 Factory_Plate_General")
        print(f"  ExternalId: {new_libs[0].get('ExternalId')}")
        
        # 统计规则数量
        rules_count = len(new_libs[0].findall('.//MachiningRule'))
        print(f"  规则数量: {rules_count}")
    else:
        print(f"  ❌ 验证失败：找到 {len(new_libs)} 个 Factory_Plate_General")
    
    print("\n✨ 完成！")
    print(f"\n📋 下一步:")
    print(f"  1. 测试: NX MKE 加载 {output_file}")
    print(f"  2. 如果通过: Copy-Item {output_file} machining_knowledge.xml -Force")

if __name__ == "__main__":
    main()
