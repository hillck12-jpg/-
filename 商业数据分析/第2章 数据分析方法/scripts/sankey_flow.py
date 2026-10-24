# -*- coding: utf-8 -*-
"""复现第2章 六类分析方法 6桑基图（对应 PBIX 参考答案 第6页 SankeyDiagram）。

数据（6桑吉图.xlsx Sheet1）：ID/来源/目标/流量（16 条网站访问流向）
实现：matplotlib 手绘桑基图（数据坐标下用多边形填充流带，宽度=流量，无 plotly 依赖）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "6桑吉图.xlsx", sheet_name="Sheet1")
df.columns = [str(c).strip() for c in df.columns]
df = df.dropna(subset=["来源", "目标"])
df["流量"] = pd.to_numeric(df["流量"], errors="coerce").fillna(0)

# 4. 节点与层级（拓扑排序）
nodes = list(dict.fromkeys(df["来源"].tolist() + df["目标"].tolist()))
out_sum = df.groupby("来源")["流量"].sum()
in_sum = df.groupby("目标")["流量"].sum()

level = {n: 0 for n in nodes}
changed = True
while changed:
    changed = False
    for _, r in df.iterrows():
        s, t = r["来源"], r["目标"]
        if level[t] <= level[s]:
            level[t] = level[s] + 1
            changed = True
levels = {}
for n, lv in level.items():
    levels.setdefault(lv, []).append(n)

# 6. 节点坐标（y 已归一化到 0-1 区间）
GAP = 0.04
node_pos, node_height = {}, {}
col_totals = {lv: sum(max(out_sum.get(n, 0), in_sum.get(n, 0)) for n in ns)
              for lv, ns in levels.items()}
max_total = max(col_totals.values())
for lv, ns in levels.items():
    total = col_totals[lv]
    y = (1.0 - total / max_total) / 2
    for n in ns:
        h = max(out_sum.get(n, 0), in_sum.get(n, 0)) / max_total
        node_pos[n] = (lv, y + h / 2)
        node_height[n] = h
        y += h + GAP

# 7. 绘制
fig, ax = plt.subplots(figsize=(12, 7), dpi=100)
cmap = plt.cm.tab20
node_colors = {n: cmap(i / max(len(nodes) - 1, 1)) for i, n in enumerate(nodes)}
max_x = max(l for l, _ in node_pos.values())

# 流带：数据坐标下构造闭合多边形（上下边界各一条贝塞尔近似折线），宽度=流量
link_offset = {}
for _, r in df.iterrows():
    s, t, v = r["来源"], r["目标"], r["流量"]
    x0, yc0 = node_pos[s]
    x1, yc1 = node_pos[t]
    h = v / max_total
    key0, key1 = ("out", s), ("in", t)
    off0 = link_offset.get(key0, -node_height[s] / 2)
    off1 = link_offset.get(key1, -node_height[t] / 2)
    ys0 = yc0 + off0          # 流带在源节点上的下缘
    ys1 = yc1 + off1          # 流带在目标节点上的下缘
    link_offset[key0] = off0 + h
    link_offset[key1] = off1 + h
    xm = (x0 + x1) / 2
    # 上边缘：源上缘 → 中线上缘 → 目标上缘；下边缘反向
    verts_top = [(x0 + 0.0125, ys0 + h), (xm, ys0 + h), (xm, ys1 + h), (x1 - 0.0125, ys1 + h)]
    verts_bot = [(x1 - 0.0125, ys1), (xm, ys1), (xm, ys0), (x0 + 0.0125, ys0)]
    verts = verts_top + verts_bot + [verts_top[0]]
    codes = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4,
             MPath.LINETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.CLOSEPOLY]
    patch = PathPatch(MPath(verts, codes), facecolor=node_colors[s],
                      edgecolor="none", alpha=0.35, zorder=1)
    ax.add_patch(patch)

# 节点条与标签
for n, (x, yc) in node_pos.items():
    ax.barh(yc, 0.025, left=x - 0.0125, height=node_height[n],
            color=node_colors[n], edgecolor="white", zorder=3)
    ha = "left" if x == max_x else "right"
    x_text = x + 0.03 if ha == "left" else x - 0.03
    ax.text(x_text, yc, str(n), ha=ha, va="center", fontsize=9)

ax.set_xlim(-0.15, max_x + 0.15)
ax.set_ylim(-0.02, 1.05)
ax.set_autoscale_on(False)
ax.axis("off")
ax.set_title("网站访问流向桑基图", loc="left", fontsize=14)
FIG_DIR = Path(__file__).resolve().parents[1] / "figures"
FIG_DIR.mkdir(exist_ok=True)
out = FIG_DIR / "sankey_flow.png"
fig.savefig(out, dpi=150)
plt.close(fig)
print(f"已保存: {out}")
