# -*- coding: utf-8 -*-
"""复现第2章 PBIX⑨《服装零售分析》第1页：指标分析（KPI 卡 + 环比）。

对照截图 figures/_reference/1.指标分析.png：
- 日期 2020-12-20 时点：零售金额 207220（环比 88.21%）、成交金额 164530（环比 101.45%）、
  折扣率 79.40%（环比 5.22%）、会员人数 127（环比 79）、会员人均消费 1227（环比 -26.59%）、
  订单数 146（环比 93）、客单价 1127（环比 -26.87%）、件数 184（环比 116）、
  件单价 894（环比 -25.55%）、连带率 1.3（环比 0.0）
- 环比规则：金额类 =(当日-上周同期)/上周同期；数量类 = 当日-上周同期
产出：复刻 KPI 卡矩阵图（当日值 + 环比值，下降红色强调）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 读取数据（12 张表）
XL = DATA_DIR / "服装零售-原始数据.xlsx"
retail = pd.read_excel(XL, sheet_name="零售单")          # 单据头
detail = pd.read_excel(XL, sheet_name="零售单明细")       # 明细行
stores = pd.read_excel(XL, sheet_name="店铺表")
vips = pd.read_excel(XL, sheet_name="vip表")
skus = pd.read_excel(XL, sheet_name="SKU表")
styles = pd.read_excel(XL, sheet_name="款号表")
print("零售单字段：", list(retail.columns))
print("明细字段：", list(detail.columns))

# 统一字段（真实列名：零售单[订单id/订单编号/订单日期id/订单日期/店铺id/会员id/数量/零售金额/成交金额]
#                     零售单明细[订单明细id/订单id/商品id/数量/折扣率/标准价/零售金额/成交金额]）
retail.columns = [str(c).strip() for c in retail.columns]
detail.columns = [str(c).strip() for c in detail.columns]
date_col = "订单日期"
retail[date_col] = pd.to_datetime(retail[date_col], errors="coerce")
retail = retail.dropna(subset=[date_col])
vip_col = "会员id"

# 关联明细
retail_id, detail_id = "订单id", "订单id"
m = detail.merge(retail, on="订单id", how="inner", suffixes=("", "_单"))

# 金额字段（明细级）
amt_col = "成交金额"
retail_amt_col = "零售金额"
qty_col = "数量"

# 4. 指标计算函数：指定日期 → 当日 vs 上周同日
def kpi_at(day):
    day = pd.Timestamp(day)
    prev = day - pd.Timedelta(days=7)
    cur = m[m[date_col].dt.date == day.date()]
    pre = m[m[date_col].dt.date == prev.date()]
    cur_retail = retail[retail[date_col].dt.date == day.date()]
    pre_retail = retail[retail[date_col].dt.date == prev.date()]

    def s(d, col, default=0):
        return float(pd.to_numeric(d[col], errors="coerce").sum()) if col and col in d.columns else default

    res = {}
    res["零售金额"] = s(cur_retail, retail_amt_col) or s(cur, amt_col)
    res["成交金额"] = s(cur, amt_col)
    n_cur, n_pre = len(cur), len(pre)
    res["订单数"] = cur_retail[retail_id].nunique()
    res["件数"] = s(cur, qty_col)
    mem_cur = cur_retail[cur_retail[vip_col].notna()] if vip_col else cur_retail.iloc[:0]
    mem_pre = pre_retail[pre_retail[vip_col].notna()] if vip_col else pre_retail.iloc[:0]
    res["会员人数"] = mem_cur[vip_col].nunique() if vip_col else 0
    mem_amt = s(mem_cur, amt_col)
    res["会员人均消费"] = mem_amt / max(res["会员人数"], 1)
    res["客单价"] = res["成交金额"] / max(res["订单数"], 1)
    res["件单价"] = res["成交金额"] / max(res["件数"], 1)
    res["连带率"] = res["件数"] / max(res["订单数"], 1)
    discount = 1 - res["成交金额"] / res["零售金额"] if res["零售金额"] else np.nan
    res["折扣率"] = discount * 100 if pd.notna(discount) else 0

    pre_retail_amt = s(pre_retail, retail_amt_col) or s(pre, amt_col)
    pre_deal = s(pre, amt_col)
    pre_orders = pre_retail[retail_id].nunique()
    pre_qty = s(pre, qty_col)
    pre_mem_n = mem_pre[vip_col].nunique() if vip_col else 0
    pre_mem_amt = s(mem_pre, amt_col)
    res["零售金额环比"] = (res["零售金额"] - pre_retail_amt) / pre_retail_amt * 100 if pre_retail_amt else np.nan
    res["成交金额环比"] = (res["成交金额"] - pre_deal) / pre_deal * 100 if pre_deal else np.nan
    res["订单数环比"] = res["订单数"] - pre_orders
    res["件数环比"] = res["件数"] - pre_qty
    res["会员人数环比"] = res["会员人数"] - pre_mem_n
    pre_mem_avg = pre_mem_amt / max(pre_mem_n, 1)
    res["会员人均消费环比"] = (res["会员人均消费"] - pre_mem_avg) / pre_mem_avg * 100 if pre_mem_avg else np.nan
    pre_aov = pre_deal / max(pre_orders, 1)
    res["客单价环比"] = (res["客单价"] - pre_aov) / pre_aov * 100 if pre_aov else np.nan
    pre_asp = pre_deal / max(pre_qty, 1)
    res["件单价环比"] = (res["件单价"] - pre_asp) / pre_asp * 100 if pre_asp else np.nan
    pre_ipt = pre_qty / max(pre_orders, 1)
    res["连带率环比"] = res["连带率"] - pre_ipt
    pre_retail_v = pre_retail_amt
    res["折扣率环比"] = res["折扣率"] - (1 - pre_deal / pre_retail_v) * 100 if pre_retail_v else np.nan
    return res

DAY = "2020-12-20"
r = kpi_at(DAY)

# 7. KPI 卡矩阵（对照截图排布）
CARDS = [
    ("零售金额", "零售金额环比", "{:,.0f}"),
    ("折扣率", "折扣率环比", "{:.2f}%"),
    ("成交金额", "成交金额环比", "{:,.0f}"),
    ("会员人数", "会员人数环比", "{:,.0f}"),
    ("会员人均消费", "会员人均消费环比", "{:,.0f}"),
    ("订单数", "订单数环比", "{:,.0f}"),
    ("客单价", "客单价环比", "{:,.0f}"),
    ("连带率", "连带率环比", "{:.1f}"),
    ("件数", "件数环比", "{:,.0f}"),
    ("件单价", "件单价环比", "{:,.0f}"),
]
fig, axes = plt.subplots(2, 5, figsize=(16, 6))
for ax, (name, mom, fmt) in zip(axes.flat, CARDS):
    val = r.get(name, 0)
    mom_v = r.get(mom, np.nan)
    is_down = pd.notna(mom_v) and mom_v < 0
    ax.barh([0], [1], color="#F5F5F5", edgecolor="#B22222" if is_down else "#999999", lw=2 if is_down else 1)
    ax.set_xlim(0, 1); ax.set_ylim(-0.5, 0.5); ax.axis("off")
    ax.text(0.5, 0.25, fmt.format(val), ha="center", fontsize=17, weight="bold",
            color="#1F3B8C")
    mom_str = f"{mom_v:+.2f}%" if "率" not in name or "环比" in mom and "率" in name else f"{mom_v:+.0f}"
    if name == "折扣率":
        mom_str = f"{mom_v:+.2f}%"
    elif name == "连带率":
        mom_str = f"{mom_v:+.1f}"
    ax.text(0.5, -0.1, mom_str, ha="center", fontsize=11,
            color="#B22222" if is_down else "#2E8B57")
    ax.text(0.5, -0.38, name, ha="center", fontsize=10, color="#666666")
fig.suptitle(f"指标分析（{DAY}）· 左对齐标题：各 KPI 及环比", x=0.01, ha="left", fontsize=14)
save(fig, "retail_kpi_cards")
