#!/usr/bin/env python3
"""Simple BOM Manager for 四旋翼无人机整机.

Features:
1) material input/add
2) material modification
3) material query/search
4) parent-child relationship maintenance
5) hierarchy/tree display
6) BOM list export (CSV)
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Material:
    code: str
    name: str
    spec: str
    unit: str
    quantity: float
    parent_code: Optional[str] = None
    children: List[str] = field(default_factory=list)


class BOMManager:
    def __init__(self, product_name: str):
        self.product_name = product_name
        self.materials: Dict[str, Material] = {}
        self.root_code: Optional[str] = None

    def add_material(self, code: str, name: str, spec: str, unit: str, quantity: float, parent_code: Optional[str] = None) -> None:
        if code in self.materials:
            raise ValueError(f"物料编号已存在: {code}")
        if parent_code is None and self.root_code is not None:
            raise ValueError("根节点已存在，不能添加多个顶层产品")
        if parent_code is not None and parent_code not in self.materials:
            raise ValueError(f"父物料不存在: {parent_code}")

        self.materials[code] = Material(
            code=code,
            name=name,
            spec=spec,
            unit=unit,
            quantity=quantity,
            parent_code=parent_code,
        )

        if parent_code is None:
            self.root_code = code
        else:
            self.materials[parent_code].children.append(code)

    def edit_material(self, code: str, **updates) -> None:
        mat = self.materials.get(code)
        if mat is None:
            raise ValueError(f"物料不存在: {code}")

        allowed = {"name", "spec", "unit", "quantity"}
        for key, value in updates.items():
            if key not in allowed:
                raise ValueError(f"不支持修改字段: {key}")
            setattr(mat, key, value)

    def move_material(self, code: str, new_parent_code: str) -> None:
        if code == self.root_code:
            raise ValueError("根节点不能移动")
        if code not in self.materials or new_parent_code not in self.materials:
            raise ValueError("物料或新父节点不存在")
        if self._is_descendant(new_parent_code, code):
            raise ValueError("不能把节点移动到自己的子孙节点下")

        node = self.materials[code]
        old_parent = node.parent_code
        if old_parent:
            self.materials[old_parent].children.remove(code)

        self.materials[new_parent_code].children.append(code)
        node.parent_code = new_parent_code

    def _is_descendant(self, node_code: str, ancestor_code: str) -> bool:
        current = self.materials[node_code]
        while current.parent_code is not None:
            if current.parent_code == ancestor_code:
                return True
            current = self.materials[current.parent_code]
        return False

    def search_material(self, keyword: str) -> List[Material]:
        keyword = keyword.lower().strip()
        result = []
        for mat in self.materials.values():
            if (
                keyword in mat.code.lower()
                or keyword in mat.name.lower()
                or keyword in mat.spec.lower()
            ):
                result.append(mat)
        return result

    def print_tree(self) -> None:
        if self.root_code is None:
            print("BOM为空")
            return
        print(f"产品: {self.product_name}")
        self._print_subtree(self.root_code, level=0)

    def _print_subtree(self, code: str, level: int) -> None:
        mat = self.materials[code]
        indent = "    " * level
        print(f"{indent}- [{mat.code}] {mat.name} | 规格: {mat.spec} | 用量: {mat.quantity}{mat.unit}")
        for child_code in mat.children:
            self._print_subtree(child_code, level + 1)

    def export_csv(self, filename: str) -> None:
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["层级", "物料编号", "物料名称", "规格", "单位", "用量", "父物料编号"])
            if self.root_code is not None:
                self._export_rows(self.root_code, level=1, writer=writer)

    def _export_rows(self, code: str, level: int, writer: csv.writer) -> None:
        mat = self.materials[code]
        writer.writerow([level, mat.code, mat.name, mat.spec, mat.unit, mat.quantity, mat.parent_code or "-"])
        for child_code in mat.children:
            self._export_rows(child_code, level + 1, writer)


def build_default_drone_bom() -> BOMManager:
    mgr = BOMManager(product_name="四旋翼无人机整机")

    # Level 1 root
    mgr.add_material("DRONE-001", "四旋翼无人机整机", "标准教学版", "台", 1)

    # Level 2 assemblies
    mgr.add_material("ASM-100", "机架总成", "450mm 碳纤维", "套", 1, "DRONE-001")
    mgr.add_material("ASM-200", "动力总成", "四轴无刷动力", "套", 1, "DRONE-001")
    mgr.add_material("ASM-300", "飞控与导航总成", "含GPS/IMU", "套", 1, "DRONE-001")
    mgr.add_material("ASM-400", "供电总成", "22.2V系统", "套", 1, "DRONE-001")

    # Level 3+ materials (>=10 total materials)
    mgr.add_material("MAT-101", "中央板", "碳纤维2mm", "件", 1, "ASM-100")
    mgr.add_material("MAT-102", "机臂", "碳管 16mm", "件", 4, "ASM-100")

    mgr.add_material("MAT-201", "无刷电机", "920KV", "个", 4, "ASM-200")
    mgr.add_material("MAT-202", "电调ESC", "40A", "个", 4, "ASM-200")
    mgr.add_material("MAT-203", "螺旋桨", "10x4.5", "对", 2, "ASM-200")

    mgr.add_material("MAT-301", "飞控主板", "F7", "块", 1, "ASM-300")
    mgr.add_material("MAT-302", "GPS模块", "双模定位", "个", 1, "ASM-300")
    mgr.add_material("MAT-303", "IMU模块", "六轴", "个", 1, "ASM-300")

    mgr.add_material("MAT-401", "锂电池", "6S 5000mAh", "块", 1, "ASM-400")
    mgr.add_material("MAT-402", "电源分配板", "PDB 120A", "块", 1, "ASM-400")
    mgr.add_material("MAT-403", "电源线束", "硅胶线12AWG", "套", 1, "ASM-400")

    # Level 4 example
    mgr.add_material("MAT-404", "XT60接头", "镀金", "个", 2, "MAT-403")

    return mgr


def demo() -> None:
    mgr = build_default_drone_bom()

    print("\n=== 初始BOM树 ===")
    mgr.print_tree()

    print("\n=== 物料修改示例 ===")
    mgr.edit_material("MAT-203", quantity=4, spec="10x4.5 正反桨")
    print("已修改 MAT-203")

    print("\n=== 物料查询示例（关键词: 电） ===")
    for item in mgr.search_material("电"):
        print(f"[{item.code}] {item.name} | {item.spec} | {item.quantity}{item.unit}")

    print("\n=== 父子关系维护示例（移动 XT60接头 到 PDB 下） ===")
    mgr.move_material("MAT-404", "MAT-402")

    print("\n=== 变更后BOM树 ===")
    mgr.print_tree()

    out_file = "drone_bom_export.csv"
    mgr.export_csv(out_file)
    print(f"\n=== 已导出BOM清单: {out_file} ===")


if __name__ == "__main__":
    demo()
