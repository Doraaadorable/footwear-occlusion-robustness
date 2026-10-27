"""Validate published reproduction metadata without ML dependencies."""
from pathlib import Path
import json
import math

root = Path(__file__).resolve().parents[1] / "evidence/reproduction_check"
summary = json.loads((root / "summary.json").read_text())
assert summary["status"] == "completed"
assert summary["training_receipts"] == 12
assert summary["executed_code_cells"] == 14
assert summary["protected_artifacts_unchanged"]
assert not summary["formal_models_replaced"]
comparisons = json.loads((root / "validation_comparison.json").read_text())
assert len(comparisons) == 12
assert len({row["fit"] for row in comparisons}) == 12
for row in comparisons:
    receipt = json.loads((root / (row["fit"] + ".json")).read_text())
    assert receipt["device"] == "cuda"
    assert math.isfinite(receipt["val_loss"])
    assert receipt["val_loss"] == row["reproduced_val_loss"] == row["formal_val_loss"]
    assert len(receipt["sha256"]) == 64
    int(receipt["sha256"], 16)
print("All 12 published reproduction receipt comparisons passed.")
