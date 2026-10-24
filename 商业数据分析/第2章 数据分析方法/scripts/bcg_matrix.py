# -*- coding: utf-8 -*-
"""复现第2章 1-1 波士顿矩阵（BCG Matrix）。

参考答案口径（来自 1-1波士顿矩阵-参考.xlsx）：
- x 轴 = 市场占有率（品牌销售额占比），y 轴 = 销售额环比（8月 vs 7月）
- 总市场环比增长率 0.0217，品牌平均市场占有率 0.0714 作为分隔线
- 数据：销售表（订单ID/销售日期/品牌/规格/单价/销量），2021-07、2021-08 两个月
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "1-1波士顿矩阵.xlsx", sheet_name="销售表")
df["销售日期"] = pd.to_datetime(df["销售日期"])
df["订单金额"] = df["单价"] * df["销量"]
df["月"] = df["销售日期"].dt.month

# 6. 分组聚合：各品牌 7月/8月 销售额
pv = df.pivot_table(index="品牌", columns="月", values="订单金额", aggfunc="sum").fillna(0)
total_share = pv[8] / pv[8].sum()                 # 市场占有率（销售额占比）
mom = (pv[8] - pv[7]) / pv[7]                     # 销售额环比
market_mom = (pv[8].sum() - pv[7].sum()) / pv[7].sum()
avg_share = total_share.mean()

# 7. 绘制波士顿矩阵散点
fig, ax = new_ax(figsize=(9, 7))
ax.scatter(total_share, mom, s=total_share * 3000, alpha=0.55,
           color="#3A5FCD", edgecolors="white", linewidths=1.5)
for brand, x, y in zip(total_share.index, total_share, mom):
    ax.annotate(brand, (x, y), ha="center", va="center", fontsize=9, weight="bold", color="white")
ax.axvline(avg_share, color="gray", ls="--", lw=1)
ax.axhline(market_mom, color="gray", ls="--", lw=1)

# 象限标注
xmin, xmax = ax.get_xlim(); ymin, ymax = ax.get_ylim()
ax.text(xmax * 0.99, ymax * 0.95, "明星产品", ha="right", fontsize=11, color="#B22222", weight="bold")
ax.text(xmin * 0.99, ymax * 0.95, "问题产品", ha="left", fontsize=11, color="#E8A33D", weight="bold")
ax.text(xmin * 0.99, ymin * 0.95, "瘦狗产品", ha="left", fontsize=11, color="gray", weight="bold")
ax.text(xmax * 0.99, ymin * 0.95, "现金牛产品", ha="right", fontsize=11, color="#2E8B57", weight="bold")

# 8. 图表美化
beautify(ax, "品牌波士顿矩阵（2021年8月）", "市场占有率（销售额占比）", "销售额环比")
ax.text(0.99, -0.12, f"总市场环比增长率={market_mom:.3f}  品牌平均占有率={avg_share:.3f}",
        transform=ax.transAxes, ha="right", fontsize=8, color="gray")
save(fig, "bcg_matrix")
