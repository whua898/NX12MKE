#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证生成的 XML 文件结构"""

import xml.etree.ElementTree as ET

def validate_xml(filepath):
    """验证 XML 文件"""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        print(f"✅ XML 格式正确")
        print(f"根节点: {root.tag}")
        
        # 查找 Objects
        objects = root.find('Objects')
        if objects is None:
            print("❌ 未找到 Objects 节点")
            return False
        
        # 统计库和规则
        libs = objects.findall('.//MachiningRuleLibrary')
        rules = objects.findall('.//MachiningRule')
        
        print(f"\n📊 统计信息:")
        print(f"  库数量: {len(libs)}")
        print(f"  规则数量: {len(rules)}")
        
        # 列出所有库
        print(f"\n📚 库列表:")
        for lib in libs:
            name = lib.get('Name', 'N/A')
            ext_id = lib.get('ExternalId', 'N/A')
            print(f"  - {name} (ExternalId: {ext_id})")
            
            # 检查 children 引用
            children = lib.find('children')
            if children is not None:
                child_refs = [item.text for item in children.findall('item')]
                if child_refs:
                    print(f"    children: {len(child_refs)} 个引用")
        
        # 验证双向指针
        print(f"\n🔗 双向指针验证:")
        all_ext_ids = set()
        for obj in objects.findall('.//*'):
            ext_id = obj.get('ExternalId')
            if ext_id:
                all_ext_ids.add(ext_id)
        
        broken_children = []
        broken_collections = []
        
        for lib in libs:
            # 检查 children
            children = lib.find('children')
            if children is not None:
                for item in children.findall('item'):
                    ref_id = item.text
                    if ref_id and ref_id not in all_ext_ids:
                        broken_children.append((lib.get('Name'), ref_id))
            
            # 检查 collections
            collections = lib.find('collections')
            if collections is not None:
                for item in collections.findall('item'):
                    ref_id = item.text
                    if ref_id and ref_id not in all_ext_ids:
                        broken_collections.append((lib.get('Name'), ref_id))
        
        if broken_children:
            print(f"  ⚠️ 断裂的 children 引用 ({len(broken_children)} 个):")
            for lib_name, ref_id in broken_children[:5]:
                print(f"    {lib_name} -> {ref_id}")
        else:
            print(f"  ✅ children 引用完整")
        
        if broken_collections:
            print(f"  ⚠️ 断裂的 collections 引用 ({len(broken_collections)} 个):")
            for lib_name, ref_id in broken_collections[:5]:
                print(f"    {lib_name} -> {ref_id}")
        else:
            print(f"  ✅ collections 引用完整")
        
        # 检查规则名称唯一性
        rule_names = [r.get('Name') for r in rules]
        duplicates = set([n for n in rule_names if rule_names.count(n) > 1])
        if duplicates:
            print(f"\n  ⚠️ 重复的规则名称: {duplicates}")
        else:
            print(f"\n  ✅ 规则名称唯一")
        
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML 解析错误: {e}")
        return False

if __name__ == "__main__":
    validate_xml('factory_plate_rules_complete.xml')
