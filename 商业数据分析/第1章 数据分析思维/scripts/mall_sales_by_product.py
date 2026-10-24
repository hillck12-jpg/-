# -*- coding: utf-8 -*-
"""复现第1章 PBIX②《商场销售数据表》：各产品销售额对比（multiRowCard/柱图）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd

# 2. 读取数据
sales = pd.read_excel(DATA_DIR / "商场销售数据表.xlsx", sheet_name="产品销售数据表")

# 6. 分组聚合：按产品名称汇总销售额
by_product = sales.groupby("产品名称")["销售额"].sum().sort_values(ascending=True)

# 7. 绘制水平条形图
fig, ax = new_ax(figsize=(9, 5))
bars = ax.barh(by_product.index, by_product.values, color="#3A5FCD", alpha=0.85)
for b, v in zip(bars, by_product.values):
    ax.text(v + by_product.max() * 0.01, b.get_y() + b.get_height() / 2, f"{v:,.0f}",
            va="center", fontsize=9)

# 8. 图表美化
beautify(ax, "各产品销售额对比", "销售额（元）", "产品名称")
save(fig, "mall_sales_by_product")
