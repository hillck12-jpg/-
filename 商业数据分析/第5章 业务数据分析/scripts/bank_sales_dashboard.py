# -*- coding: utf-8 -*-
"""复现第5章 PBIX⑩《银行案例》业务看板。

Layout 解析结果（案例结果.pbix）：
V1 card 购买金额 + MTD销售目标达成率
V2 decompositionTree 购买金额 → 学历 → 家庭年收入 → 年龄 → 性别（此处用分维柱图替代）
V3 clusteredColumn 品类 x 风险偏好 购买金额
V4 combo 品类 x 购买金额(柱) + 期限(线)
V5/V6 WordCloud 选择本行的原因 / 购买目的

数据：银行案例数据 - 学员用.xlsx（销售数据 + 三张说明表）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 读取数据
XL = DATA_DIR / "银行案例数据 - 学员用.xlsx"
sales = pd.read_excel(XL, sheet_name="销售数据")
cat_map = pd.read_excel(XL, sheet_name="品类说明表")
edu_map = pd.read_excel(XL, sheet_name="学历说明表")
risk_map = pd.read_excel(XL, sheet_name="风险偏好说明表")
print("销售数据字段：", list(sales.columns))

sales.columns = [str(c).strip() for c in sales.columns]
amt_col = [c for c in sales.columns if "购买金额" in c][0]
term_col = [c for c in sales.columns if "期限" in c][0]
cat_col = [c for c in sales.columns if "品类" in c][0]
risk_col = [c for c in sales.columns if "风险" in c][0]
edu_col = [c for c in sales.columns if "学历" in c][0]
reason_col = [c for c in sales.columns if "原因" in c][0]
purpose_col = [c for c in sales.columns if "目的" in c][0]
sales[amt_col] = pd.to_numeric(sales[amt_col], errors="coerce").fillna(0)

# 关联说明表（品类名称 / 学历名称）
cat_key = [c for c in cat_map.columns if "编号" in c][0]
cat_name_col = [c for c in cat_map.columns if "名称" in c][0]
sales = sales.merge(cat_map[[cat_key, cat_name_col]], left_on=cat_col, right_on=cat_key, how="left")

TARGET = 25_000_000  # 业务描述：本月销售目标 2500 万
total_amt = sales[amt_col].sum()

# 7-1. KPI 卡
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.axis("off")
kpis = [("购买金额", f"{total_amt:,.0f}"),
        ("MTD达成率", f"{total_amt/TARGET:.1%}"),
        ("销售目标", f"{TARGET:,}")]
for i, (t, v) in enumerate(kpis):
    ax.text(0.18 + i * 0.32, 0.6, v, ha="center", fontsize=17, weight="bold", color="#1F3B8C")
    ax.text(0.18 + i * 0.32, 0.22, t, ha="center", fontsize=12, color="#666666")
ax.set_title("银行理财产品销售 KPI（本月目标 2500 万）", loc="left", fontsize=14)
save(fig, "bank_kpi_cards")

# 7-2. 品类 x 风险偏好 购买金额（簇状柱图）
pv = sales.pivot_table(index=cat_name_col, columns=risk_col, values=amt_col, aggfunc="sum").fillna(0)
fig, ax = new_ax(figsize=(12, 5.5))
pv.plot(kind="bar", ax=ax, alpha=0.85, width=0.75,
        color=plt.cm.Set2.colors[:pv.shape[1]])
beautify(ax, "各品类在不同风险偏好客户的购买金额", "品类", "购买金额（元）")
plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=9)
ax.legend(title="风险偏好", frameon=False, fontsize=9)
save(fig, "bank_category_risk")

# 7-3. 品类购买金额(柱) + 平均期限(线) 组合图
by_cat = sales.groupby(cat_name_col).agg(购买金额=(amt_col, "sum"), 平均期限=(term_col, "mean"))
fig, ax = new_ax(figsize=(11, 5.5))
bars = ax.bar(by_cat.index, by_cat["购买金额"], color="#3A5FCD", alpha=0.85, label="购买金额")
ax2 = ax.twinx()
ax2.plot(by_cat.index, by_cat["平均期限"], color="#B22222", marker="o", lw=1.5, label="平均期限")
ax2.set_ylabel("平均期限（月）", fontsize=12)
ax2.spines["top"].set_visible(False)
plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=9)
beautify(ax, "各品类购买金额与平均期限", "品类", "购买金额（元）")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False)
save(fig, "bank_category_term")

# 7-4/7-5. 词云：选择本行的原因 / 购买目的
from wordcloud import WordCloud
for col, name in [(reason_col, "bank_wordcloud_reason"), (purpose_col, "bank_wordcloud_purpose")]:
    text = " ".join(sales[col].dropna().astype(str))
    wc = WordCloud(font_path=r"C:\Windows\Fonts\simhei.ttf", width=900, height=500,
                   background_color="white", colormap="tab10").generate(text)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("客户选择本行的原因词云" if "原因" in col else "客户购买目的词云",
                 loc="left", fontsize=14)
    save(fig, name)

# 7-6. 分解树替代：学历 → 家庭年收入 → 性别 购买金额
edu_name = [c for c in edu_map.columns if "名称" in c][0]
edu_key = [c for c in edu_map.columns if "编号" in c][0]
sales2 = sales.merge(edu_map[[edu_key, edu_name]], left_on=edu_col, right_on=edu_key, how="left")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for ax, col, title in zip(
        axes, [edu_name, "家庭年收入", "性别"],
        ["按学历", "按家庭年收入", "按性别"]):
    d = sales2.groupby(col)[amt_col].sum().sort_values(ascending=False)
    ax.bar(d.index.astype(str), d.values, color="#3A5FCD", alpha=0.85)
    beautify(ax, f"购买金额{title}", "", "购买金额（元）")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(lambda x, p: f"{x/1e4:.0f}万" if x >= 1e4 else f"{x:.0f}")
save(fig, "bank_decompose_tree")
