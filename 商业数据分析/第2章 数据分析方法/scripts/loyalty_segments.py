# -*- coding: utf-8 -*-
"""复现第2章 1-3 用户忠诚度模型。

参考答案口径（来自 1-3用户忠诚度模型-参考.xlsx）：
- 销售流水表：订单编号/会员编号/消费日期/产品编号/消费金额，分析时点 2021-01-01
- 消费次数 = distinctcount(订单编号)，消费额 = sum(消费金额)
- 会员 1000+ 人，聚合到会员级别后画柱图：是否潜在&易流失用户两类
- 潜在&易流失口径：是否最近13周内消费 = 否（超过13周未消费 → 易流失；消费过但13周内无消费 → 潜在）
- 产出：两类用户的消费额与消费次数对比
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "1-3用户忠诚度模型.xlsx", sheet_name="销售流水表")
df["消费日期"] = pd.to_datetime(df["消费日期"])
SNAPSHOT = pd.Timestamp("2021-01-01")

# 4. 会员级聚合
member = df.groupby("会员编号").agg(
    消费次数=("订单编号", "nunique"),
    消费额=("消费金额", "sum"),
    最近消费=("消费日期", "max"),
)
member["距今天数"] = (SNAPSHOT - member["最近消费"]).dt.days

# 5. 忠诚度分类：13周=91天
member["用户类别"] = np.where(member["距今天数"] > 91, "易流失用户", "忠诚用户")

# 6. 两类用户消费额 / 消费次数汇总
seg_amt = member.groupby("用户类别")["消费额"].sum()
seg_cnt = member.groupby("用户类别")["消费次数"].sum()
seg_n = member.groupby("用户类别").size()

# 7. 绘制对比柱图
fig, axes = __import__("matplotlib.pyplot", fromlist=["subplots"]).subplots(1, 3, figsize=(14, 5))
for ax, series, title, unit in zip(
        axes, [seg_amt, seg_cnt, seg_n],
        ["各类用户消费额", "各类用户消费次数", "各类用户人数"],
        ["消费额（元）", "消费次数（次）", "人数（人）"]):
    bars = ax.bar(series.index, series.values, color=["#B22222", "#3A5FCD"], alpha=0.85, width=0.5)
    for b, v in zip(bars, series.values):
        ax.text(b.get_x() + b.get_width()/2, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=10)
    beautify(ax, title, "用户类别", unit)
    ax.yaxis.set_major_formatter(lambda x, p: f"{x/1000:.0f}千" if x >= 1000 else f"{x:.0f}")
save(fig, "loyalty_segments")
