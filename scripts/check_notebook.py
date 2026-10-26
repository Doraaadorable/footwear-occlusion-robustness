"""Check public notebook syntax and ensure private outputs are absent."""
from pathlib import Path
import ast
import json

root = Path(__file__).resolve().parents[1]
notebook = json.loads((root / "notebooks/MGSC673_Project.ipynb").read_text())
for index, cell in enumerate(notebook["cells"]):
    if cell["cell_type"] == "code":
        ast.parse("".join(cell["source"]), filename=f"cell_{index}")
        assert not cell.get("outputs"), f"Unexpected output in cell {index}"
        assert cell.get("execution_count") is None
print("Public notebook syntax and output checks passed.")
