# -*- coding: utf-8 -*-
"""复现第10章：信用卡消费额时间序列分解（含节日 vs 去除节日对比）。

数据：
- 信用卡消费额_含节日.xlsx（pos：date/amount，原始日度，单位元）
- 信用卡消费额_去除节日.xlsx（日期/信用卡消费额，已去除节日效应，单位万元）
产出：
- 含节日原始序列趋势
- 去节日序列分解（趋势/季节/残差）
- 两个序列对比图
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_style import DATA_DIR, new_ax, beautify, save
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# 2. 读取数据
raw = pd.read_excel(DATA_DIR / "信用卡消费额_含节日.xlsx", sheet_name="pos")
raw["date"] = pd.to_datetime(raw["date"])
raw = raw.set_index("date").sort_index()
ts_raw = raw["amount"]

clean = pd.read_excel(DATA_DIR / "信用卡消费额_去除节日.xlsx", sheet_name="Sheet1")
clean.columns = [str(c).strip() for c in clean.columns]
date_c = [c for c in clean.columns if "日期" in c][0]
amt_c = [c for c in clean.columns if "消费额" in c][0]
clean[date_c] = pd.to_datetime(clean[date_c])
clean = clean.set_index(date_c).sort_index()
ts_clean = pd.to_numeric(clean[amt_c], errors="coerce").dropna()

# 6. 分解（月度聚合后季节分解；去节日序列约 30 天不足以做月度分解，改用周频分解或降级为移动平均趋势）
m_raw = ts_raw.resample("MS").sum()
m_clean = ts_clean.resample("MS").sum()
if len(m_clean) >= 24:
    dec = seasonal_decompose(m_clean, model="additive", period=12)
    trend, seasonal, resid = dec.trend, dec.seasonal, dec.resid
else:
    # 数据不足两个完整年度循环：以 7 日移动平均为趋势，余项 = 原序列 - 趋势
    trend = ts_clean.rolling(7, center=True).mean()
    seasonal = pd.Series(0.0, index=ts_clean.index)
    resid = ts_clean - trend
    m_clean = ts_clean

# 7-1. 含节日日度序列
fig, ax = new_ax(figsize=(11, 5))
ax.plot(ts_raw.index, ts_raw.values / 1e4, color="#1F3B8C", lw=0.8)
beautify(ax, "信用卡日消费额（含节日，原始序列）", "日期", "消费额（万元）")
save(fig, "credit_card_daily_raw")

# 7-2. 去节日序列分解四联图
fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True)
axes[0].plot(m_clean.index, m_clean.values, color="#1F3B8C")
axes[0].set_title("去节日信用卡消费额（原始序列）", loc="left", fontsize=13)
axes[1].plot(trend.index, trend.values, color="#2E8B57")
axes[1].set_title("趋势效应 Trend", loc="left", fontsize=13)
axes[2].plot(seasonal.index, seasonal.values, color="#E8A33D")
axes[2].set_title("季节/周期效应 Seasonal", loc="left", fontsize=13)
axes[3].plot(resid.index, resid.values, color="#B22222")
axes[3].set_title("残差 Residual", loc="left", fontsize=13)
for ax in axes:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.3)
fig.tight_layout()
FIG = Path(__file__).resolve().parents[1] / "figures"
FIG.mkdir(exist_ok=True)
fig.savefig(FIG / "credit_card_decomposition.png", dpi=150, bbox_inches="tight")
print(f"已保存: {FIG / 'credit_card_decomposition.png'}")
plt.close(fig)

# 7-3. 含节日 vs 去节日月度对比
fig, ax = new_ax(figsize=(11, 5.5))
ax.plot(m_raw.index, m_raw.values / 1e4, color="#B22222", label="含节日", alpha=0.8)
ax.plot(m_clean.index, m_clean.values, color="#1F3B8C", label="去除节日")
beautify(ax, "信用卡月度消费额：含节日 vs 去除节日", "日期", "消费额（万元）")
ax.legend(frameon=False)
save(fig, "credit_card_compare")
