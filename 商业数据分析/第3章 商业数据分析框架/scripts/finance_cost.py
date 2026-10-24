# -*- coding: utf-8 -*-
"""复现第3章案例2《财务费用分析》：三大期间费用7月较6月增长、管理费用环比、总费用对比。

原始数据：总费用数据（年份/月份/金额）、财务三大期间费用数据（年份/月份/期间费用项/金额）、
管理费用数据（年份/份/管理费用项/金额）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np

# 2. 读取数据
total = pd.read_excel(DATA_DIR / "案例2：财务费用分析-原始数据.xlsx", sheet_name="总费用数据")
detail = pd.read_excel(DATA_DIR / "案例2：财务费用分析-原始数据.xlsx", sheet_name="财务三大期间费用数据")
admin = pd.read_excel(DATA_DIR / "案例2：财务费用分析-原始数据.xlsx", sheet_name="管理费用数据")

# 6. 分组聚合：6月 vs 7月
def by_month(d, val="金额"):
    return d.groupby("月份")[val].sum()

m_total = by_month(total)                      # 总费用
m_detail = detail.pivot_table(index="期间费用项", columns="月份", values="金额", aggfunc="sum")
m_admin = admin.pivot_table(index="管理费用项", columns="份", values="金额", aggfunc="sum")

# 7-1. 三大期间财务费用7月较6月增长情况（对比柱图）
fig, ax = new_ax(figsize=(9, 5))
x = range(len(m_detail))
w = 0.35
b1 = ax.bar([i - w/2 for i in x], m_detail[6], w, label="6月", color="#3A5FCD", alpha=0.85)
b2 = ax.bar([i + w/2 for i in x], m_detail[7], w, label="7月", color="#E8A33D", alpha=0.85)
ax.set_xticks(list(x)); ax.set_xticklabels(m_detail.index, fontsize=10)
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height(), f"{b.get_height():,.0f}",
                ha="center", va="bottom", fontsize=8)
beautify(ax, "三大期间财务费用7月较6月增长情况", "期间费用项", "金额（元）")
ax.legend(frameon=False)
save(fig, "finance_cost_three_period")

# 7-2. 管理费用7月环比增长分析
fig, ax = new_ax(figsize=(9, 5))
x = range(len(m_admin))
b1 = ax.bar([i - w/2 for i in x], m_admin[6], w, label="6月", color="#3A5FCD", alpha=0.85)
b2 = ax.bar([i + w/2 for i in x], m_admin[7], w, label="7月", color="#E8A33D", alpha=0.85)
ax.set_xticks(list(x)); ax.set_xticklabels(m_admin.index, fontsize=9, rotation=20, ha="right")
beautify(ax, "管理费用7月环比增长分析", "管理费用项", "金额（元）")
ax.legend(frameon=False)
save(fig, "finance_cost_admin")

# 7-3. 总财务费用对比
fig, ax = new_ax(figsize=(7, 5))
b = ax.bar([str(i) + "月" for i in m_total.index], m_total.values, color="#3A5FCD", alpha=0.85, width=0.5)
for bb, v in zip(b, m_total.values):
    ax.text(bb.get_x() + bb.get_width()/2, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
beautify(ax, "总财务费用对比", "月份", "金额（元）")
save(fig, "finance_cost_total")
