# -*- coding: utf-8 -*-
"""复现第5章 WPS 归因分析案例 - 银行贷款申请。

数据：归因分析数据.xlsx（申请书编号/申请日期/申请渠道，1597 行）
产出：
- 各渠道贷款申请量对比（柱图）
- 申请量月度趋势（按申请渠道堆积面积图）
- 各渠道申请量占比（饼图）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import matplotlib.pyplot as plt

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "归因分析数据.xlsx", sheet_name="贷款申请表")
df.columns = [str(c).strip() for c in df.columns]
date_col = [c for c in df.columns if "日期" in c][0]
ch_col = [c for c in df.columns if "渠道" in c][0]
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.dropna(subset=[date_col])

# 6. 聚合
by_ch = df.groupby(ch_col).size().sort_values(ascending=False)
df["年月"] = df[date_col].dt.to_period("M").astype(str)
by_month = df.pivot_table(index="年月", columns=ch_col, values=df.columns[0],
                          aggfunc="count").fillna(0)

# 7-1. 各渠道申请量柱图
fig, ax = new_ax(figsize=(9, 5.5))
bars = ax.bar(by_ch.index.astype(str), by_ch.values, color="#3A5FCD", alpha=0.85, width=0.55)
for b, v in zip(bars, by_ch.values):
    ax.text(b.get_x() + b.get_width()/2, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=10)
beautify(ax, "各渠道贷款申请量对比", "申请渠道", "申请量（笔）")
save(fig, "loan_attribution_channel")

# 7-2. 月度趋势堆积面积图
fig, ax = new_ax(figsize=(11, 5.5))
ax.stackplot(by_month.index.tolist(), [by_month[c] for c in by_month.columns],
             labels=by_month.columns, alpha=0.8,
             colors=plt.cm.Set2.colors[:by_month.shape[1]])
beautify(ax, "各渠道贷款申请量月度趋势", "年月", "申请量（笔）")
ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_xticks(ax.get_xticks()[::max(1, len(by_month) // 12)])
plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
save(fig, "loan_attribution_trend")

# 7-3. 渠道占比饼图
fig, ax = new_ax(figsize=(7.5, 6))
ax.pie(by_ch.values, labels=by_ch.index.astype(str), autopct="%1.1f%%",
       startangle=90, colors=plt.cm.Set2.colors[:len(by_ch)], textprops={"fontsize": 10})
ax.set_title("各渠道贷款申请量占比", loc="left", fontsize=14)
save(fig, "loan_attribution_pie")
