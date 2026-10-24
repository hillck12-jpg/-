# -*- coding: utf-8 -*-
"""复现第2章 六类分析方法 4分布分析（对应 PBIX 参考答案 第4页）。

数据（4分布分析.xlsx）三个子表：
- 时点/门店客流量（340行，时点粒度到小时）→ 直方图
- 用户id/年龄 → 直方图（年龄分布）
- 用户id/客单价 → 箱线图（参考答案 V1 用 BoxWhisker）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np

# 2. 读取数据
raw = pd.read_excel(DATA_DIR / "4分布分析.xlsx", sheet_name="分布分析", header=None)
# 子表1：门店客流量（列 B/C）
flow = pd.read_excel(DATA_DIR / "4分布分析.xlsx", sheet_name="分布分析",
                     header=1, usecols=[1, 2]).dropna()
flow.columns = ["时点", "门店客流量"]
# 子表2：年龄（列 K/L）
age = pd.read_excel(DATA_DIR / "4分布分析.xlsx", sheet_name="分布分析",
                    header=1, usecols=[10, 11]).dropna()
age.columns = ["用户id", "年龄"]
age["年龄"] = pd.to_numeric(age["年龄"], errors="coerce")
age = age.dropna()
# 子表3：客单价（列 T/U）
price = pd.read_excel(DATA_DIR / "4分布分析.xlsx", sheet_name="分布分析",
                      header=None, usecols=[19, 20], skiprows=1).dropna()
price.columns = ["用户id", "客单价"]
price["客单价"] = pd.to_numeric(price["客单价"], errors="coerce")
price = price.dropna()

import matplotlib.pyplot as plt

# 7-1. 门店客流量直方图
fig, ax = new_ax(figsize=(9, 5.5))
ax.hist(pd.to_numeric(flow["门店客流量"], errors="coerce").dropna(), bins=25,
        color="#3A5FCD", alpha=0.85, edgecolor="white")
beautify(ax, "门店客流量分布（直方图）", "客流量（人次）", "频数")
save(fig, "distribution_flow_hist")

# 7-2. 年龄分布直方图
fig, ax = new_ax(figsize=(9, 5.5))
ax.hist(age["年龄"], bins=range(int(age["年龄"].min()), int(age["年龄"].max()) + 5, 5),
        color="#2E8B57", alpha=0.85, edgecolor="white")
beautify(ax, "用户年龄分布（直方图）", "年龄（岁）", "用户数")
save(fig, "distribution_age_hist")

# 7-3. 客单价箱线图
fig, ax = new_ax(figsize=(7, 5.5))
bp = ax.boxplot(price["客单价"], vert=True, patch_artist=True, widths=0.4,
                boxprops={"facecolor": "#3A5FCD", "alpha": 0.7},
                medianprops={"color": "#B22222", "lw": 1.5},
                flierprops={"marker": "o", "markerfacecolor": "gray", "alpha": 0.5})
q = price["客单价"].quantile([0.25, 0.5, 0.75])
for y, label in [(q[0.5], f"中位数 {q[0.5]:.1f}"), (q[0.25], f"Q1 {q[0.25]:.1f}"), (q[0.75], f"Q3 {q[0.75]:.1f}")]:
    ax.annotate(label, (1.25, y), fontsize=9, color="#333333", va="center")
beautify(ax, "用户客单价分布（箱线图）", "", "客单价（元）")
ax.set_xticklabels(["全部用户"])
save(fig, "distribution_price_box")
