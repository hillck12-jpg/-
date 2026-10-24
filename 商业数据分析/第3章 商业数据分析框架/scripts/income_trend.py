# -*- coding: utf-8 -*-
"""复现第3章案例1《收入趋势分析》：年度销售趋势、2020年月趋势、同比增长率趋势。

原始数据字段：订单年份、订单月份、销售省份、销售额（2017-2020）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import matplotlib.pyplot as plt

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "案例1：收入趋势分析原始数据.xlsx")

# 6. 分组聚合
year_sales = df.groupby("订单年份")["销售额"].sum()
m2020 = df[df["订单年份"] == 2020].groupby("订单月份")["销售额"].sum()
m2020 = m2020.reindex(range(1, 13)).dropna()

# 同比增长率：2020 各月 vs 2019 各月
m2019 = df[df["订单年份"] == 2019].groupby("订单月份")["销售额"].sum()
yoy = ((m2020 - m2019.reindex(m2020.index)) / m2019.reindex(m2020.index)).dropna()

# 7-1. 年度销售趋势分析
fig, ax = new_ax(figsize=(8, 5))
ax.plot(year_sales.index.astype(str), year_sales.values, marker="o", color="#3A5FCD")
for x, v in zip(year_sales.index.astype(str), year_sales.values):
    ax.annotate(f"{v:,.0f}", (x, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
beautify(ax, "年度销售趋势分析", "订单年份", "销售额（元）")
save(fig, "income_trend_yearly")

# 7-2. 2020年月销售趋势分析
fig, ax = new_ax(figsize=(9, 5))
ax.plot(m2020.index.astype(str), m2020.values, marker="o", color="#2E8B57")
beautify(ax, "2020年月销售趋势分析", "订单月份", "销售额（元）")
save(fig, "income_trend_monthly_2020")

# 7-3. 2020年销售同比增长率趋势分析
fig, ax = new_ax(figsize=(9, 5))
ax.plot(yoy.index.astype(str), yoy.values * 100, marker="o", color="#B22222")
ax.axhline(0, color="gray", lw=0.8, ls="--")
beautify(ax, "2020年销售同比增长率趋势分析", "订单月份", "同比增长率（%）")
save(fig, "income_trend_yoy_2020")
