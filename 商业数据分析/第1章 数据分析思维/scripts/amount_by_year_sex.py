import sys
from pathlib import Path as _P

sys.path.insert(0, str(_P(__file__).resolve().parent))
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

DATA_DIR = _P(__file__).resolve().parents[1] / 'data'
FIG_DIR = _P(__file__).resolve().parents[1] / 'figures'

# 1. 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 2. 读取数据
trans = pd.read_csv(DATA_DIR / 'trans.csv', encoding='gbk', low_memory=False)
disp = pd.read_csv(DATA_DIR / 'disp.csv', encoding='gbk')
clients = pd.read_csv(DATA_DIR / 'clients.csv', encoding='gbk')

# 3. 强制统一关联键的数据类型
trans['account_id'] = trans['account_id'].astype(str).str.strip()
disp['account_id'] = disp['account_id'].astype(str).str.strip()
disp['client_id'] = disp['client_id'].astype(str).str.strip()
clients['client_id'] = clients['client_id'].astype(str).str.strip()

# 4. 数据清洗与特征提取
trans['amount'] = pd.to_numeric(trans['amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0)

trans['year'] = pd.to_datetime(trans['date'], errors='coerce').dt.year
if trans['year'].isna().all():
    trans['year'] = pd.to_datetime(trans['date'], format='%y%m%d', errors='coerce').dt.year

# 5. 表关联
disp['type_clean'] = disp['type'].astype(str).str.strip()
disp_owner = disp[disp['type_clean'] == '所有者']

merged_df = trans.merge(disp_owner, on='account_id', how='inner')
merged_df = merged_df.merge(clients, on='client_id', how='inner')

# 6. 分组聚合与透视
summary_df = merged_df.groupby(['year', 'sex'])['amount'].sum().reset_index()
pivot_df = summary_df.pivot(index='year', columns='sex', values='amount').fillna(0)

# 7. 绘制面积图
fig, ax = plt.subplots(figsize=(10, 6))

colors = ['#87CEFA', '#3A5FCD']
if not pivot_df.empty:
    pivot_df.plot.area(ax=ax, color=colors[:len(pivot_df.columns)], alpha=0.8)
else:
    print("警告：清洗和关联后没有剩下任何数据，请检查年份或性别数据是否为空！")

# 8. 图表美化与格式设置
ax.set_title('amount 的总和(按 年 和 sex)', loc='left', fontsize=14)
ax.set_xlabel('年', fontsize=12)
ax.set_ylabel('amount 的总和', fontsize=12)

def millions_formatter(x, pos):
    return f'{int(x / 1000000)} 百万'
ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

plt.legend(title='sex', loc='upper left', frameon=False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
FIG_DIR.mkdir(exist_ok=True)
plt.savefig(FIG_DIR / 'amount_by_year_sex.png', dpi=150, bbox_inches='tight')
plt.show()