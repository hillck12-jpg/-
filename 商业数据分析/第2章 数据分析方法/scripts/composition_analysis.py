# -*- coding: utf-8 -*-
"""复现第2章 六类分析方法 3构成分析（对应 PBIX 参考答案 第3页）。

数据（3构成分析.xlsx 构成分析 sheet）三个子表：
- row3-7:  产品1-4 销售量（占比和量两个维度）
- row16-21: 近5年各产品销量统计（年/产品1/产品2/产品3）
- row28-33: 累积柱形/面积用数据（年/产品1/产品2/产品3）
产出（参考答案 V1-V4）：饼图、环形图、堆积柱形图、堆积面积图
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 读取数据
raw = pd.read_excel(DATA_DIR / "3构成分析.xlsx", sheet_name="构成分析", header=None)

# 子表1：产品销售量（row4-7，列1-2）
df = raw.iloc[4:8, [1, 2]].copy()
df.columns = ["产品类型", "销售量"]
df["销售量"] = pd.to_numeric(df["销售量"], errors="coerce")
df = df.dropna()
df["产品类型"] = df["产品类型"].astype(str)

# 子表2：近5年产品销量统计（row17-21，列1-4）
years_df = raw.iloc[17:22, [1, 2, 3, 4]].copy()
years_df.columns = ["年份", "产品 1", "产品 2", "产品 3"]
years_df["年份"] = years_df["年份"].astype(str)
years_df = years_df.set_index("年份").apply(pd.to_numeric, errors="coerce").dropna()
years = years_df.index.tolist()

colors = ["#3A5FCD", "#E8A33D", "#2E8B57", "#B22222"]

# 7-1. 饼图（当前销量构成）
fig, ax = new_ax(figsize=(7, 5.5))
ax.pie(df["销售量"], labels=df["产品类型"], autopct="%1.1f%%", startangle=90,
       colors=colors, textprops={"fontsize": 11})
ax.set_title("各产品销售量占比", loc="left", fontsize=14)
save(fig, "composition_pie")

# 7-2. 环形图
fig, ax = new_ax(figsize=(7, 5.5))
wedges, texts, autotexts = ax.pie(
    df["销售量"], labels=df["产品类型"], autopct="%1.1f%%", startangle=90,
    colors=colors, pctdistance=0.78, wedgeprops={"width": 0.42, "edgecolor": "white"},
    textprops={"fontsize": 11})
ax.text(0, 0, f"总计\n{df['销售量'].sum():.0f}", ha="center", va="center", fontsize=13, weight="bold")
ax.set_title("各产品销售量构成（环形）", loc="left", fontsize=14)
save(fig, "composition_donut")

# 7-3. 堆积柱形图（近5年各产品销量，对应参考答案"累积柱形图"）
fig, ax = new_ax(figsize=(9, 5.5))
bottom = np.zeros(len(years))
for (name, row), c in zip(years_df.items(), colors):
    vals = row.to_numpy(dtype=float)
    ax.bar(years, vals, bottom=bottom, label=str(name), color=c, alpha=0.85, width=0.55)
    bottom += vals
totals = years_df.sum(axis=1)
for i, t in enumerate(totals):
    ax.text(i, t, f"{t:,.0f}", ha="center", va="bottom", fontsize=9)
beautify(ax, "近5年各产品销量堆积构成", "年份", "销售量")
ax.legend(frameon=False, fontsize=9)
save(fig, "composition_stacked_column")

# 7-4. 堆积面积图（近5年各产品销量）
fig, ax = new_ax(figsize=(9, 5.5))
stack_vals = [years_df[c].to_numpy(dtype=float) for c in years_df.columns]
ax.stackplot(years, np.vstack(stack_vals),
             labels=[str(c) for c in years_df.columns], colors=colors[:len(stack_vals)], alpha=0.8)
beautify(ax, "近5年各产品销量堆积面积", "年份", "销售量")
ax.legend(frameon=False, fontsize=9, loc="upper left")
save(fig, "composition_stacked_area")
