# -*- coding: utf-8 -*-
"""复现第2章 PBIX⑤《快速搭建销售看板》。

Layout 解析结果：
V1 card 实际支付总额 | V2 card 数量 | V6 card 最小订单号 | V4 clusteredColumn
商品类别xsku_name 销售额 | V7 map（此处用条形图替代地图）| V8 lineChart 销售额按季度

数据：零售订单表.xlsx（sheet1：订单号/订单时间/商品类别/sku_name/数量/实际支付/省份...）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import matplotlib.pyplot as plt

# 2. 读取数据
df = pd.read_excel(DATA_DIR / "零售订单表.xlsx", sheet_name="sheet1")
print("字段：", list(df.columns))
df.columns = [str(c).strip() for c in df.columns]
amt_col = [c for c in df.columns if "支付" in c or "金额" in c][0]
time_col = [c for c in df.columns if "时间" in c or "日期" in c][0]
df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
df = df.dropna(subset=[time_col])

# 6. KPI
total_amt = df[amt_col].sum()
total_qty = pd.to_numeric(df.get("数量"), errors="coerce").sum() if "数量" in df.columns else 0
min_order = df[[c for c in df.columns if "订单号" in c][0]].min()

# 7-1. KPI 卡
fig, ax = plt.subplots(figsize=(8, 3))
ax.axis("off")
kpis = [("实际支付总额", f"{total_amt:,.0f}"), ("销售数量", f"{total_qty:,.0f}"),
        ("最小订单号", str(min_order))]
for i, (t, v) in enumerate(kpis):
    ax.text(0.2 + i * 0.3, 0.6, v, ha="center", fontsize=18, weight="bold", color="#1F3B8C")
    ax.text(0.2 + i * 0.3, 0.22, t, ha="center", fontsize=12, color="#666666")
ax.set_title("零售订单 KPI 概览", loc="left", fontsize=14)
save(fig, "dashboard_kpi_cards")

# 7-2. 商品类别 x sku_name 销售额簇状柱图
cat_col = [c for c in df.columns if "类别" in c or "类目" in c]
sku_col = [c for c in df.columns if "sku" in c.lower() or "商品" in c]
if cat_col and sku_col:
    top = df.groupby([cat_col[0], sku_col[0]])[amt_col].sum().reset_index()
    top = top.sort_values(amt_col, ascending=False).groupby(cat_col[0]).head(3)
    fig, ax = new_ax(figsize=(12, 5.5))
    import seaborn as sns
    sns.barplot(data=top, x=sku_col[0], y=amt_col, hue=cat_col[0], ax=ax,
                palette="Blues_r", dodge=False)
    beautify(ax, "各商品类别Top单品销售额", "SKU", "实际支付（元）")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
    ax.legend(frameon=False, fontsize=9)
    save(fig, "dashboard_category_sku")

# 7-3. 销售额按季度趋势
df["季度"] = df[time_col].dt.to_period("Q").astype(str)
qs = df.groupby("季度")[amt_col].sum()
fig, ax = new_ax(figsize=(10, 5))
ax.plot(qs.index, qs.values, marker="o", color="#3A5FCD")
beautify(ax, "销售额按季度变化趋势", "季度", "实际支付（元）")
save(fig, "dashboard_sales_by_quarter")

# 7-4. 地域销售额分布（地图替代为条形图）
prov_col = [c for c in df.columns if "省" in c or "城市" in c or "地区" in c]
if prov_col:
    ps = df.groupby(prov_col[0])[amt_col].sum().sort_values(ascending=True)
    fig, ax = new_ax(figsize=(9, 7))
    ax.barh(ps.index.astype(str), ps.values, color="#3A5FCD", alpha=0.85)
    beautify(ax, f"各地区{amt_col}分布", amt_col, prov_col[0])
    save(fig, "dashboard_by_region")
