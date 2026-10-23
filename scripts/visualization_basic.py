# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.patches as patches
import matplotlib.ticker as ticker

# ================= 全局配置 =================
plt.rcParams['font.sans-serif'] = ['SimHei'] # Mac用户改为 'Arial Unicode MS'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font='SimHei')

file1 = '../data/第二章 图表(前15).xlsx'
file2 = '../data/第二章 图表(后15).xlsx'
fig_dir = '../figures/'
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# 辅助函数：自动寻找表头
def get_df(file, sheet_name, search_kw):
    raw = pd.read_excel(file, sheet_name=sheet_name, header=None)
    row = next((i for i in range(10) if search_kw in str(raw.iloc[i].values)), 0)
    return pd.read_excel(file, sheet_name=sheet_name, header=row)

print("🚀 开始生成 30 张高清图表...")

# ==========================================
# 1. 渐变柱形图
# ==========================================
df = get_df(file1, '1 渐变柱形图', '区域').dropna(subset=['区域'])[['区域', '销售量']].dropna()
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x='区域', y='销售量', data=df, palette='Blues_d', ax=ax)
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')
ax.set_title('1. 渐变柱形图')
plt.savefig(fig_dir + '01_渐变柱形图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 2. 带均值柱形图
# ==========================================
df = get_df(file1, '2 带均值柱形图', '区域').dropna(subset=['区域'])[['区域', '销售量']].dropna()
df['均值'] = df['销售量'].mean()
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x='区域', y='销售量', data=df, color='#4C72B0', ax=ax)
ax.axhline(df['均值'].iloc[0], color='red', linestyle='--', label=f'均值: {df["均值"].iloc[0]:.1f}')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')
ax.set_title('2. 带均值柱形图')
ax.legend()
plt.savefig(fig_dir + '02_带均值柱形图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 3. 渐变圆角柱形图
# ==========================================
df = get_df(file1, '3 渐变圆角柱形图', '商品').dropna(subset=['商品'])[['商品', '销量']].dropna()
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x='商品', y='销量', data=df, palette='viridis', ax=ax)
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')
ax.set_title('3. 渐变圆角柱形图')
plt.savefig(fig_dir + '03_渐变圆角柱形图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 4. 标注柱形图
# ==========================================
df = get_df(file1, '4 标注柱形图', '月份').dropna(subset=['月份'])[['月份', '销量']].dropna()
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='月份', y='销量', data=df, color='#55A868', ax=ax)
max_idx = df['销量'].idxmax()
for i, v in enumerate(df['销量']):
    ax.text(i, v + 50, str(v), ha='center', va='bottom')
ax.text(max_idx, df['销量'][max_idx] + 400, '最高销量', ha='center', color='red', fontweight='bold')
ax.set_title('4. 标注柱形图')
plt.savefig(fig_dir + '04_标注柱形图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 5. 层叠柱形图
# ==========================================
df = get_df(file1, '5 层叠柱形图', '季度').dropna(subset=['季度'])[['季度', '销售额', '利润额']].dropna()
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(df['季度'], df['销售额'], label='销售额', color='#4C72B0')
ax.bar(df['季度'], df['利润额'], bottom=df['销售额'], label='利润额', color='#C44E52')
for i, row in df.iterrows():
    ax.text(i, row['销售额']/2, str(row['销售额']), ha='center', va='center', color='white')
    ax.text(i, row['销售额'] + row['利润额']/2, str(row['利润额']), ha='center', va='center', color='white')
ax.set_title('5. 层叠柱形图')
ax.legend()
plt.savefig(fig_dir + '05_层叠柱形图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 6. 蝴蝶图
# ==========================================
df = get_df(file1, '6 蝴蝶图', '区域').dropna(subset=['区域'])[['区域', '2022年销量', '2021年销量']].dropna()
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(df['区域'], df['2022年销量'], color='#1f77b4', label='2022年')
ax.barh(df['区域'], df['2021年销量'] * -1, color='#ff7f0e', label='2021年') 
ax.axvline(0, color='black', linewidth=1)
for i, v in enumerate(df['2022年销量']): ax.text(v + 50, i, str(v), va='center')
for i, v in enumerate(df['2021年销量']): ax.text(-v - 50, i, str(v), va='center', ha='right')
ax.set_title('6. 蝴蝶图')
ax.legend()
plt.savefig(fig_dir + '06_蝴蝶图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 7. 蝴蝶图2
# ==========================================
df = get_df(file1, '7 蝴蝶图', '区域').dropna(subset=['区域'])[['区域', '2022年', '2021年']].dropna()
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(df['区域'], df['2022年'], color='#1f77b4', label='2022年')
ax.barh(df['区域'], df['2021年'] * -1, color='#ff7f0e', label='2021年')
ax.axvline(0, color='black', linewidth=1)
ax.set_title('7. 蝴蝶图 (比例)')
ax.legend()
plt.savefig(fig_dir + '07_蝴蝶图2.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 8. 数值百分比 (横向条形图 + 同比说明)
# ==========================================
df = get_df(file1, '8 数值百分比', '区域').dropna(subset=['区域'])[['区域', '销量', '同比去年']].dropna()
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y='区域', x='销量', data=df, color='#4C72B0', ax=ax)
for i, row in df.iterrows():
    ax.text(row['销量'] + 50, i, str(int(row['销量'])), va='center')
    ax.text(row['销量'] + 800, i, f"同比: {row['同比去年']*100:.1f}%", va='center', color='red' if row['同比去年']<0 else 'green')
ax.set_title('8. 各区域销量及同比下降率')
plt.savefig(fig_dir + '08_数值百分比.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 9. 对比柱形图
# ==========================================
df = get_df(file1, '9 对比柱形图', '商品').dropna(subset=['商品'])[['商品', '2021销量', '2022销量']].dropna()
df_melt = df.melt(id_vars='商品', value_vars=['2021销量', '2022销量'], var_name='年份', value_name='销量')
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='商品', y='销量', hue='年份', data=df_melt, ax=ax)
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom', fontsize=9)
ax.set_title('9. 对比柱形图')
plt.savefig(fig_dir + '09_对比柱形图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 10. 甘特图
# ==========================================
df = get_df(file1, '10 甘特图', '项目名称').dropna(subset=['项目名称'])[['项目名称', '开始日期', '项目天数']].dropna()
df['开始日期'] = pd.to_datetime(df['开始日期'])
fig, ax = plt.subplots(figsize=(10, 5))
for i, row in df.iterrows():
    ax.barh(row['项目名称'], row['项目天数'], left=row['开始日期'], color='#4C72B0')
    ax.text(row['开始日期'] + pd.Timedelta(days=row['项目天数']/2), i, f"{int(row['项目天数'])}天", ha='center', va='center', color='white')
ax.set_title('10. 甘特图')
plt.savefig(fig_dir + '10_甘特图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 11. 平滑折线图 (标峰值)
# ==========================================
df = get_df(file1, '11 平滑折线图', '年份').dropna(subset=['年份'])[['年份', '月份', '销量']].dropna()
df['时间'] = df['年份'].astype(str) + '-' + df['月份']
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x='时间', y='销量', data=df, marker='o', color='#C44E52', ax=ax)
max_idx = df['销量'].idxmax()
ax.annotate(f"峰值: {df['销量'][max_idx]}", xy=(max_idx, df['销量'][max_idx]), xytext=(max_idx-1, df['销量'][max_idx]+200), arrowprops=dict(facecolor='black', shrink=0.05))
plt.xticks(rotation=45)
ax.set_title('11. 平滑折线图 (标出峰值)')
plt.savefig(fig_dir + '11_平滑折线图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 12. 菱形走势图 (垂线与百分比)
# ==========================================
df = get_df(file1, '12 菱形走势图', '月份').dropna(subset=['月份'])[['月份', '完成率']].dropna()
df['完成率'] = df['完成率'] * 100
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df['月份'], df['完成率'], marker='D', markersize=8, color='#8172B3', linestyle='-')
for i, row in df.iterrows():
    ax.plot([i, i], [0, row['完成率']], color='#8172B3', linestyle='--', alpha=0.5)
    ax.text(i, row['完成率']+1, f"{row['完成率']:.1f}%", ha='center', va='bottom')
ax.set_ylim(0, max(df['完成率'])*1.2)
ax.set_title('12. 菱形走势图 (带垂线)')
plt.savefig(fig_dir + '12_菱形走势图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 13. 对比折线图
# ==========================================
df = get_df(file1, '13 对比折线图', '月份').dropna(subset=['月份'])[['月份', '2021年', '2022年']].dropna()
df_melt = df.melt(id_vars='月份', value_vars=['2021年', '2022年'], var_name='年份', value_name='销量')
fig, ax = plt.subplots(figsize=(8, 5))
sns.lineplot(x='月份', y='销量', hue='年份', data=df_melt, marker='o', ax=ax)
ax.set_title('13. 对比折线图')
plt.savefig(fig_dir + '13_对比折线图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 14. 单值圆环图
# ==========================================
df = get_df(file1, '14 单值圆环图', '完成率').dropna(subset=['完成率'])
val = df['完成率'].iloc[0]
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie([val, 1-val], colors=['#4C72B0', '#e0e0e0'], startangle=90, counterclock=False)
centre_circle = plt.Circle((0,0), 0.70, fc='white')
fig.gca().add_artist(centre_circle)
ax.text(0, 0, f"{val*100:.0f}%", ha='center', va='center', fontsize=24)
ax.set_title('14. 单值圆环图')
plt.savefig(fig_dir + '14_单值圆环图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 15. 水球图 (高度逼真填充)
# ==========================================
df = get_df(file1, '15 水球图', '完成率').dropna(subset=['完成率'])
val = df['完成率'].iloc[0]
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2); ax.set_aspect('equal'); ax.axis('off')
outer = plt.Circle((0, 0), 1, color='#4C72B0', fill=False, linewidth=4)
ax.add_patch(outer)
water = plt.Circle((0, -1 + val*2), 1.05, color='#4C72B0', alpha=0.5, clip_on=True)
ax.add_patch(water)
clip = plt.Circle((0, 0), 1, transform=ax.transData)
water.set_clip_path(clip)
ax.text(0, 0, f"{val*100:.0f}%", ha='center', va='center', fontsize=40, fontweight='bold', color='white')
ax.set_title('15. 水球图')
plt.savefig(fig_dir + '15_水球图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 16. 波浪水球图 (同上)
# ==========================================
df = get_df(file2, '16 波浪水球图 ', '完成率').dropna(subset=['完成率'])
val = df['完成率'].iloc[0]
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2); ax.set_aspect('equal'); ax.axis('off')
outer = plt.Circle((0, 0), 1, color='#C44E52', fill=False, linewidth=4)
ax.add_patch(outer)
water = plt.Circle((0, -1 + val*2), 1.05, color='#C44E52', alpha=0.5, clip_on=True)
ax.add_patch(water)
clip = plt.Circle((0, 0), 1, transform=ax.transData)
water.set_clip_path(clip)
ax.text(0, 0, f"{val*100:.0f}%", ha='center', va='center', fontsize=40, fontweight='bold', color='white')
ax.set_title('16. 波浪水球图')
plt.savefig(fig_dir + '16_波浪水球图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 17. 玉玦图 (同心圆环)
# ==========================================
df = get_df(file2, '17 玉玦图', '年龄').dropna(subset=['年龄'])[['年龄', '占比']].dropna()
df = df.sort_values('占比', ascending=True)
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect('equal'); ax.axis('off')
colors = sns.color_palette("husl", len(df))
for i, (idx, row) in enumerate(df.iterrows()):
    radius = 1.0 - i*0.2
    bg_circle = plt.Circle((0, 0), radius, color='#f0f0f0')
    ax.add_patch(bg_circle)
    theta = row['占比'] * 2 * np.pi
    wedge = patches.Wedge((0, 0), radius, 90, 90 + np.degrees(theta), width=0.15, facecolor=colors[i], label=row['年龄'])
    ax.add_patch(wedge)
ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2)
ax.set_title('17. 玉玦图 (同心圆环)')
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
plt.savefig(fig_dir + '17_玉玦图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 18. 跑道图 (横向进度)
# ==========================================
df = get_df(file2, '18 跑道图', '部门').dropna(subset=['部门'])[['部门', '人数']].dropna()
df['占位'] = df['人数'].max() - df['人数']
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='占位', y='部门', data=df, color='#e0e0e0', ax=ax)
sns.barplot(x='人数', y='部门', data=df, color='#4C72B0', ax=ax)
for i, row in df.iterrows():
    ax.text(row['人数'] + 10, i, str(row['人数']), va='center')
ax.set_title('18. 跑道图')
plt.savefig(fig_dir + '18_跑道图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 19. 南丁格尔圆饼图
# ==========================================
df = get_df(file2, '19 南丁格尔圆饼图', '部门').dropna(subset=['部门'])[['部门', '人数占比']].dropna()
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(df['人数占比'], labels=df['部门'], autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
ax.set_title('19. 南丁格尔圆饼图')
plt.savefig(fig_dir + '19_南丁格尔圆饼图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 20. 南丁格尔圆环图
# ==========================================
df = get_df(file2, '20 南丁格尔圆环图', '年龄').dropna(subset=['年龄'])[['年龄', '人数占比']].dropna()
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(df['人数占比'], labels=df['年龄'], autopct='%1.1f%%', startangle=90, pctdistance=0.85, colors=sns.color_palette("Set3"))
centre_circle = plt.Circle((0,0), 0.70, fc='white')
fig.gca().add_artist(centre_circle)
ax.set_title('20. 南丁格尔圆环图')
plt.savefig(fig_dir + '20_南丁格尔圆环图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 21. 南丁格尔（PPT）
# ==========================================
df = get_df(file2, '20 南丁格尔（PPT）', '部门').dropna(subset=['部门'])[['部门', '人数占比']].dropna()
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(df['人数占比'], labels=df['部门'], autopct='%1.1f%%', startangle=90, colors=sns.color_palette("tab10"))
ax.set_title('21. 南丁格尔 (PPT版)')
plt.savefig(fig_dir + '21_南丁格尔PPT.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 22. 仪表盘图 (带刻度和指针)
# ==========================================
raw = pd.read_excel(file2, sheet_name='22 仪表盘图', header=None)
val = float(raw.iloc[2, 7])
fig, ax = plt.subplots(figsize=(8, 5), subplot_kw={'projection': 'polar'})
ax.bar(0, 100, width=np.pi, bottom=0, color='#e0e0e0', align='edge', alpha=0.5)
for tick in range(50, 151, 10):
    theta = np.pi - (tick - 50) / 100 * np.pi
    ax.text(theta, 105, str(tick), ha='center', va='center', fontsize=10)
    ax.plot([theta, theta], [95, 100], color='black', linewidth=1)
theta_val = np.pi - (val - 50) / 100 * np.pi
ax.annotate('', xy=(theta_val, 80), xytext=(theta_val, 0), arrowprops=dict(facecolor='red', width=2, headwidth=8))
ax.scatter(0, 0, color='red', s=100, zorder=10)
ax.set_axis_off()
ax.set_title('22. 仪表盘图 (带刻度及指针)', pad=20)
plt.savefig(fig_dir + '22_仪表盘图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 23. 柱形折线图 (修正增长率)
# ==========================================
df = get_df(file2, '23 柱形折线图', '年份').dropna(subset=['年份'])[['年份', '销售量']].dropna()
df['同比'] = df['销售量'].pct_change() * 100 
fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()
sns.barplot(x='年份', y='销售量', data=df, color='#4C72B0', ax=ax1)
for p in ax1.patches:
    ax1.annotate(f'{int(p.get_height())}', (p.get_x()+p.get_width()/2., p.get_height()), ha='center', va='bottom')
ax2.plot(df['年份'].astype(str), df['同比'], color='#C44E52', marker='o')
for i, v in enumerate(df['同比']):
    if not np.isnan(v): ax2.text(i, v + 2, f"{v:.1f}%", color='#C44E52', ha='center', va='bottom', fontsize=10)
ax1.set_title('23. 柱形折线图')
fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.9))
plt.savefig(fig_dir + '23_柱形折线图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 24. 目标柱形图
# ==========================================
df = get_df(file2, '24 目标柱形图', '商品').dropna(subset=['商品'])[['商品', '实际销量', '目标销量']].dropna()
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='商品', y='实际销量', data=df, color='#4C72B0', label='实际销量', ax=ax)
for i, row in df.iterrows():
    ax.plot([i-0.4, i+0.4], [row['目标销量'], row['目标销量']], color='red', linewidth=3, label='目标销量' if i==0 else "")
    ax.text(i, row['实际销量'] + 20, f"{int(row['实际销量'])}", ha='center', va='bottom')
    ax.text(i, 10, f"达成率\n{(row['实际销量']/row['目标销量']*100):.1f}%", ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')
ax.set_title('24. 目标柱形图')
ax.legend()
plt.savefig(fig_dir + '24_目标柱形图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 25. 子弹图
# ==========================================
df = get_df(file2, '25 子弹图', '商品').dropna(subset=['商品'])[['商品', '实际', '目标', '及格', '良好', '优秀']].dropna()
fig, ax = plt.subplots(figsize=(10, 6))
for i, row in df.iterrows():
    ax.barh(i, row['及格'], color='#d3d3d3', height=0.5)
    ax.barh(i, row['良好'], left=row['及格'], color='#a9a9a9', height=0.5)
    ax.barh(i, row['优秀'], left=row['及格']+row['良好'], color='#808080', height=0.5)
sns.barplot(y='商品', x='实际', data=df, color='#4C72B0', ax=ax, label='实际')
for i, row in df.iterrows():
    ax.plot([row['目标'], row['目标']], [i-0.25, i+0.25], color='red', linewidth=3, label='目标' if i==0 else "")
    ax.text(row['实际'] + 10, i, str(int(row['实际'])), va='center')
ax.set_title('25. 子弹图 (实际/目标/指标)')
ax.legend(loc='lower right')
plt.savefig(fig_dir + '25_子弹图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 26. 柱形圆
# ==========================================
df = get_df(file2, '26 柱形圆', '区域').dropna(subset=['区域'])[['区域', '销量', '同比去年']].dropna()
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='区域', y='销量', data=df, color='#4C72B0', ax=ax)
for i, row in df.iterrows():
    ax.text(i, row['销量']+50, str(int(row['销量'])), ha='center', va='bottom')
    ax.text(i, 50, f"同比\n{row['同比去年']*100:.1f}%", ha='center', color='white', fontweight='bold')
ax.set_title('26. 柱形圆 (带比例)')
plt.savefig(fig_dir + '26_柱形圆.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 27. 簇状柱形折线图
# ==========================================
df = get_df(file2, '27 簇状柱形折线图', '区域').dropna(subset=['区域'])[['区域', '2022销量', '2021销量', '同比去年']].dropna()
df_melt = df.melt(id_vars='区域', value_vars=['2022销量', '2021销量'], var_name='年份', value_name='销量')
fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()
sns.barplot(x='区域', y='销量', hue='年份', data=df_melt, ax=ax1)
for p in ax1.patches:
    ax1.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom', fontsize=9)
ax2.plot(df['区域'], df['同比去年']*100, color='black', marker='o', linestyle='--', label='同比去年')
for i, v in enumerate(df['同比去年']*100): ax2.text(i, v+2, f"{v:.1f}%", ha='center')
ax1.set_title('27. 簇状柱形折线图')
ax2.legend(loc='upper right')
plt.savefig(fig_dir + '27_簇状柱形折线图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 28. 复合柱形图 (含季度分区)
# ==========================================
df = get_df(file2, '28 复合柱形图', '月份').dropna(subset=['月份'])[['月份', '月度销量']].dropna()
df['季度'] = df['月份'].str.extract(r'(\d+)').astype(int).apply(lambda x: (x-1)//3 + 1)
quarter_sums = df.groupby('季度')['月度销量'].sum()
fig, ax = plt.subplots(figsize=(12, 5))
sns.barplot(x='月份', y='月度销量', data=df, color='#4C72B0', label='月度销量', ax=ax)
for q in range(1, 5):
    start_idx = (q-1)*3
    rect = patches.Rectangle((start_idx-0.5, 0), 3, ax.get_ylim()[1]*0.8, linewidth=2, edgecolor='#C44E52', facecolor='none', linestyle='--')
    ax.add_patch(rect)
    ax.text(start_idx+1, ax.get_ylim()[1]*0.85, f"Q{q} 总计: {quarter_sums[q]}", ha='center', color='#C44E52', fontweight='bold')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom', fontsize=8)
ax.set_title('28. 复合柱形图')
ax.legend()
plt.savefig(fig_dir + '28_复合柱形图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 29. 滑珠图
# ==========================================
df = get_df(file2, '29 滑珠图', '区域').dropna(subset=['区域'])[['区域', '完成率']].dropna()
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(df['区域'], [1]*len(df), color='#e0e0e0', height=0.4)
ax.barh(df['区域'], df['完成率'], color='#4C72B0', height=0.4)
for i, row in enumerate(df['完成率']):
    ax.plot(row, i, marker='o', markersize=15, color='white', markeredgecolor='#4C72B0', markeredgewidth=2, zorder=10)
    ax.text(row / 2, i, f"{row*100:.1f}%", ha='center', va='center', color='white', fontweight='bold')
ax.set_xlim(0, 1.1); ax.set_xticks([])
ax.set_title('29. 滑珠图')
plt.savefig(fig_dir + '29_滑珠图.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# 30. 对比滑珠图 (双圆球)
# ==========================================
df = get_df(file2, '30 对比滑珠图', '区域').dropna(subset=['区域'])[['区域', '2022完成率', '2021完成率']].dropna()

fig, ax = plt.subplots(figsize=(10, 6))
# 1. 画背景灰色等长横条
ax.barh(df['区域'], [1]*len(df), color='#e0e0e0', height=0.4)

# 2. 画 2022 年进度条并保留一个小圆球
ax.barh(df['区域'], df['2022完成率'], color='#4C72B0', height=0.4)
for i, row in enumerate(df['2022完成率']):
    ax.plot(row, i, marker='o', markersize=15, color='#4C72B0', markeredgecolor='white', markeredgewidth=2, zorder=10)
    ax.text(row - 0.05, i, f"{row*100:.1f}%", ha='right', va='center', color='black', fontsize=9)

# 3. 画 2021 年进度条并保留一个小圆球（换种颜色区分）
for i, row in enumerate(df['2021完成率']):
    ax.plot(row, i, marker='o', markersize=10, color='#ff7f0e', markeredgecolor='white', markeredgewidth=1, zorder=11)
    ax.text(row + 0.03, i, f"{row*100:.1f}%", ha='left', va='center', color='#ff7f0e', fontsize=9)

ax.set_xlim(0, 1.1)
ax.set_xticks([])
ax.set_title('30. 对比滑珠图 (2022 vs 2021)')
plt.savefig(fig_dir + '30_对比滑珠图.png', dpi=300, bbox_inches='tight')
plt.close()
