# -*- coding: utf-8 -*-
"""复现第3章案例3《电商平台的精准营销》：4 张分析图。

业务需求（来自完整案例 xlsx）：
1. 购买客户的性别分布（饼图）
2. 女性消费客户的年龄段分布（饼图）
3. 50岁以上的女性客户的消费品类分布（柱图）
4. 50岁以上女性服饰和护肤品消费人群的支付方式分布（柱图）

原始数据字段：客户ID/性别/年龄/品类/数量/支付方式/订单月份/订单年份
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import matplotlib.pyplot as plt

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "案例3：电商平台的精准营销-原始数据.xlsx")

# 4. 特征提取：年龄段（10岁一档）
df["年龄段"] = pd.cut(df["年龄"], bins=range(10, 81, 10),
                     labels=["10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80"],
                     right=False)

# 7-1. 购买客户的性别分布
sex = df["性别"].value_counts()
fig, ax = new_ax(figsize=(7, 5.5))
ax.pie(sex.values, labels=sex.index, autopct="%1.1f%%", startangle=90,
       colors=["#3A5FCD", "#E8A33D"], textprops={"fontsize": 11})
ax.set_title("购买客户的性别分布", loc="left", fontsize=14)
save(fig, "ecommerce_sex_dist")

# 7-2. 女性消费客户的年龄段分布
female = df[df["性别"] == "Female"]
age_f = female["年龄段"].value_counts().sort_index()
fig, ax = new_ax(figsize=(8, 5.5))
ax.pie(age_f.values, labels=age_f.index, autopct="%1.1f%%", startangle=90,
       colors=plt.cm.Blues([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]), textprops={"fontsize": 10})
ax.set_title("女性消费客户的年龄段分布", loc="left", fontsize=14)
save(fig, "ecommerce_female_age_dist")

# 7-3. 50岁以上女性客户的消费品类分布
old_f = female[female["年龄"] >= 50]
cat = old_f.groupby("品类")["数量"].sum().sort_values(ascending=False)
fig, ax = new_ax(figsize=(10, 5.5))
bars = ax.bar(cat.index, cat.values, color="#3A5FCD", alpha=0.85)
for b, v in zip(bars, cat.values):
    ax.text(b.get_x() + b.get_width()/2, v, int(v), ha="center", va="bottom", fontsize=9)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=9)
beautify(ax, "50岁以上的女性客户的消费品类分布", "品类", "购买数量（件）")
save(fig, "ecommerce_old_female_category")

# 7-4. 50岁以上女性服饰和护肤品消费人群的支付方式分布
sub = old_f[old_f["品类"].isin(["Clothing", "Cosmetics"])]
pay = sub["支付方式"].value_counts()
fig, ax = new_ax(figsize=(8, 5))
bars = ax.bar(pay.index, pay.values, color="#2E8B57", alpha=0.85, width=0.55)
for b, v in zip(bars, pay.values):
    ax.text(b.get_x() + b.get_width()/2, v, int(v), ha="center", va="bottom", fontsize=10)
beautify(ax, "50岁以上女性服饰和护肤品消费人群的支付方式分布", "支付方式", "订单数（单）")
save(fig, "ecommerce_old_female_payment")
