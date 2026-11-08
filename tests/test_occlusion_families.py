"""Unit tests for the held-out occlusion families (synthetic data, CPU only)."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments/occlusion_generalization"))
import occlusion_families as of  # noqa: E402

BOX = (40, 70, 200, 150)  # top, left, bottom, right


def synthetic_canvas(seed=0):
    rng = np.random.default_rng(seed)
    x = np.ones((224, 224), dtype=np.float32)
    top, left, bottom, right = BOX
    tread = (rng.random((bottom - top, right - left)) < 0.35).astype(np.float32)
    x[top:bottom, left:right] = 1.0 - 0.8 * tread
    return x


@pytest.mark.parametrize("family", list(of.FAMILIES))
def test_shape_range_and_determinism(family):
    canvas = synthetic_canvas()
    for level in of.levels_for(family):
        a, info = of.apply_family(canvas, BOX, family, level, of.make_rng(42, "k", family, level, 0))
        b, _ = of.apply_family(canvas, BOX, family, level, of.make_rng(42, "k", family, level, 0))
        assert a.shape == canvas.shape and a.dtype == np.float32
        assert a.min() >= 0.0 and a.max() <= 1.0
        np.testing.assert_array_equal(a, b)
        assert not np.array_equal(a, canvas)
        assert 0.0 <= info["ink_coverage"] <= 1.0 + 1e-6


@pytest.mark.parametrize("family", [f for f, kind in of.FAMILIES.items() if kind == "removal"])
def test_removal_area_and_locality(family):
    canvas = synthetic_canvas()
    top, left, bottom, right = BOX
    for level in of.REMOVAL_LEVELS:
        out, info = of.apply_family(canvas, BOX, family, level, of.make_rng(1, "k", family, level, 0))
        assert abs(info["area_fraction"] - level) < 0.08, (family, level, info)
        outside = np.ones_like(canvas, dtype=bool)
        outside[top:bottom, left:right] = False
        np.testing.assert_array_equal(out[outside], canvas[outside])


def test_rect_white_matches_notebook_rule():
    """rect_white must reproduce the notebook's severe_mask for the same RNG."""
    canvas = synthetic_canvas()
    level = 0.5

    def severe_mask(canvas_float, box, frac, rng):  # copied from the notebook, cell 39
        x = np.asarray(canvas_float, dtype=np.float32).copy()
        top, left, bottom, right = box
        h, w = bottom - top, right - left
        rel_h = float(np.exp(rng.uniform(np.log(frac), 0.0)))
        rel_w = frac / rel_h
        mh = max(1, min(h, int(round(rel_h * h))))
        mw = max(1, min(w, int(round(rel_w * w))))
        y0 = top + int(rng.integers(0, h - mh + 1))
        x0 = left + int(rng.integers(0, w - mw + 1))
        x[y0:y0 + mh, x0:x0 + mw] = 1.0
        return x

    ours, _ = of.apply_family(canvas, BOX, "rect_white", level, np.random.default_rng(7))
    theirs = severe_mask(canvas, BOX, level, np.random.default_rng(7))
    np.testing.assert_array_equal(ours, theirs)


def test_bootstrap_keeps_pairs_together_and_class_counts():
    pair_ids = np.array([1, 1, 2, 2, 3, 3, 4, 4])
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    w = of.pair_bootstrap_weights(pair_ids, y, 200, 0)
    assert w.shape == (200, 8)
    np.testing.assert_array_equal(w[:, 0], w[:, 1])
    np.testing.assert_array_equal(w[:, 4], w[:, 5])
    np.testing.assert_array_equal(w[:, :4].sum(1), 4)  # 2 pairs x 2 images
    np.testing.assert_array_equal(w[:, 4:].sum(1), 4)


def test_weighted_balanced_accuracy():
    y = np.array([0, 0, 1, 1])
    yhat = np.array([0, 1, 1, 1])
    assert of.weighted_balanced_accuracy(y, yhat, np.ones((1, 4)))[0] == pytest.approx(0.75)


def test_evaluate_end_to_end_with_dummy_models():
    """A score that reads total ink separates classes when clean, and is hurt by removal."""
    rng = np.random.default_rng(0)
    canvases, keys, y, pairs = [], [], [], []
    for p in range(8):
        label = p % 2
        for side in "LR":
            c = synthetic_canvas(seed=p * 2 + (side == "R"))
            if label == 1:
                c[BOX[0]:BOX[2], BOX[1]:BOX[3]] *= 0.8  # darker class
            canvases.append(c)
            keys.append(f"{p}{side}")
            y.append(label)
            pairs.append(p)
    y = np.array(y)

    def score_fn(models, images):
        ink = (1 - images).reshape(len(images), -1).mean(1)
        return 1 / (1 + np.exp(-(ink - models) * 200))

    clean_ink = float(np.mean([(1 - c).mean() for c in canvases]))
    models = {"original": clean_ink, "occlusion_augmented": clean_ink * 0.6}
    metrics, diffs, preds, masks = of.evaluate(
        models, score_fn, canvases, [BOX] * len(canvases), keys, y, pairs,
        seed=42, draws=2, n_boot=50, families=["rect_white", "fade"])
    clean = [m for m in metrics if m["family"] == "clean" and m["model"] == "original"][0]
    assert clean["balanced_accuracy"] == pytest.approx(1.0)
    assert {m["family"] for m in metrics} == {"clean", "rect_white", "fade"}
    assert len(diffs) == 1 + 2 * 3
    assert len(preds) == 2 * 3 * 2 * 2 * len(canvases)
    assert all(m["ci_low"] <= m["balanced_accuracy"] + 1e-9 for m in metrics)
    held = {m["family"]: m["held_out"] for m in metrics}
    assert held["rect_white"] is False and held["fade"] is True
