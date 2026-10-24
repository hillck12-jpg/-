# -*- coding: utf-8 -*-
"""复现第2章 PBIX⑧《分省销售分析》（案例1，5 个 csv）。

PBIX 页面包含（Layout 解析结果）：
V1 card 销售额 | V2 card 利润 | V3 card 订单数 | V5 lineChart 销售额按季度
V6 pieChart 品类销售额占比 | V7 clusteredColumn 品类x产品销售额 | V8 treemap 省份销售额

数据真实字段（gbk 编码）：
- 订单表: OrderID, EmployeeID, ShipProvince, OrderDate
- 订单表明细表: 订单ID, 商品ID, 销售额, 销售成本
- 商品表: ProductID, ProductName, CategoryID
- 商品类型表: CategoryID, CategoryName, Description
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 读取数据（编码自动探测：utf-8-sig / gbk）
def read_csv_any(name):
    for enc in ("utf-8-sig", "gbk"):
        try:
            return pd.read_csv(DATA_DIR / name, encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(DATA_DIR / name, encoding="gbk", encoding_errors="replace")

orders = read_csv_any("订单表.csv")
detail = read_csv_any("订单表明细表.csv")
products = read_csv_any("商品表.csv")
category = read_csv_any("商品类型表.csv")

# 5. 表关联：明细.订单ID → 订单表.OrderID；明细.产口ID(笔误列) → 商品表.ProductID → 类型表.CategoryID
prod_link = "商品ID" if "商品ID" in detail.columns else "产口ID"
m = detail.merge(orders, left_on="订单ID", right_on="OrderID", how="left")
m = m.merge(products, left_on=prod_link, right_on="ProductID", how="left")
m = m.merge(category, on="CategoryID", how="left", suffixes=("", "_类型"))
m["销售额"] = pd.to_numeric(m["销售金额"], errors="coerce").fillna(0)
m["利润"] = m["销售额"] - pd.to_numeric(m["销售成本"], errors="coerce").fillna(0)

# 6. KPI 汇总
sales_sum = m["销售额"].sum()
profit_sum = m["利润"].sum()
order_cnt = orders["OrderID"].nunique()

# 7-1. KPI 卡
fig, ax = plt.subplots(figsize=(8, 3))
ax.axis("off")
kpis = [("总销售额", f"{sales_sum:,.0f}"), ("总利润", f"{profit_sum:,.0f}"), ("订单数", f"{order_cnt:,}")]
for i, (t, v) in enumerate(kpis):
    ax.text(0.2 + i * 0.3, 0.6, v, ha="center", fontsize=20, weight="bold", color="#1F3B8C")
    ax.text(0.2 + i * 0.3, 0.25, t, ha="center", fontsize=12, color="#666666")
ax.set_title("销售 KPI 概览", loc="left", fontsize=14)
save(fig, "province_kpi_cards")

# 7-2. 销售额按季度趋势（线图）
m["OrderDate"] = pd.to_datetime(m["OrderDate"], errors="coerce")
m = m.dropna(subset=["OrderDate"])
m["季度"] = m["OrderDate"].dt.to_period("Q").astype(str)
qs = m.groupby("季度")["销售额"].sum()
fig, ax = new_ax(figsize=(10, 5))
ax.plot(qs.index, qs.values, marker="o", color="#3A5FCD")
beautify(ax, "销售额按季度变化趋势", "季度", "销售额（元）")
save(fig, "province_sales_by_quarter")

# 7-3. 品类销售额占比（饼图）
cs = m.groupby("CategoryName")["销售额"].sum().sort_values(ascending=False)
fig, ax = new_ax(figsize=(8, 6))
ax.pie(cs.values, labels=cs.index, autopct="%1.1f%%", startangle=90,
       colors=plt.cm.tab20.colors[:len(cs)], textprops={"fontsize": 9})
ax.set_title("各品类销售额占比", loc="left", fontsize=14)
save(fig, "province_category_pie")

# 7-4. 品类 x 产品销售额（Top 产品柱图）
top_prod = m.groupby(["CategoryName", "ProductName"])["销售额"].sum().reset_index()
top_prod = top_prod.sort_values("销售额", ascending=False).groupby("CategoryName").head(3)
fig, ax = new_ax(figsize=(12, 5.5))
import seaborn as sns
sns.barplot(data=top_prod, x="ProductName", y="销售额", hue="CategoryName", ax=ax,
            palette="Blues_r", dodge=False)
beautify(ax, "各品类Top产品销售额对比", "产品", "销售额（元）")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
ax.legend(frameon=False, fontsize=9)
save(fig, "province_category_product")

# 7-5. 省份销售额（treemap → 水平条形图替代）
ps = m.groupby("ShipProvince")["销售额"].sum().sort_values(ascending=True)
fig, ax = new_ax(figsize=(10, 7))
ax.barh(ps.index.astype(str), ps.values, color="#3A5FCD", alpha=0.85)
beautify(ax, "各省份销售额", "销售额（元）", "省份")
save(fig, "province_sales_treemap")
