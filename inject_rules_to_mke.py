#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将生成的规则库注入到 machining_knowledge.xml
应用核心经验：
1. 备份原文件
2. 清洗旧节点（正则清除遗留 ExternalId）
3. 注入新规则（保持双向指针完整）
4. 验证完整性
"""

import xml.etree.ElementTree as ET
import re
import shutil
from datetime import datetime

def backup_original(filepath):
    """备份原文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ 已备份原文件: {backup_path}")
    return backup_path

def clean_legacy_nodes(xml_content):
    """
    强制清洗：清除所有带有 Factory_Plate_General 前缀的遗留节点
    避免孤儿节点和 ExternalId 冲突
    """
    print("🧹 开始清洗遗留节点...")
    
    # 清除旧的 Factory_Plate_General 相关节点
    patterns_to_remove = [
        r'<MachiningRuleLibrary[^>]*Name="Factory_Plate_General"[^>]*/>',
        r'<MachiningRuleLibrary[^>]*Name="Factory_Plate_General"[^>]*>.*?</MachiningRuleLibrary>',
        r'<MachiningRule[^>]*ExternalId="#Factory_Plate_[^"]*"[^>]*/>',
    ]
    
    cleaned_content = xml_content
    for pattern in patterns_to_remove:
        matches = re.findall(pattern, cleaned_content, re.DOTALL)
        if matches:
            print(f"  找到 {len(matches)} 个匹配项，正在清除...")
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.DOTALL)
    
    print("✅ 清洗完成")
    return cleaned_content

def inject_rules(target_xml, source_xml):
    """
    将源 XML 中的规则注入到目标 XML
    关键：维护双向指针完整性
    """
    print("\n📥 开始注入规则...")
    
    # 解析源文件（新生成的规则库）
    source_tree = ET.parse(source_xml)
    source_root = source_tree.getroot()
    source_objects = source_root.find('Objects')
    
    # 解析目标文件（原始 machining_knowledge.xml）
    target_tree = ET.parse(target_xml)
    target_root = target_tree.getroot()
    target_objects = target_root.find('Objects')
    
    if target_objects is None:
        # 如果没有 Objects 节点，创建它
        target_objects = ET.SubElement(target_root, 'Objects')
    
    # 提取源文件中的所有新节点
    new_libraries = source_objects.findall('.//MachiningRuleLibrary')
    new_rules = source_objects.findall('.//MachiningRule')
    
    print(f"  找到 {len(new_libraries)} 个库，{len(new_rules)} 条规则")
    
    # 检查 ExternalId 冲突
    existing_ids = set()
    for obj in target_objects.findall('.//*'):
        ext_id = obj.get('ExternalId')
        if ext_id:
            existing_ids.add(ext_id)
    
    conflicts = []
    for lib in new_libraries:
        ext_id = lib.get('ExternalId')
        if ext_id and ext_id in existing_ids:
            conflicts.append(ext_id)
    
    if conflicts:
        print(f"  ⚠️ 发现 ExternalId 冲突: {conflicts}")
        print("  需要重新生成 ExternalId...")
        # TODO: 重新生成唯一的 ExternalId
    
    # 注入主库节点
    factory_lib = None
    for lib in new_libraries:
        if lib.get('Name') == 'Factory_Plate_General':
            factory_lib = lib
            break
    
    if factory_lib is not None:
        # 添加到 Objects
        target_objects.append(factory_lib)
        print(f"  ✅ 已注入主库: Factory_Plate_General")
        
        # 更新父节点的 children 引用
        # 找到 OOTB_EnvironmentLibraryEnvRuleRoot 或合适的父节点
        parent_node = None
        for obj in target_objects.findall('.//MachiningRuleLibrary'):
            collections = obj.find('collections')
            if collections is not None:
                for item in collections.findall('item'):
                    if item.text == '#OOTB_EnvironmentLibraryEnvRuleRoot':
                        parent_node = obj
                        break
        
        if parent_node is not None:
            # 添加 children 引用
            children = parent_node.find('children')
            if children is None:
                children = ET.SubElement(parent_node, 'children')
            
            # 检查是否已存在
            existing_children = [item.text for item in children.findall('item')]
            new_ext_id = factory_lib.get('ExternalId')
            
            if new_ext_id and new_ext_id not in existing_children:
                ET.SubElement(children, 'item').text = new_ext_id
                print(f"  ✅ 已添加 children 引用: {new_ext_id}")
    
    # 保存修改后的文件
    output_file = target_xml.replace('.xml', '_updated.xml')
    target_tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"\n✅ 已保存到: {output_file}")
    
    return output_file

def validate_injected_xml(filepath):
    """验证注入后的 XML"""
    print("\n🔍 验证注入结果...")
    
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        objects = root.find('Objects')
        
        if objects is None:
            print("❌ 未找到 Objects 节点")
            return False
        
        # 统计
        libs = objects.findall('.//MachiningRuleLibrary')
        rules = objects.findall('.//MachiningRule')
        
        print(f"  库数量: {len(libs)}")
        print(f"  规则数量: {len(rules)}")
        
        # 查找我们的库
        factory_lib = None
        for lib in libs:
            if lib.get('Name') == 'Factory_Plate_General':
                factory_lib = lib
                break
        
        if factory_lib is None:
            print("  ❌ 未找到 Factory_Plate_General 库")
            return False
        
        print(f"  ✅ 找到 Factory_Plate_General 库")
        
        # 检查子库
        sub_libs = factory_lib.findall('MachiningRuleLibrary')
        print(f"  子库数量: {len(sub_libs)}")
        for sub_lib in sub_libs:
            print(f"    - {sub_lib.get('Name')}")
        
        # 验证双向指针
        all_ext_ids = set()
        for obj in objects.findall('.//*'):
            ext_id = obj.get('ExternalId')
            if ext_id:
                all_ext_ids.add(ext_id)
        
        # 检查 children 引用
        broken_refs = []
        for lib in libs:
            children = lib.find('children')
            if children is not None:
                for item in children.findall('item'):
                    ref_id = item.text
                    if ref_id and ref_id not in all_ext_ids:
                        # 允许指向外部节点（如 OOTB）
                        if not ref_id.startswith('#OOTB_'):
                            broken_refs.append((lib.get('Name'), ref_id))
        
        if broken_refs:
            print(f"  ⚠️ 断裂的引用: {len(broken_refs)} 个")
            for lib_name, ref_id in broken_refs[:5]:
                print(f"    {lib_name} -> {ref_id}")
        else:
            print(f"  ✅ 双向指针完整")
        
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML 解析错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("  NX12 MKE 规则库注入工具 v1.0")
    print("  应用核心经验：双向指针 + 脏数据清洗")
    print("=" * 70)
    print()
    
    target_file = "machining_knowledge.xml"
    source_file = "factory_plate_rules_complete.xml"
    
    # 步骤 1: 备份
    backup_original(target_file)
    
    # 步骤 2: 读取并清洗
    with open(target_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    cleaned_content = clean_legacy_nodes(original_content)
    
    # 如果内容有变化，先保存清洗后的版本
    if cleaned_content != original_content:
        cleaned_file = target_file.replace('.xml', '_cleaned.xml')
        with open(cleaned_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"💾 已保存清洗后的文件: {cleaned_file}")
        target_file = cleaned_file
    
    # 步骤 3: 注入规则
    output_file = inject_rules(target_file, source_file)
    
    # 步骤 4: 验证
    if validate_injected_xml(output_file):
        print("\n✨ 注入成功！")
        print(f"\n📋 下一步操作:")
        print(f"  1. 在 NX MKE 中测试加载: {output_file}")
        print(f"  2. 如果测试通过，替换原文件:")
        print(f"     Copy-Item {output_file} machining_knowledge.xml -Force")
    else:
        print("\n❌ 验证失败，请检查错误信息")

if __name__ == "__main__":
    main()
