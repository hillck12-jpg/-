# -*- coding: utf-8 -*-
"""复现第9章 用户标签体系与用户画像：银行客户基础画像。

数据（data/ 下的 KDD99 银行 8 表，与第1章同源）：
- clients（客户）：client_id/sex/birth_date/district_id
- disp（处置权）：disp_id/client_id/account_id/type
- loans（贷款）：loan_id/account_id/date/amount/duration/payments/status
- card（卡）：card_id/disp_id/type/issued
产出（对应 信用卡客户画像 看板风格）：
- 客户性别分布（饼图）
- 客户年龄分布（直方图 + 分性别）
- 贷款金额按年趋势（面积图）
- 贷款状态分布（柱图）
- 各年龄段贷款金额（柱图）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 读取数据（gbk 编码）
clients = pd.read_csv(DATA_DIR / "clients.csv", encoding="gbk")
disp = pd.read_csv(DATA_DIR / "disp.csv", encoding="gbk")
loans = pd.read_csv(DATA_DIR / "loans.csv", encoding="gbk")
cards = pd.read_csv(DATA_DIR / "card.csv", encoding="gbk")
print("clients:", list(clients.columns), "| loans:", list(loans.columns))

# 3. 统一关联键
for d, keys in [(clients, ["client_id"]), (disp, ["client_id", "account_id"]),
                (loans, ["account_id"]), (cards, ["disp_id"])]:
    for k in keys:
        d[k] = d[k].astype(str).str.strip()

# 4. 特征提取
SNAPSHOT = pd.Timestamp("1999-12-31")
clients["birth_date"] = pd.to_datetime(clients["birth_date"], errors="coerce")
clients["年龄"] = (SNAPSHOT - clients["birth_date"]).dt.days / 365.25
clients["年龄区间"] = pd.cut(clients["年龄"], bins=[0, 25, 35, 45, 55, 65, 100],
                            labels=["≤25", "26-35", "36-45", "46-55", "56-65", "65+"])

loans["date"] = pd.to_datetime(loans["date"], format="%y%m%d", errors="coerce")
if loans["date"].isna().all():
    loans["date"] = pd.to_datetime(loans["date"], errors="coerce")
loans["年"] = loans["date"].dt.year
loans["amount"] = pd.to_numeric(loans["amount"], errors="coerce").fillna(0)

# 5. 关联：贷款 → 处置（所有者）→ 客户
disp_owner = disp[disp["type"].astype(str).str.contains("所有者|OWNER", case=False, na=False)]
loan_client = loans.merge(disp_owner, on="account_id", how="inner") \
                    .merge(clients, on="client_id", how="inner")

# 7-1. 客户性别分布
sex = clients["sex"].value_counts()
fig, ax = new_ax(figsize=(7, 5.5))
ax.pie(sex.values, labels=sex.index, autopct="%1.1f%%", startangle=90,
       colors=["#3A5FCD", "#E8A33D"], textprops={"fontsize": 11})
ax.set_title("客户性别分布", loc="left", fontsize=14)
save(fig, "profile_sex_dist")

# 7-2. 客户年龄分布（分性别直方图）
fig, ax = new_ax(figsize=(10, 5.5))
for sex_name, color in zip(sex.index, ["#3A5FCD", "#E8A33D"]):
    ax.hist(clients.loc[clients["sex"] == sex_name, "年龄"].dropna(), bins=20,
            alpha=0.6, label=sex_name, color=color, edgecolor="white")
beautify(ax, "客户年龄分布（分性别）", "年龄（岁）", "人数")
ax.legend(frameon=False)
save(fig, "profile_age_dist")

# 7-3. 贷款金额按年面积图
by_year = loans.groupby("年")["amount"].sum()
fig, ax = new_ax(figsize=(10, 5.5))
ax.fill_between([str(y) for y in by_year.index], by_year.values, alpha=0.75, color="#3A5FCD")
ax.plot([str(y) for y in by_year.index], by_year.values, color="#1F3B8C", lw=1.5)
beautify(ax, "贷款金额按年变化", "年份", "贷款金额（元）")
ax.yaxis.set_major_formatter(lambda x, p: f"{x/1e6:.0f}百万")
save(fig, "profile_loan_by_year")

# 7-4. 贷款状态分布
status_col = [c for c in loans.columns if "status" in c.lower() or "状态" in c]
if status_col:
    st = loans[status_col[0]].value_counts()
    fig, ax = new_ax(figsize=(8, 5.5))
    bars = ax.bar(st.index.astype(str), st.values, color="#2E8B57", alpha=0.85, width=0.55)
    for b, v in zip(bars, st.values):
        ax.text(b.get_x() + b.get_width()/2, v, int(v), ha="center", va="bottom", fontsize=10)
    beautify(ax, "贷款状态分布", "贷款状态", "笔数")
    save(fig, "profile_loan_status")

# 7-5. 各年龄段贷款金额（贷款客户画像）
by_age = loan_client.groupby("年龄区间", observed=True)["amount"].sum()
fig, ax = new_ax(figsize=(9, 5.5))
bars = ax.bar(by_age.index.astype(str), by_age.values, color="#3A5FCD", alpha=0.85, width=0.55)
for b, v in zip(bars, by_age.values):
    ax.text(b.get_x() + b.get_width()/2, v, f"{v/1e6:.1f}百万", ha="center", va="bottom", fontsize=9)
beautify(ax, "各年龄段客户贷款金额", "年龄区间", "贷款金额（元）")
save(fig, "profile_loan_by_age")

# 7-6. 持卡类型分布
type_col = [c for c in cards.columns if "type" in c.lower() or "类型" in c]
if type_col:
    ct = cards[type_col[0]].value_counts()
    fig, ax = new_ax(figsize=(7.5, 5.5))
    ax.pie(ct.values, labels=ct.index.astype(str), autopct="%1.1f%%", startangle=90,
           colors=plt.cm.Set2.colors[:len(ct)], textprops={"fontsize": 10})
    ax.set_title("银行卡类型分布", loc="left", fontsize=14)
    save(fig, "profile_card_type")
