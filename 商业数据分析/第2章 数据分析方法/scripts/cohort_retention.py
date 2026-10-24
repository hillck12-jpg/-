# -*- coding: utf-8 -*-
"""复现第2章 1-4 同期群分析（Cohort Analysis）。

参考答案口径（来自 1-4同期群分析-参考.xlsx）：
- 用户登录明细：用户id / 注册日期 / 登录日期（13102 行）
- 产出：按注册月份分组的留存率三角矩阵（热力图）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "1-4同期群分析.xlsx", sheet_name="用户登录明细")
print("字段：", list(df.columns))
df.columns = [str(c).strip() for c in df.columns]
# 真实列：用户编号 / 注册日期 / 登录时点
reg_col = "注册日期"
login_col = "登录时点" if "登录时点" in df.columns else [c for c in df.columns if "登录" in c][0]
user_col = "用户编号"
df[reg_col] = pd.to_datetime(df[reg_col])
df[login_col] = pd.to_datetime(df[login_col])

# 4. 注册相对天数分桶（数据仅覆盖约1个月注册期，按天做同期群更有意义；
#    同时保留按月的列结构：相对月=0 全部为注册当月）
df["注册月"] = df[reg_col].dt.to_period("D")   # 以"注册日"为同期群
df["登录日偏移"] = (df[login_col].dt.normalize() - df[reg_col]).dt.days

# 6. 同期群矩阵：注册日 x 此后第 N 天是否活跃
cohort_size = df.groupby("注册月")[user_col].nunique()
pivot = df.pivot_table(index="注册月", columns="登录日偏移", values=user_col, aggfunc="nunique")
retention = pivot.div(cohort_size, axis=0).iloc[:, :14]  # 只看前14天留存

# 7. 绘制留存率热力图
fig, ax = plt.subplots(figsize=(13, 8))
sns.heatmap(retention, annot=True, fmt=".0%", cmap="Blues", cbar_kws={"label": "留存率"},
            linewidths=0.5, linecolor="white", ax=ax, annot_kws={"fontsize": 7})
ax.set_title("同期群分析：按注册日期的用户次日/周留存率", loc="left", fontsize=14)
ax.set_xlabel("注册后第 N 天", fontsize=12)
ax.set_ylabel("注册日期", fontsize=12)
ax.set_yticklabels([p.strftime("%m-%d") for p in retention.index], rotation=0, fontsize=7)
save(fig, "cohort_retention")
