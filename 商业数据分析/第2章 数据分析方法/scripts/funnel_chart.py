# -*- coding: utf-8 -*-
"""复现第2章 2-1 漏斗图。

参考答案口径（来自 2-1漏斗图-参考.xlsx）：
- 演示 sheet：各环节转化（访问→注册→加购→下单→支付 等典型电商漏斗）
- 产出：居中对称漏斗图（matplotlib 梯形绘制）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, save
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# 2. 读取数据（练习 sheet 或演示 sheet，取行数多且像漏斗的那个）
xl = pd.ExcelFile(DATA_DIR / "2-1漏斗图.xlsx")
best = None
for sh in xl.sheet_names:
    d = xl.parse(sh, header=None)
    if d.shape[0] >= 5 and d.shape[1] >= 3:
        best = (sh, d)
if best is None:
    best = (xl.sheet_names[0], xl.parse(xl.sheet_names[0], header=None))
sh, raw = best
print(f"使用 sheet: {sh} shape={raw.shape}")
print(raw.head(8).to_string())

# 4. 提取环节名与数值：练习 sheet 结构为 B=环节名, C=人数（表头在第2行）
vals = None
for c in raw.columns:
    s = pd.to_numeric(raw[c], errors="coerce").dropna()
    if len(s) >= 3 and (s <= 1).mean() < 0.5:
        vals = s
        break
vals = vals[vals > 0]
# 环节名取数值行左侧最近的非空文本
def pick_name(idx):
    row = raw.loc[idx]
    for c in raw.columns:
        v = row[c]
        if isinstance(v, str) and v.strip():
            return v.strip()
    return f"环节{idx}"
names = [pick_name(i) for i in vals.index]
values = vals.astype(float).tolist()

# 7. 绘制居中漏斗（数据可能非单调，梯形宽度按归一化值直接呈现）
fig, ax = new_ax(figsize=(9, 6))
max_v = max(values)
n = len(values)
colors = plt.cm.Blues([0.85 - 0.6 * i / max(n - 1, 1) for i in range(n)])
BAR_H = 0.8
for i, (name, v) in enumerate(zip(names, values)):
    w = max(v / max_v, 0.03)          # 最小可视宽度
    y_top, y_bot = n - i, n - i - BAR_H
    poly = Polygon([(-w / 2, y_top), (w / 2, y_top),
                    (w / 2, y_bot), (-w / 2, y_bot)],
                   closed=True, facecolor=colors[i], edgecolor="white", lw=2)
    ax.add_patch(poly)
    ax.text(0, (y_top + y_bot) / 2, f"{name}  {v:,.0f}  ({v/max_v:.1%})",
            ha="center", va="center", fontsize=11,
            color="white" if i < n / 2 else "#1F3B8C", weight="bold")
    if i + 1 < n and values[i] > 0:
        rate = values[i + 1] / values[i]
        ax.text(0.62, (y_top + y_bot) / 2, f"转化率 {rate:.1%}",
                ha="left", va="center", fontsize=9, color="#666666")

ax.set_xlim(-0.75, 0.85)
ax.set_ylim(0, n)
ax.axis("off")
ax.set_title("转化漏斗分析", loc="left", fontsize=14)
save(fig, "funnel_chart")
