# -*- coding: utf-8 -*-
"""复现第3章案例1：2020年11月各省份同比增长情况（柱图）+ 四川省2020年各月同比增长（线图）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import matplotlib.pyplot as plt

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "案例1：收入趋势分析原始数据.xlsx")

# 6. 分组聚合
m = df[df["订单年份"].isin([2019, 2020])].pivot_table(
    index="销售省份", columns="订单年份", values="销售额", aggfunc="sum").fillna(0)

# 2020年11月各省份同比增长
prov = ((m[2020] - m[2019]) / m[2019]).dropna().sort_values(ascending=False)
# 需要限定 11 月：重新按月份过滤
mm = df[(df["订单年份"].isin([2019, 2020])) & (df["订单月份"] == 11)].pivot_table(
    index="销售省份", columns="订单年份", values="销售额", aggfunc="sum").fillna(0)
prov_nov = ((mm[2020] - mm[2019]) / mm[2019]).replace([float("inf")], 0).dropna().sort_values(ascending=False)

# 四川省 2020 各月同比
sc = df[(df["销售省份"] == "四川") & (df["订单年份"].isin([2019, 2020]))].pivot_table(
    index="订单月份", columns="订单年份", values="销售额", aggfunc="sum").fillna(0)
sc_yoy = ((sc[2020] - sc[2019]) / sc[2019]).replace([float("inf")], 0).dropna()

# 7-1. 2020年11月各省份同比增长情况
fig, ax = new_ax(figsize=(10, 6))
colors = ["#B22222" if v < 0 else "#3A5FCD" for v in prov_nov.values]
ax.bar(prov_nov.index, prov_nov.values * 100, color=colors)
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
beautify(ax, "2020年11月各省份同比增长情况分析", "销售省份", "同比增长率（%）")
ax.axhline(0, color="gray", lw=0.8)
save(fig, "income_trend_province_nov")

# 7-2. 四川省2020年各月同比增长
fig, ax = new_ax(figsize=(9, 5))
ax.plot(sc_yoy.index.astype(str), sc_yoy.values * 100, marker="o", color="#2E8B57")
ax.axhline(0, color="gray", lw=0.8, ls="--")
beautify(ax, "四川省2020年各月同比增长情况", "订单月份", "同比增长率（%）")
save(fig, "income_trend_sichuan_yoy")
