# -*- coding: utf-8 -*-
"""复现第1章 PBIX②《商场销售数据表》第1页：各月销售额堆积面积图（附年度切片器）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, FIG_DIR, new_ax, beautify, save
import pandas as pd

# 2. 读取数据（维度模型：事实表 产品销售数据表 + 维度表 日期表）
sales = pd.read_excel(DATA_DIR / "商场销售数据表.xlsx", sheet_name="产品销售数据表")
sales["订单日期"] = pd.to_datetime(sales["订单日期"])

# 6. 分组聚合：按年月汇总销售额
sales["年月"] = sales["订单日期"].dt.to_period("M").astype(str)
monthly = sales.groupby("年月")["销售额"].sum()

# 7. 绘制面积图
fig, ax = new_ax()
ax.fill_between(range(len(monthly)), monthly.values, alpha=0.75, color="#3A5FCD")
ax.plot(range(len(monthly)), monthly.values, color="#1F3B8C", lw=1.5)
ax.set_xticks(range(0, len(monthly), 6))
ax.set_xticklabels(monthly.index[::6], rotation=0, fontsize=9)

# 8. 图表美化
beautify(ax, "各月销售额变化（2018.1-2019.12）", "订单日期", "销售额（元）")
ax.yaxis.set_major_formatter(__import__("matplotlib.ticker", fromlist=["FuncFormatter"]).FuncFormatter(
    lambda x, p: f"{x/1e6:.0f} 百万"))
save(fig, "mall_sales_by_month")
