# -*- coding: utf-8 -*-
"""复现第2章 PBIX⑥《人力资源看板》（DAX 函数练习 - 人力案例）。

Layout 解析结果：
V3 clusteredBar 年龄区间 x 员工人数/期末在职/离职 | V4 multiRowCard 员工人数/离职率等
V5 areaChart 年月 x 员工人数/离职人数 | V6 tableEx 员工在职天数明细

数据：员工信息.xlsx（员工工号/姓名/部门/入职日期/离职日期/员工状态/文化程度/年龄...）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "员工信息.xlsx", sheet_name="员工信息")
print("字段：", list(df.columns))
df.columns = [str(c).strip() for c in df.columns]
in_col = [c for c in df.columns if "入职" in c][0]
out_col = [c for c in df.columns if "离职" in c and "日期" in c]
status_col = [c for c in df.columns if "状态" in c]
out_col = out_col[0] if out_col else None
df[in_col] = pd.to_datetime(df[in_col], errors="coerce")
if out_col:
    df[out_col] = pd.to_datetime(df[out_col], errors="coerce")

SNAPSHOT = pd.Timestamp("2023-12-31")

# 4. 在职天数
df["在职天数"] = np.where(
    df[out_col].notna() if out_col else False,
    (df[out_col] - df[in_col]).dt.days,
    (SNAPSHOT - df[in_col]).dt.days)
df["在职天数"] = df["在职天数"].clip(lower=0)

# 5. 年龄区间
age_col = [c for c in df.columns if "年龄" in c]
if age_col:
    df["年龄区间"] = pd.cut(pd.to_numeric(df[age_col[0]], errors="coerce"),
                          bins=[0, 25, 30, 35, 40, 45, 50, 100],
                          labels=["≤25", "26-30", "31-35", "36-40", "41-45", "46-50", "50+"])

# 6. 指标
total = len(df)
is_on = df[status_col[0]].astype(str).str.contains("在职| active", case=False, na=False) \
    if status_col else df[out_col].isna() if out_col else pd.Series(True, index=df.index)
on_job = int(is_on.sum())
left = total - on_job

# 7-1. 年龄区间 x 在职/离职堆积条形图
if age_col:
    pv = df.groupby(["年龄区间", is_on.map({True: "在职", False: "离职"})]).size().unstack(fill_value=0)
    fig, ax = new_ax(figsize=(9, 5.5))
    pv.plot(kind="bar", stacked=True, ax=ax, color=["#3A5FCD", "#B22222"], alpha=0.85)
    beautify(ax, "各年龄区间在职/离职人数", "年龄区间", "人数（人）")
    ax.legend(title="", frameon=False)
    save(fig, "hr_age_status")

# 7-2. 在职/离职人数 KPI 卡
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.axis("off")
kpis = [("员工总数", f"{total}"), ("期末在职", f"{on_job}"), ("离职人数", f"{left}"),
        ("离职率", f"{left/total:.1%}")]
for i, (t, v) in enumerate(kpis):
    ax.text(0.125 + i * 0.25, 0.6, v, ha="center", fontsize=18, weight="bold", color="#1F3B8C")
    ax.text(0.125 + i * 0.25, 0.22, t, ha="center", fontsize=12, color="#666666")
ax.set_title("人力资源 KPI 概览", loc="left", fontsize=14)
save(fig, "hr_kpi_cards")

# 7-3. 各年月在职/离职人数面积图
df["入职年月"] = df[in_col].dt.to_period("M").astype(str)
hired = df.groupby("入职年月").size()
if out_col:
    df_left = df[df[out_col].notna()].copy()
    df_left["离职年月"] = df_left[out_col].dt.to_period("M").astype(str)
    lefted = df_left.groupby("离职年月").size()
    idx = sorted(set(hired.index) | set(lefted.index))
    hired = hired.reindex(idx, fill_value=0)
    lefted = lefted.reindex(idx, fill_value=0)
    fig, ax = new_ax(figsize=(11, 5.5))
    ax.stackplot(idx, hired.values, lefted.values, labels=["入职人数", "离职人数"],
                 colors=["#3A5FCD", "#B22222"], alpha=0.8)
    beautify(ax, "各年月入职/离职人数", "年月", "人数（人）")
    ax.legend(frameon=False, loc="upper left")
    ax.set_xticks(ax.get_xticks()[::max(1, len(idx) // 12)])
    save(fig, "hr_hire_leave_area")

# 7-4. 各部门在职天数均值条形图
dept_col = [c for c in df.columns if "部门" in c]
if dept_col:
    d = df.groupby(dept_col[0])["在职天数"].mean().sort_values()
    fig, ax = new_ax(figsize=(9, 5.5))
    ax.barh(d.index.astype(str), d.values, color="#2E8B57", alpha=0.85)
    beautify(ax, "各部门平均在职天数", "在职天数（天）", "部门")
    save(fig, "hr_days_by_dept")
