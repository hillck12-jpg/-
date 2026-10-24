# -*- coding: utf-8 -*-
"""复现第2章 六类分析方法 5关系分析（对应 PBIX 参考答案 第5页）。

数据（5关系分析.xlsx 关系图 sheet）三个子表：
- B:D  不同营销活动客户下单情况对比（堆积百分比柱图，参考答案 V2）
- L:O  用户id/营销活动1/2/3 销售金额（柱图对比）
- X:Z  投入成本/产出收益（散点图，参考答案 V1）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 读取数据
raw = pd.read_excel(DATA_DIR / "5关系分析.xlsx", sheet_name="关系图", header=None)

# 子表1：地区/人数（下单用户 vs 未下单用户），位于 B:D，表头在第3行
d1 = raw.iloc[3:, 1:4].dropna(how="all").reset_index(drop=True)
d1.columns = ["地区", "下单用户", "未下单用户"]
d1 = d1[d1["地区"].notna()]
d1["下单用户"] = pd.to_numeric(d1["下单用户"], errors="coerce")
d1["未下单用户"] = pd.to_numeric(d1["未下单用户"], errors="coerce")
d1 = d1.dropna()

# 子表2：用户id / 三个营销活动销售金额，位于 L:O，表头在第2行
d2 = raw.iloc[2:, 10:14].dropna(how="all").reset_index(drop=True)
d2.columns = ["标题", "用户id", "营销活动1", "营销活动2"]
d2 = d2[pd.to_numeric(d2["营销活动1"], errors="coerce").notna()]

# 子表3：产出收益 vs 投入成本（X1="产出收益"为数值列起头，实际数据在 24/25 列附近）
# 稳妥做法：扫描第 20 列之后，找表头含"产出收益/投入成本"的相邻两列
d3 = None
for c in range(18, raw.shape[1] - 1):
    h1, h2 = str(raw.iloc[0, c]), str(raw.iloc[0, c + 1])
    if "产出" in h1 and "投入" in h2:
        d3 = raw.iloc[1:, [c, c + 1]].copy()
        d3.columns = ["产出收益", "投入成本"]
        break
if d3 is None:
    # 回退：直接取最后一两列
    d3 = raw.iloc[1:, [-2, -1]].copy()
    d3.columns = ["产出收益", "投入成本"]
d3 = d3.apply(pd.to_numeric, errors="coerce").dropna()
d3 = d3[(d3["产出收益"] > 0) & (d3["投入成本"] > 0)]
print("散点子表行数：", len(d3), "列位置扫描完成")

# 7-1. 散点图：投入成本 vs 产出收益
fig, ax = new_ax(figsize=(8, 6))
ax.scatter(d3["投入成本"], d3["产出收益"], alpha=0.7, color="#3A5FCD",
           edgecolors="white", s=55)
k, b = np.polyfit(d3["投入成本"], d3["产出收益"], 1)
xs = np.linspace(d3["投入成本"].min(), d3["投入成本"].max(), 50)
ax.plot(xs, k * xs + b, color="#B22222", lw=1.5, ls="--")
r = d3["投入成本"].corr(d3["产出收益"])
beautify(ax, f"投入成本与产出收益关系（r={r:.2f}）", "投入成本（元）", "产出收益（元）")
save(fig, "relation_scatter")

# 7-2. 100% 堆积柱图：各营销活动下单 vs 未下单
fig, ax = new_ax(figsize=(10, 5.5))
tot = d1["下单用户"] + d1["未下单用户"]
p1 = d1["下单用户"] / tot * 100
p2 = d1["未下单用户"] / tot * 100
ax.bar(d1["地区"], p1, label="下单用户", color="#3A5FCD", alpha=0.85)
ax.bar(d1["地区"], p2, bottom=p1, label="未下单用户", color="#E8A33D", alpha=0.85)
ax.set_ylim(0, 100)
ax.yaxis.set_major_formatter(lambda x, p: f"{x:.0f}%")
plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=9)
beautify(ax, "不同地区客户下单情况对比", "地区", "人数占比")
ax.legend(frameon=False, loc="upper right")
save(fig, "relation_stacked_pct")

# 7-3. 营销活动销售金额对比（三个活动柱图）
acts = ["营销活动1", "营销活动2", "营销活动3"]
raw2 = raw.iloc[2:, 10:14].reset_index(drop=True)
raw2.columns = ["标题", "用户id", "营销活动1", "营销活动2"]
# 营销活动3在 N 列（13）
raw3 = pd.read_excel(DATA_DIR / "5关系分析.xlsx", sheet_name="关系图", header=1, usecols=[11, 12, 13]).dropna(how="all")
raw3.columns = ["用户id", "营销活动1", "营销活动2"]
act3 = pd.read_excel(DATA_DIR / "5关系分析.xlsx", sheet_name="关系图", header=1, usecols=[13]).dropna()
act3.columns = ["营销活动3"]
vals = {
    "营销活动1": pd.to_numeric(raw3["营销活动1"], errors="coerce").sum(),
    "营销活动2": pd.to_numeric(raw3["营销活动2"], errors="coerce").sum(),
    "营销活动3": pd.to_numeric(act3["营销活动3"], errors="coerce").sum(),
}
fig, ax = new_ax(figsize=(8, 5.5))
bars = ax.bar(list(vals.keys()), list(vals.values()), color=["#3A5FCD", "#E8A33D", "#2E8B57"], alpha=0.85, width=0.5)
for b, v in zip(bars, vals.values()):
    ax.text(b.get_x() + b.get_width()/2, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=10)
beautify(ax, "各营销活动销售金额对比", "营销活动", "销售金额（元）")
save(fig, "relation_campaign_sales")
