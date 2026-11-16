import json, sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch

R = "/home/claude/handoff/NSL_Team_Handoff/repo/"
cjk = [f for f in fm.findSystemFonts() if "NotoSansCJK" in f and "Regular" in f]
fm.fontManager.addfont(cjk[0]); CJK = fm.FontProperties(fname=cjk[0]).get_name()
BLUE, GREY, RED, INK, MUT = "#1F5FBF", "#9AA3B2", "#D9322E", "#1D2330", "#5B6475"

for lang in ("en", "zh"):
    zh = lang == "zh"
    plt.rcParams["font.family"] = [CJK] if zh else ["DejaVu Serif"]
    T = lambda a, b: a if zh else b
    NM = ({"C": "C 站城连接", "M": "M 步行换乘", "F": "F 导向标识", "V": "V 垂直交通", "D": "D 拥挤人流", "T": "T 热舒适", "Q": "Q 清洁维护", "A": "A 设施停留", "L": "L 照明氛围"} if zh else
          {"C": "C connectivity", "M": "M walking/transfer", "F": "F wayfinding", "V": "V vertical access", "D": "D crowding", "T": "T thermal", "Q": "Q cleanliness", "A": "A amenities", "L": "L lighting"})

    # Fig 1 workflow
    fig, ax = plt.subplots(figsize=(3.4, 3.3)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    steps = [(T("采集", "Collect"), T("27 站 21,796 条评分\n按最新排序，2026-10-04", "27 stations, 21,796 ratings\nnewest-first, 4 Oct 2026")),
             (T("筛选与编码", "Screen & code"), T("词典标出 9 个方面\n3,884 条进入模型", "dictionary flags 9 aspects\n3,884 reviews in the model")),
             (T("人工检验", "Human check"), T("两人独立编码 100 条\nκ、裁决、冻结编码手册 v2", "two coders, 100 reviews\nκ, adjudication, codebook v2")),
             (T("建模", "Model"), T("提及 / 提及加正负 / 对照\n按站分组 5 折交叉验证", "mentions / + polarity / control\nstation-grouped 5-fold CV")),
             (T("解释与检验", "Explain & test"), T("置换重要性、排序稳定性\nWoodlands 前瞻检验", "permutation importance, rank\nstability, Woodlands check")),
             (T("证据卡与网站", "Evidence & site"), T("3 张车站证据卡\n交互地图", "3 station evidence cards\ninteractive map"))]
    for i, (h, b) in enumerate(steps):
        y = 9.0 - i * 1.6
        ax.add_patch(FancyBboxPatch((0.2, y - 0.62), 9.6, 1.24, boxstyle="round,pad=0.02,rounding_size=0.25", fc="#EEF3FA", ec="none"))
        ax.add_patch(plt.Circle((0.85, y), 0.32, fc="white", ec=RED, lw=1.6))
        ax.text(0.85, y, str(i + 1), ha="center", va="center", fontsize=7, color=RED, weight="bold")
        ax.text(1.5, y, h, ha="left", va="center", fontsize=7.5, weight="bold", color="#123B7A")
        ax.text(4.2 if zh else 4.9, y, b, ha="left", va="center", fontsize=6.2, color=INK, linespacing=1.25)
        if i < 5: ax.plot([0.85, 0.85], [y - 0.32, y - 1.28], color=RED, lw=1.6)
    fig.tight_layout(pad=0.2); fig.savefig(f"fig1_workflow_{lang}.png", dpi=300, facecolor="white"); plt.close(fig)

    # Fig 2 kappa
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    labs = [T("范围（7 类）", "Scope (7)"), T("车站空间 vs 其他", "Station vs other"), T("方面提及", "Aspect mention")]
    r1, r2 = [0.26, 0.29, 0.47], [0.77, 0.85, 0.67]; x = range(3)
    ax.bar([i - 0.18 for i in x], r1, 0.34, color=GREY, label=T("第一轮（60 条，v1）", "Round 1 (60, v1)"))
    ax.bar([i + 0.18 for i in x], r2, 0.34, color=BLUE, label=T("第二轮（40 条，v2）", "Round 2 (40, v2)"))
    for i in x:
        ax.text(i - 0.18, r1[i] + 0.02, f"{r1[i]:.2f}", ha="center", fontsize=6.5); ax.text(i + 0.18, r2[i] + 0.02, f"{r2[i]:.2f}", ha="center", fontsize=6.5)
    ax.set_xticks(list(x)); ax.set_xticklabels(labs, fontsize=6.8); ax.set_ylim(0, 1); ax.set_ylabel("Cohen's κ", fontsize=7); ax.tick_params(labelsize=6.5)
    ax.legend(fontsize=6.3, frameon=False, loc="upper left")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(f"fig2_kappa_{lang}.png", dpi=300, facecolor="white"); plt.close(fig)

    # Fig 3 importance (stacked)
    f = json.load(open(R + "model/results.json"))["factors"]
    order = sorted(f, key=lambda r: -r["mention_percent"]); y = list(range(9))[::-1]
    fig, ax = plt.subplots(2, 1, figsize=(3.4, 4.4))
    ax[0].barh(y, [r["mention_percent"] for r in order], color=GREY)
    for yy, r in zip(y, order): ax[0].text(r["mention_percent"] + 0.8, yy, f"{r['mention_percent']:.0f}%", va="center", fontsize=6.3)
    ax[0].set_xlim(0, 50); ax[0].set_title(T("(a) 提及该方面的评论比例（%）", "(a) Share of reviews mentioning (%)"), fontsize=7.3, loc="left")
    for yy, r in zip(y, order):
        ax[1].plot([r["logistic_ci_low"] * 100, r["logistic_ci_high"] * 100], [yy, yy], color=BLUE, lw=1.2)
        ax[1].plot(r["logistic_auc_drop"] * 100, yy, "o", color=BLUE, ms=3.3)
        ax[1].text(4.6, yy, T("第 %d", "rank %d") % r["logistic_importance_rank"], va="center", fontsize=6, color=MUT)
    ax[1].axvline(0, color="#999", ls="--", lw=0.6); ax[1].set_xlim(-1.5, 5.6)
    ax[1].set_title(T("(b) 打乱后 AUC 下降 ×100", "(b) AUC drop ×100 when shuffled"), fontsize=7.3, loc="left")
    for a in ax:
        a.set_yticks(y); a.set_yticklabels([NM[r["code"]] for r in order], fontsize=6.3); a.tick_params(axis="x", labelsize=6.3)
        for s in ("top", "right"): a.spines[s].set_visible(False)
    fig.tight_layout(h_pad=1.0); fig.savefig(f"fig3_importance_{lang}.png", dpi=300, facecolor="white"); plt.close(fig)

    # Fig 4 performance
    pol = json.load(open(R + "model/polarity_results.json"))["performance"]
    base = json.load(open(R + "model/results.json"))["performance"]
    rows = [(T("基线", "Base-\nline"), base["MajorityBaseline"]), (T("B\n逻辑", "B\nlogit"), pol["B_mention_logistic"]), (T("B\n森林", "B\nforest"), pol["B_mention_forest"]),
            (T("C\n逻辑", "C\nlogit"), pol["C_polarity_logistic"]), (T("C\n森林", "C\nforest"), pol["C_polarity_forest"]),
            (T("对照\n森林", "Ctrl\nforest"), pol["S_mention_plus_overall_sentiment_forest"]), (T("TF-IDF\n文本", "TF-IDF\ntext"), base["TextTFIDFLogisticRegression"])]
    fig, ax = plt.subplots(figsize=(3.4, 2.4)); x = range(len(rows))
    auc = [r[1]["mean_repeated_group_cv"]["auc"] for r in rows]; f1 = [r[1]["mean_repeated_group_cv"]["macro_f1"] for r in rows]
    ax.bar([i - 0.19 for i in x], auc, 0.36, color=BLUE, label="AUC"); ax.bar([i + 0.19 for i in x], f1, 0.36, color=GREY, label="Macro F1")
    for i in x: ax.text(i - 0.19, auc[i] + 0.015, f"{auc[i]:.2f}", ha="center", fontsize=5.3)
    ax.set_xticks(list(x)); ax.set_xticklabels([r[0] for r in rows], fontsize=6.2); ax.set_ylim(0, 0.9); ax.tick_params(axis="y", labelsize=6.3)
    ax.legend(fontsize=6.3, frameon=False, ncol=2, loc="upper left")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(f"fig4_performance_{lang}.png", dpi=300, facecolor="white"); plt.close(fig)

    # Fig 5 rank stability heatmap
    imp = json.load(open(R + "model/polarity_results.json"))["importance_and_rank_uncertainty"]
    ms = ["B_mention_logistic", "B_mention_forest", "C_polarity_logistic", "C_polarity_forest"]
    keys = ["C", "A", "V", "Q", "D", "M", "F", "T", "L"]
    import numpy as np
    M = np.array([[imp[m][k]["share_top3"] for m in ms] for k in keys])
    fig, ax = plt.subplots(figsize=(3.4, 2.9))
    ax.imshow(M, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    for i in range(len(keys)):
        for j in range(4): ax.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center", fontsize=6.3, color="white" if M[i, j] > .6 else INK)
    ax.set_xticks(range(4)); ax.set_xticklabels([T("B 逻辑", "B logistic"), T("B 森林", "B forest"), T("C 逻辑", "C logistic"), T("C 森林", "C forest")], fontsize=6.3)
    ax.set_yticks(range(len(keys))); ax.set_yticklabels([NM[k] for k in keys], fontsize=6.3); ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)
    fig.tight_layout(); fig.savefig(f"fig5_rankstability_{lang}.png", dpi=300, facecolor="white"); plt.close(fig)
print("ok")
