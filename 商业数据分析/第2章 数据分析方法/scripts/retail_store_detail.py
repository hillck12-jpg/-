# -*- coding: utf-8 -*-
"""复现第2章 PBIX⑨《服装零售分析》第2页：店铺详情。

对照截图 figures/_reference/2.店铺详情.png（筛选 CRYSTAL百联，2020-12-14 ~ 2020-12-20）：
- 坪效变化趋势（lineChart）
- 成交金额按销售姓名（barChart，Top XM0199 8849 / XM0507 3549 / XM0198 1161）
- 成交金额按大类（毛衣 8551 / 牛仔 2104 / 衬衫 1659 / 羽绒 1245）
- 订单数按联单类型（1单1件 80% / 2联单 10% / 3联单 10%）
- 订单明细表（MASTERID/SKUID/大类/EMPNAME/件数/成交金额/折扣率）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 读取数据
XL = DATA_DIR / "服装零售-原始数据.xlsx"
retail = pd.read_excel(XL, sheet_name="零售单")
detail = pd.read_excel(XL, sheet_name="零售单明细")
stores = pd.read_excel(XL, sheet_name="店铺表")
skus = pd.read_excel(XL, sheet_name="SKU表")
styles = pd.read_excel(XL, sheet_name="款号表")
for d in (retail, detail):
    d.columns = [str(c).strip() for c in d.columns]

date_col = "订单日期"
retail[date_col] = pd.to_datetime(retail[date_col], errors="coerce")
retail = retail.dropna(subset=[date_col])
retail_id, detail_id = "订单id", "订单id"

store_col = "店铺id"
emp_col = "员工id"
STORE, D1, D2 = "CRYSTAL百联", "2020-12-14", "2020-12-20"
store_id = int(stores.loc[stores["店铺名称"] == STORE, "店铺id"].iloc[0])

# 5. 筛选：店铺 + 日期区间
mask = (retail[store_col] == store_id) & \
       (retail[date_col] >= pd.Timestamp(D1)) & (retail[date_col] <= pd.Timestamp(D2) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
sub_retail = retail[mask]
m = detail.merge(sub_retail, on="订单id", how="inner", suffixes=("", "_单"))

amt_col = "成交金额"
qty_col = "数量"
m[amt_col] = pd.to_numeric(m[amt_col], errors="coerce").fillna(0)
m[qty_col] = pd.to_numeric(m[qty_col], errors="coerce").fillna(0)

# 关联大类：明细.商品id(SKUid) → SKU表.SKUid → 款号表.款号id(大类id 是编码，改为关联款号id)
sku_key = "商品id"
sku_id_col, style_key = "SKUid", "款号id"
style_id_col = "款号id"
# 款号表无大类名称，构造大类=款号id 映射说明；此处直接用款号id 作为大类维度
cat_col = None
m = m.merge(skus[[sku_id_col, style_key]], left_on=sku_key, right_on=sku_id_col, how="left")

# 7-1. 坪效变化趋势（店铺面积来自店铺表）
area = float(stores.loc[stores["店铺名称"] == STORE, "店铺面积"].iloc[0])
daily_amt = m.groupby(m[date_col].dt.date)[amt_col].sum()
daily_eff = daily_amt / area
fig, ax = new_ax(figsize=(10, 5))
ax.plot([str(d) for d in daily_eff.index], daily_eff.values, marker="o", color="#1F3B8C")
for x, v in zip([str(d) for d in daily_eff.index], daily_eff.values):
    ax.annotate(f"{v:.0f}", (x, v), textcoords="offset points", xytext=(0, 8),
                ha="center", fontsize=9)
beautify(ax, f"{STORE} 坪效变化趋势", "日期", "坪效（元/㎡）")
save(fig, "retail_store_efficiency")

# 7-2. 成交金额按销售员工（员工id，可关联员工表获取姓名）
by_emp = m.groupby(m[emp_col])[amt_col].sum().sort_values(ascending=False).head(10)
fig, ax = new_ax(figsize=(9, 5.5))
bars = ax.barh(by_emp.index.astype(str)[::-1], by_emp.values[::-1], color="#1F3B8C")
for b, v in zip(bars, by_emp.values[::-1]):
    ax.text(v, b.get_y() + b.get_height()/2, f"{v:,.0f}", va="center", fontsize=9)
beautify(ax, "成交金额按销售员工Top10", "成交金额（元）", "员工id")
save(fig, "retail_amount_by_emp")

# 7-3. 成交金额按款号（款号表无大类名称，用款号id 作为商品维度近似）
by_cat = m.groupby(style_key)[amt_col].sum().sort_values(ascending=False).head(6)
fig, ax = new_ax(figsize=(9, 5.5))
bars = ax.barh(by_cat.index.astype(str)[::-1], by_cat.values[::-1], color="#1F3B8C")
for b, v in zip(bars, by_cat.values[::-1]):
    ax.text(v, b.get_y() + b.get_height()/2, f"{v:,.0f}", va="center", fontsize=9)
beautify(ax, "成交金额按款号Top6", "成交金额（元）", "款号id")
save(fig, "retail_amount_by_category")

# 7-4. 订单数按联单类型（饼图：1单1件/2联单/3联单+）
ord_qty = m.groupby(detail_id)[qty_col].sum()
def bucket(q):
    if q <= 1:
        return "1单1件"
    if q == 2:
        return "2联单"
    return "3联单+"
buckets = ord_qty.apply(bucket).value_counts()
fig, ax = new_ax(figsize=(7.5, 6))
wedges, texts, autotexts = ax.pie(
    buckets.values, labels=buckets.index, autopct="%1.0f%%", startangle=90,
    colors=["#1F3B8C", "#3A5FCD", "#6C8EBF", "#9DC3E6"][:len(buckets)],
    textprops={"fontsize": 11})
ax.set_title(f"订单数按联单类型（{STORE}）", loc="left", fontsize=14)
save(fig, "retail_order_type_pie")

# 7-5. 订单明细表（Top10 表格图）
cols_show = [detail_id, sku_key, emp_col, qty_col, amt_col]
cols_show = [c for c in cols_show if c]
tbl = m[cols_show].head(10).copy()
tbl[amt_col] = tbl[amt_col].round(0)
if len(tbl) == 0:
    tbl = m[cols_show].head(10).copy()
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.axis("off")
tbl_disp = tbl.rename(columns=lambda c: str(c))
if len(tbl_disp) > 0:
    table = ax.table(cellText=tbl_disp.astype(str).values, colLabels=tbl_disp.columns,
                     cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)
    for j in range(len(tbl_disp.columns)):
        table[0, j].set_facecolor("#1F3B8C")
        table[0, j].set_text_props(color="white", weight="bold")
else:
    ax.text(0.5, 0.5, "筛选条件下无订单明细数据", ha="center", fontsize=12, color="#666666")
ax.set_title(f"订单明细（{STORE}，{D1}~{D2}，Top10）", loc="left", fontsize=14)
save(fig, "retail_order_detail_table")
