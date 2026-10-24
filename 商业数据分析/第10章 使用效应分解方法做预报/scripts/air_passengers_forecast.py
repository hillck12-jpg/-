# -*- coding: utf-8 -*-
"""复现第10章《效应分解法》：AirPassengers 时间序列分解与预测。

PBIX⑪ Layout 解析结果：
PAGE1 V1 lineChart：AIR 按年 + 预测线（forecast.ForecastValue / 高低置信带）
PAGE2 V1 lineChart：ln(AIR) 按年+月份
实现：statsmodels STL/乘法季节分解 + 简单趋势外推预测（95% 置信带）
数据：AirPassengers.csv（DATE/AIR/ln_AIR，1949-1960 月度）
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
df = pd.read_csv(DATA_DIR / "AirPassengers.csv", encoding="gbk")
df["DATE"] = pd.to_datetime(df["DATE"])
df = df.set_index("DATE").asfreq("MS")
ts = df["AIR"]

# 6. 效应分解（乘法模型：趋势 x 季节 x 残差）
decomp = seasonal_decompose(ts, model="multiplicative", period=12)

# 7-1. 分解四联图（原始/趋势/季节/残差）
fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True)
axes[0].plot(ts.index, ts.values, color="#1F3B8C")
axes[0].set_title("原始序列 AIR（1949-1960）", loc="left", fontsize=13)
axes[1].plot(decomp.trend.index, decomp.trend.values, color="#2E8B57")
axes[1].set_title("趋势效应 Trend", loc="left", fontsize=13)
axes[2].plot(decomp.seasonal.index, decomp.seasonal.values, color="#E8A33D")
axes[2].set_title("季节效应 Seasonal", loc="left", fontsize=13)
axes[3].plot(decomp.resid.index, decomp.resid.values, color="#B22222")
axes[3].set_title("残差 Residual", loc="left", fontsize=13)
for ax in axes:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.3)
fig.tight_layout()
FIG = __import__("pathlib").Path(__file__).resolve().parents[1] / "figures"
FIG.mkdir(exist_ok=True)
fig.savefig(FIG / "air_decomposition.png", dpi=150, bbox_inches="tight")
print(f"已保存: {FIG / 'air_decomposition.png'}")
plt.close(fig)

# 7-2. 预测：趋势外推 + 季节因子（对应 PBIX forecast.ForecastValue + 置信带）
seasonal_factor = decomp.seasonal.groupby(decomp.seasonal.index.month).mean()
trend_last = decomp.trend.dropna()
x = np.arange(len(trend_last))
k, b = np.polyfit(x, trend_last.values, 1)
future_idx = pd.date_range(ts.index[-1] + pd.DateOffset(months=1), periods=24, freq="MS")
trend_pred = k * (np.arange(len(ts), len(ts) + 24)) + b
season_pred = [seasonal_factor[m] for m in future_idx.month]
forecast = trend_pred * season_pred
resid_std = decomp.resid.dropna().std()
lower, upper = forecast * np.exp(-1.96 * resid_std), forecast * np.exp(1.96 * resid_std)

fig, ax = new_ax(figsize=(11, 6))
ax.plot(ts.index, ts.values, color="#1F3B8C", label="历史值")
ax.plot(future_idx, forecast, color="#B22222", lw=1.8, ls="--", label="预测值")
ax.fill_between(future_idx, lower, upper, color="#B22222", alpha=0.15,
                label="95% 置信区间")
beautify(ax, "AirPassengers 预测（效应分解 + 趋势外推，95% 置信带）", "日期", "旅客数（千人）")
ax.legend(frameon=False)
save(fig, "air_forecast")

# 7-3. 对数序列按年-月份趋势（PBIX 第2页）
fig, ax = new_ax(figsize=(11, 5.5))
ln_ts = df["ln_AIR"] if "ln_AIR" in df.columns else np.log(ts)
for year, grp in ln_ts.groupby(ln_ts.index.year):
    ax.plot(grp.index.month, grp.values, marker="o", ms=3, label=str(year))
ax.set_xticks(range(1, 13))
ax.set_xticklabels([f"{m}月" for m in range(1, 13)], fontsize=9)
beautify(ax, "ln(AIR) 各年份月份趋势", "月份", "ln(AIR)")
ax.legend(frameon=False, ncol=4, fontsize=8, loc="upper left")
save(fig, "air_ln_by_month")
