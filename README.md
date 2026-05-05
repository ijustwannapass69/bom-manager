# BOM Manager（四旋翼无人机整机）

这是一个用于课程作业的简易 Python BOM 管理器示例，产品对象为**四旋翼无人机整机**。

## 已实现功能

1. 物料录入 / 新增（`add_material`）
2. 物料修改（`edit_material`）
3. 物料查询（`search_material`）
4. 父子关系维护（`move_material`）
5. 层级树展示（`print_tree`）
6. BOM 清单导出 CSV（`export_csv`）

默认数据满足作业要求：
- 层级不少于 3 层（示例到 4 层）
- 物料总数不少于 10 个

## 运行环境

- Python 3.8+

## 运行方法

```bash
python3 bom_manager.py
```

运行后会：
- 打印初始 BOM 树
- 演示修改、查询、父子关系维护
- 打印变更后的 BOM 树
- 导出 `drone_bom_export.csv`

## 文件说明

- `bom_manager.py`：主程序源码
- `drone_bom_export.csv`：运行后生成的 BOM 导出文件
