# -*- coding: utf-8 -*-
"""复现第2章 六类分析方法 2对比分析（对应 PBIX 参考答案 第2页）。

数据（2对比分析.xlsx）：产品1-6 的订单量
产出：
- 不同产品订单量对比柱图
- 不同产品订单量对比条形图（横柱，参考答案 V2）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd

# 2. 读取数据（真实表头在第2行）
raw = pd.read_excel(DATA_DIR / "2对比分析.xlsx", sheet_name="对比分析", header=None)
df = pd.read_excel(DATA_DIR / "2对比分析.xlsx", sheet_name="对比分析", header=1)
df = df.dropna(subset=[df.columns[1]]).iloc[:, 1:3]
df.columns = ["产品类型", "订单量"]
df["订单量"] = pd.to_numeric(df["订单量"], errors="coerce")
df = df.dropna(subset=["订单量"]).sort_values("订单量", ascending=False)

# 7-1. 柱图
fig, ax = new_ax(figsize=(9, 5.5))
bars = ax.bar(df["产品类型"], df["订单量"], color="#3A5FCD", alpha=0.85)
for b, v in zip(bars, df["订单量"]):
    ax.text(b.get_x() + b.get_width()/2, v, f"{v:.0f}", ha="center", va="bottom", fontsize=9)
beautify(ax, "不同产品订单量对比", "产品类型", "订单量（单位：个）")
save(fig, "comparison_analysis_column")

# 7-2. 条形图
df_s = df.sort_values("订单量")
fig, ax = new_ax(figsize=(9, 5.5))
bars = ax.barh(df_s["产品类型"], df_s["订单量"], color="#3A5FCD", alpha=0.85)
for b, v in zip(bars, df_s["订单量"]):
    ax.text(v + df_s["订单量"].max() * 0.01, b.get_y() + b.get_height()/2,
            f"{v:.0f}", va="center", fontsize=9)
beautify(ax, "不同产品订单量对比", "订单量（单位：个）", "产品类型")
save(fig, "comparison_analysis_bar")
