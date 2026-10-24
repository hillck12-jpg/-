# -*- coding: utf-8 -*-
"""复现第2章 六类分析方法 1趋势分析（对应 PBIX 参考答案08/09 第1页）。

数据（1趋势分析.xlsx 趋势图 sheet）：year + 订单量，2014-2023
产出：
- 近10年订单量波动趋势图（柱图）
- 各月订单量及环比增幅趋势（柱+线组合图，参考答案08 第1页 V3）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd

# 2. 读取数据（真实表头在第2行）
raw = pd.read_excel(DATA_DIR / "1趋势分析.xlsx", sheet_name="趋势图", header=None)
df = pd.read_excel(DATA_DIR / "1趋势分析.xlsx", sheet_name="趋势图", header=1)
df = df.dropna(subset=[df.columns[1]]).iloc[:, 1:3]
df.columns = ["year", "订单量"]
df["year"] = df["year"].astype(str).str.strip().str.replace(".0", "", regex=False)
df["订单量"] = pd.to_numeric(df["订单量"], errors="coerce")
df = df.dropna(subset=["订单量"])

# 7-1. 近10年订单量波动趋势图
fig, ax = new_ax(figsize=(10, 5.5))
bars = ax.bar(df["year"], df["订单量"], color="#3A5FCD", alpha=0.85)
for b, v in zip(bars, df["订单量"]):
    ax.text(b.get_x() + b.get_width()/2, v, f"{v:.0f}", ha="center", va="bottom", fontsize=9)
beautify(ax, "近 10 年订单量波动趋势图", "年份", "订单量（单位：个）")
save(fig, "trend_analysis_yearly")

# 7-2. 订单量环比增幅（组合图）
df["环比增幅"] = df["订单量"].pct_change()
fig, ax = new_ax(figsize=(10, 5.5))
ax.bar(df["year"], df["订单量"], color="#3A5FCD", alpha=0.85, label="订单量")
ax2 = ax.twinx()
mask = df["环比增幅"].notna()
ax2.plot(df.loc[mask, "year"], df.loc[mask, "环比增幅"] * 100, color="#B22222",
         marker="o", lw=1.5, label="环比增幅")
ax2.set_ylabel("环比增幅（%）", fontsize=12)
ax2.spines["top"].set_visible(False)
ax2.axhline(0, color="gray", lw=0.8, ls="--")
beautify(ax, "各年订单量及环比增幅趋势图", "年份", "订单量（单位：个）")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False, loc="upper left")
save(fig, "trend_analysis_mom")
