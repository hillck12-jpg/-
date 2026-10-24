# -*- coding: utf-8 -*-
"""复现第2章 3-1 相关分析。

参考答案口径（来自 3-1相关分析-参考.xlsx）：
- 原始数据：59 行 2 列连续变量（背景：探究两个连续变量间的相关关系）
- 产出：散点图 + 相关系数 r 标注 + 拟合线
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "3-1相关分析.xlsx", sheet_name="原始数据")
print("字段：", list(df.columns))
cols = list(df.select_dtypes("number").columns)
x_col, y_col = cols[0], cols[1]
x, y = df[x_col], df[y_col]

# 4. 相关系数
r = x.corr(y)

# 7. 散点图 + 拟合线
fig, ax = new_ax(figsize=(8, 6))
ax.scatter(x, y, alpha=0.7, color="#3A5FCD", edgecolors="white", s=50)
k, b = np.polyfit(x, y, 1)
xs = np.linspace(x.min(), x.max(), 100)
ax.plot(xs, k * xs + b, color="#B22222", lw=1.5, ls="--")

# 8. 图表美化
beautify(ax, f"相关分析：{x_col} 与 {y_col}", x_col, y_col)
ax.text(0.03, 0.95, f"Pearson r = {r:.3f}", transform=ax.transAxes,
        fontsize=12, color="#B22222", weight="bold", va="top")
save(fig, "correlation_scatter")
