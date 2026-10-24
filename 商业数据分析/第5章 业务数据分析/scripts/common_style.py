# -*- coding: utf-8 -*-
"""
项目公共绘图风格模板 —— 所有章节脚本通过 `from common_style import *` 复用。

约定（与第1章已有示例 amount_by_year_sex.py 保持一致）：
- data/     存放原始数据（xlsx/csv，从教材目录原样拷贝）
- scripts/  存放 Python 脚本（每张图一个 .py）
- figures/  存放复现出的图表（与脚本同名 .png）
- 脚本可从任意工作目录运行（通过 Path(__file__) 定位，不依赖 cwd）
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")          # 无界面环境也能批量出图
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# 1. 目录定位：scripts/<脚本>.py -> 章节根 -> data/ figures/
SCRIPTS_DIR = Path(__file__).resolve().parent
CHAPTER_DIR = SCRIPTS_DIR.parent
DATA_DIR = CHAPTER_DIR / "data"
FIG_DIR = CHAPTER_DIR / "figures"
FIG_DIR.mkdir(exist_ok=True)

# 2. 中文字体
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False


def new_ax(figsize=(10, 6)):
    """新建画布与坐标轴。"""
    fig, ax = plt.subplots(figsize=figsize)
    return fig, ax


def beautify(ax, title, xlabel="", ylabel=""):
    """统一美化：左对齐标题、去上/右脊。"""
    ax.set_title(title, loc="left", fontsize=14)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def fmt_millions(x, pos):
    return f"{int(x / 1e6)} 百万"


def fmt_thousands(x, pos):
    return f"{int(x / 1e3)} 千"


MILLIONS = FuncFormatter(fmt_millions)
THOUSANDS = FuncFormatter(fmt_thousands)


def save(fig, name, dpi=150):
    """保存图片到 figures/，文件名 = 脚本名。"""
    out = FIG_DIR / f"{name}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    print(f"已保存: {out}")
    plt.close(fig)
