# -*- coding: utf-8 -*-
"""复现第2章 1-2 RFM 模型。

参考答案口径（来自 1-2RFM模型-参考.xlsx）：
- 原始数据：用户编号/消费日期/消费金额 等（65989 行）
- R = 最近一次消费距今天数（分析基准日取数据中最大消费日期）
- F = 消费频次，M = 消费金额
- R/F/M 各按中位数分为 高/低，映射 8 类用户：
  重要价值/重要发展/重要保持/重要挽留/一般价值/一般发展/一般保持/一般挽留用户
- 产出：帕累托图（各用户类别消费金额柱 + 累计消费额百分比线）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "1-2RFM模型.xlsx", sheet_name="原始数据")
print("原始字段：", list(df.columns))
df.columns = [str(c).strip() for c in df.columns]
# 统一字段名
date_col = [c for c in df.columns if "日期" in c or "时间" in c][0]
amt_col = [c for c in df.columns if "金额" in c][0]
id_col = [c for c in df.columns if "用户" in c or "客户" in c][0]
df[date_col] = pd.to_datetime(df[date_col])

# 4. 计算 R/F/M
snapshot = df[date_col].max() + pd.Timedelta(days=1)
rfm = df.groupby(id_col).agg(
    R=(date_col, lambda s: (snapshot - s.max()).days),
    F=(date_col, "count"),
    M=(amt_col, "sum"),
)

# 5. 打分：以中位数为界分高/低
r_med, f_med, m_med = rfm["R"].median(), rfm["F"].median(), rfm["M"].median()
rfm["R程度"] = np.where(rfm["R"] <= r_med, "高", "低")
rfm["F程度"] = np.where(rfm["F"] >= f_med, "高", "低")
rfm["M程度"] = np.where(rfm["M"] >= m_med, "高", "低")

SEGMENTS = {
    ("高", "高", "高"): "重要价值用户", ("低", "高", "高"): "重要发展用户",
    ("高", "低", "高"): "重要保持用户", ("低", "低", "高"): "重要挽留用户",
    ("高", "高", "低"): "一般价值用户", ("低", "高", "低"): "一般发展用户",
    ("高", "低", "低"): "一般保持用户", ("低", "低", "低"): "一般挽留用户",
}
rfm["用户类别"] = [SEGMENTS[(r, f, m)] for r, f, m in zip(rfm["R程度"], rfm["F程度"], rfm["M程度"])]

# 6. 各用户类别消费金额 + 累计百分比（帕累托）
seg = rfm.groupby("用户类别")["M"].sum().sort_values(ascending=False)
cum_pct = seg.cumsum() / seg.sum()

# 7. 绘制帕累托图
fig, ax = new_ax(figsize=(10, 6))
bars = ax.bar(seg.index, seg.values, color="#3A5FCD", alpha=0.85)
for b, v in zip(bars, seg.values):
    ax.text(b.get_x() + b.get_width()/2, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=8)
plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=9)
beautify(ax, "各用户类别消费金额（RFM分层）", "用户类别", "消费金额")

ax2 = ax.twinx()
ax2.plot(seg.index, cum_pct.values * 100, color="#B22222", marker="o", lw=1.5)
ax2.set_ylim(0, 105)
ax2.set_ylabel("累计消费额百分比（%）", fontsize=12)
ax2.spines["top"].set_visible(False)
ax2.yaxis.set_major_formatter(lambda x, p: f"{x:.0f}%")
for x, y in zip(seg.index, cum_pct.values * 100):
    ax2.annotate(f"{y:.0f}%", (x, y), textcoords="offset points", xytext=(0, 8),
                 ha="center", fontsize=8, color="#B22222")
save(fig, "rfm_pareto")
