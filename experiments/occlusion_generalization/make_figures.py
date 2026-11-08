"""Draw the occlusion-generalisation figures from outputs/metrics.csv and outputs/paired_differences.csv.

Usage: python make_figures.py [extension]   (default: svg, written to assets/)
"""
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
EXT = sys.argv[1] if len(sys.argv) > 1 else "svg"
OUT = HERE / "assets"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "none", "svg.hashsalt": "fixed"})
LABEL = {
    "rect_white": "White rectangle (training family)",
    "blob_white": "Irregular blobs",
    "stripes_white": "Stripes",
    "partial_contact": "Partial contact (toe/heel)",
    "rect_dark": "Dark rectangle",
    "rect_texture": "Textured patch",
    "fade": "Fading",
    "noise": "Gaussian noise",
    "blur": "Blur",
}
REMOVAL = {"rect_white", "blob_white", "stripes_white", "partial_contact", "rect_dark", "rect_texture"}


def level_text(family, level):
    if family in REMOVAL:
        return f"{round(level * 100)}% of box"
    if family == "fade":
        return f"{round(level * 100)}% contrast kept"
    if family == "noise":
        return f"sd {level:g}"
    return f"sigma {level:g} px"


metrics = pd.read_csv(HERE / "outputs/metrics.csv").query("split == 'test'")
diffs = pd.read_csv(HERE / "outputs/paired_differences.csv").query("split == 'test'")

# Figure 1: paired gain per family and level.
rows = []
for fam in LABEL:
    for _, r in diffs[diffs.family == fam].sort_values("level").iterrows():
        rows.append((fam, r.level, 100 * r.delta_balanced_accuracy, 100 * r.ci_low, 100 * r.ci_high))
fig, ax = plt.subplots(figsize=(7.4, 8.2))
ys = np.arange(len(rows))[::-1]
for y, (fam, level, gain, lo, hi) in zip(ys, rows):
    colour = "#2563eb" if fam == "rect_white" else "#b91c1c" if hi < 0 else "#15803d" if lo > 0 else "#64748b"
    ax.plot([lo, hi], [y, y], color=colour, lw=2)
    ax.plot(gain, y, "o", color=colour, ms=5)
ax.axvline(0, color="black", lw=0.8)
ax.set_yticks(ys, [f"{LABEL[f]} · {level_text(f, lv)}" for f, lv, *_ in rows], fontsize=8)
ax.set_xlim(-50, 50)
ax.set_xlabel("Augmented minus original balanced accuracy (percentage points)")
ax.set_title("Occlusion augmentation helps on its training family, not on most held-out ones\n"
             "Test set, 16 shoe pairs, 5 mask draws per level, 95% pair-bootstrap intervals", fontsize=9.5)
fig.text(0.01, 0.005, "Blue: training family. Green: interval above 0. Red: interval below 0. "
         "Grey: interval includes 0.", fontsize=7.5)
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(OUT / f"gain_by_family.{EXT}", dpi=110)

# Figure 2: balanced accuracy curves for both models.
fig, axes = plt.subplots(3, 3, figsize=(9, 7.6), sharey=True)
for ax, fam in zip(axes.ravel(), LABEL):
    for model, colour, name in [("original", "#64748b", "Original"),
                                ("occlusion_augmented", "#2563eb", "Occlusion-augmented")]:
        t = metrics[(metrics.family == fam) & (metrics.model == model)].sort_values("level")
        ax.plot(t.level, 100 * t.balanced_accuracy, "o-", color=colour, label=name, ms=4)
        ax.fill_between(t.level, 100 * t.ci_low, 100 * t.ci_high, color=colour, alpha=0.15, lw=0)
    ax.axhline(50, color="grey", ls=":", lw=0.8)
    ax.set_ylim(40, 103)
    ax.set_xticks(t.level)
    ax.set_title(LABEL[fam], fontsize=9)
axes[0, 0].legend(fontsize=7.5, loc="lower left")
for ax in axes[:, 0]:
    ax.set_ylabel("Test balanced accuracy (%)")
fig.suptitle("Balanced accuracy under each corruption family (test set, 95% pair-bootstrap bands)", fontsize=10)
fig.tight_layout()
fig.savefig(OUT / f"accuracy_by_family.{EXT}", dpi=100)
print("Figures written to", OUT)
