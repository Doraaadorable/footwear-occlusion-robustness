"""Check published Handiprint metadata, table consistency and notebook syntax."""
from pathlib import Path
import ast
import csv
import json
import math

root = Path(__file__).resolve().parents[1] / 'experiments/handiprint_gpu'
summary = json.loads((root / 'evidence/gpu_reproduction_summary.json').read_text())
assert summary['status'] == 'completed' and summary['device'] == 'cuda'
assert summary['executed_code_cells'] == 23
assert summary['protected_inputs_unchanged']
assert summary['original_split_sha256'] == '20f942824a8c45c102837998cf2eb0b9f6d8cc9b243fa1ae87bef3db4f03d11d'
with (root / 'tables/test_metrics.csv').open() as handle:
    metrics = {(row['model'], row['target_fraction']): float(row['balanced_accuracy']) for row in csv.DictReader(handle)}
assert len(metrics) == 10
with (root / 'tables/paired_model_differences.csv').open() as handle:
    differences = list(csv.DictReader(handle))
assert len(differences) == 5
for row in differences:
    fraction = row['target_fraction']
    gain = metrics['occlusion_augmented', fraction] - metrics['original', fraction]
    assert math.isclose(gain, float(row['delta_balanced_accuracy']), abs_tol=1e-12)
notebook = json.loads((root / 'Handiprint_GPU_Reproduction.ipynb').read_text())
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        ast.parse(''.join(cell['source']))
        assert not cell.get('outputs') and cell.get('execution_count') is None
print('Handiprint GPU metadata, table differences and public notebook checks passed.')
