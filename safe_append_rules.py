#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最安全策略：只注入新规则，不删除任何现有节点
"""

import xml.etree.ElementTree as ET
import shutil
from datetime import datetime

def main():
    print("=" * 70)
    print("  NX12 MKE 安全注入工具 v4.0 - 只追加不删除")
    print("=" * 70)
    print()
    
    target_file = "machining_knowledge.xml"
    source_file = "factory_plate_rules_complete.xml"
    output_file = "machining_knowledge_safe.xml"
    
    # 备份
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{target_file}.backup_safe_{timestamp}"
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
    
    # 提取新规则库
    print("\n📥 提取新规则库...")
    new_factory_lib = None
    for obj in source_objects.findall('.//MachiningRuleLibrary'):
        if obj.get('Name') == 'Factory_Plate_General':
            new_factory_lib = obj
            break
    
    if new_factory_lib is None:
        print("❌ 未找到新规则库")
        return
    
    print(f"  ExternalId: {new_factory_lib.get('ExternalId')}")
    
    # 检查是否已存在
    existing = []
    for obj in target_objects.findall('.//MachiningRuleLibrary'):
        name_attr = obj.get('Name')
        name_elem = obj.find('name')
        name_text = name_elem.text if name_elem is not None else None
        
        if name_attr == 'Factory_Plate_General' or name_text == 'Factory_Plate_General':
            existing.append(obj.get('ExternalId'))
    
    print(f"\n  已存在 {len(existing)} 个 Factory_Plate_General 库")
    
    if len(existing) > 0:
        print("  ⚠️  检测到旧规则库，本次不删除，只追加新库")
        print("  您可以在 NX MKE 中手动删除旧库")
    
    # 追加新规则库
    print("\n💉 追加新规则库...")
    target_objects.append(new_factory_lib)
    print(f"  ✅ 已追加: {new_factory_lib.get('ExternalId')}")
    
    # 更新父节点引用（只添加，不删除旧引用）
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
            print(f"  ✅ 已添加父节点引用")
        else:
            print(f"  ℹ️  父节点引用已存在")
    
    # 保存
    print(f"\n💾 保存到: {output_file}")
    target_tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    # 验证
    print("\n🔍 验证...")
    verify_tree = ET.parse(output_file)
    verify_root = verify_tree.getroot()
    verify_objects = verify_root.find('Objects')
    
    all_libs = []
    for obj in verify_objects.findall('.//MachiningRuleLibrary'):
        name_attr = obj.get('Name')
        name_elem = obj.find('name')
        name_text = name_elem.text if name_elem is not None else None
        
        if name_attr == 'Factory_Plate_General' or name_text == 'Factory_Plate_General':
            all_libs.append(obj)
    
    print(f"  Factory_Plate_General 库数量: {len(all_libs)}")
    for i, lib in enumerate(all_libs, 1):
        ext_id = lib.get('ExternalId')
        rules_count = len(lib.findall('.//MachiningRule'))
        first_rule = lib.find('.//MachiningRule')
        first_rule_name = first_rule.get('Name') if first_rule is not None else 'N/A'
        print(f"    {i}. {ext_id}: {rules_count} 条规则，第一条: {first_rule_name}")
    
    print("\n✨ 完成！")
    print(f"\n📋 下一步:")
    print(f"  1. 在 NX MKE 中测试加载: {output_file}")
    print(f"  2. 如果新规则正常显示，手动删除旧库")
    print(f"  3. 最终确认: Copy-Item {output_file} machining_knowledge.xml -Force")

if __name__ == "__main__":
    main()
