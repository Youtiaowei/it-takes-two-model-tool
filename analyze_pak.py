#!/usr/bin/env python3
"""
《双人成行》解包资源分析工具
扫描解包后的目录，自动识别角色模型、骨骼、贴图等资源
"""
import os
import sys
from pathlib import Path


# 角色关键词
CHARACTER_KEYWORDS = {
    "Cody (科迪)": ["cody", "sk_cody"],
    "May (梅)": ["may", "sk_may"],
    "Rose (罗斯)": ["rose", "sk_rose"],
    "Hakim (哈基姆博士)": ["hakim", "sk_hakim", "book"],
    "Cutie (布偶)": ["cutie", "sk_cutie"],
}

ASSET_TYPES = {
    "SkeletalMesh": ["sk_", "mesh"],
    "Skeleton": ["skeleton"],
    "PhysicsAsset": ["phys", "physics"],
    "Animation": ["anim"],
    "Material": ["m_", "mat_", "material", "mi_"],
    "Texture": ["t_", "tex_", "texture", "diffuse", "normal", "specular"],
    "Blueprint": ["bp_", "blueprint"],
}


def scan_unpacked_directory(unpacked_path: Path):
    """扫描解包目录，分析资源"""
    unpacked_path = Path(unpacked_path)
    if not unpacked_path.exists():
        print(f"❌ 目录不存在: {unpacked_path}")
        return

    all_files = list(unpacked_path.rglob("*"))
    uasset_files = [f for f in all_files if f.suffix.lower() == ".uasset"]
    other_files = [f for f in all_files if f.is_file() and f.suffix.lower() not in (".uasset", ".ubulk", ".uexp", ".uptnl")]

    print("=" * 60)
    print(f"  解包目录分析报告")
    print(f"  目录: {unpacked_path}")
    print("=" * 60)
    print(f"\n📊 总览:")
    print(f"  文件总数: {len(all_files)}")
    print(f"  .uasset 文件: {len(uasset_files)}")

    if not uasset_files:
        print("\n❌ 没有找到 .uasset 文件，请确认:")
        print("  1. 解包目录是否正确")
        print("  2. .pak 文件是否已正确解包")
        print("  3. 检查是否有 .ubulk / .uexp 等附加文件")
        return

    # ─── 按角色分类 ───
    print(f"\n🎮 角色资源:")
    for char_name, keywords in CHARACTER_KEYWORDS.items():
        matches = []
        for f in uasset_files:
            name_lower = f.stem.lower()
            for kw in keywords:
                if kw in name_lower:
                    matches.append(f)
                    break
        if matches:
            print(f"\n  {char_name}:")
            for f in matches[:8]:  # 最多显示8个
                rel = f.relative_to(unpacked_path)
                size_kb = f.stat().st_size / 1024
                print(f"    {rel} ({size_kb:.0f} KB)")
            if len(matches) > 8:
                print(f"    ... 还有 {len(matches) - 8} 个文件")
        else:
            print(f"\n  {char_name}: (未找到)")

    # ─── 按资产类型分类 ───
    print(f"\n📁 资源类型分布:")
    type_counts = {}
    for f in uasset_files:
        name_lower = f.stem.lower()
        categorized = False
        for asset_type, patterns in ASSET_TYPES.items():
            for pat in patterns:
                if pat in name_lower:
                    type_counts[asset_type] = type_counts.get(asset_type, 0) + 1
                    categorized = True
                    break
            if categorized:
                break
        if not categorized:
            type_counts["Other"] = type_counts.get("Other", 0) + 1

    for asset_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        bar = "█" * min(count // 5, 50)
        print(f"  {asset_type:15s}: {count:4d} 个 {bar}")

    # ─── 最大文件 TOP 10 ───
    print(f"\n📦 最大的 10 个文件:")
    sorted_files = sorted(uasset_files, key=lambda f: f.stat().st_size, reverse=True)[:10]
    for f in sorted_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        rel = f.relative_to(unpacked_path)
        print(f"  {size_mb:>6.1f} MB  {rel}")

    # ─── 推荐模型文件 ───
    print(f"\n💡 最可能是角色模型的文件:")
    mesh_candidates = [
        f for f in uasset_files
        if any(kw in f.stem.lower() for kw in ["sk_", "skeleton", "mesh"])
        and not any(kw in f.stem.lower() for kw in ["phys", "anim", "icon", "thumb"])
    ]
    for f in sorted(mesh_candidates, key=lambda f: f.stat().st_size, reverse=True)[:10]:
        size_mb = f.stat().st_size / (1024 * 1024)
        rel = f.relative_to(unpacked_path)
        print(f"  {size_mb:>6.1f} MB  {rel}")


def main():
    print("双人成行 - 解包资源分析工具")
    print("=" * 40)

    if len(sys.argv) > 1:
        scan_path = sys.argv[1]
    else:
        scan_path = input("请输入解包目录路径: ").strip()

    if not scan_path:
        print("❌ 未输入路径")
        return

    scan_unpacked_directory(Path(scan_path))

    print("\n" + "=" * 60)
    print("💡 提示: 也可以拖拽文件夹到这个脚本上运行")
    print("   或: python analyze_pak.py C:\\解包目录")


if __name__ == "__main__":
    main()
