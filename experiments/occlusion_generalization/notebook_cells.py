"""Cell source for the Colab notebooks; used by build_notebooks.py. Not meant to be run directly."""
md("## Step 1. Settings (edit these paths)")
code(r'''
from pathlib import Path
import os

# Your Drive project folder. data/ inside it is filled from public sources in Step 2 if anything is missing.
PROJECT_ROOT = Path('/content/drive/MyDrive/FOOTWEAR_PRIVATE_PROJECT')

# Optional: folder holding the PUBLISHED heads (models/ and extension/ from the original results ZIP).
# Leave as None to evaluate the heads retrained in Step 4.
SAVED_RESULTS_DIR = None

# Corruption families to evaluate.
FAMILIES_TO_RUN = __FAMILIES__

REPO_URL = 'https://github.com/Doraaadorable/footwear-occlusion-robustness.git'
REPO_BRANCH = 'main'
REPO_DIR = Path('/content/footwear-occlusion-robustness')

if str(PROJECT_ROOT).startswith('/content/drive'):
    from google.colab import drive
    drive.mount('/content/drive', force_remount=True)

import torch
assert torch.cuda.is_available(), 'Switch the runtime to GPU: Runtime > Change runtime type > T4 GPU.'
print('GPU:', torch.cuda.get_device_name(0))
PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
print('Project folder:', PROJECT_ROOT)
''')

md("## Step 2. Get the code and matching package versions")
code(r'''
import subprocess, sys
if not REPO_DIR.exists():
    subprocess.check_call(['git', 'clone', '--depth', '1', '--branch', REPO_BRANCH, REPO_URL, str(REPO_DIR)])
assert (REPO_DIR / 'experiments/occlusion_generalization/occlusion_families.py').exists(), \
    'This branch has no occlusion_generalization code. Check REPO_BRANCH in Step 1.'
commit = subprocess.check_output(['git', '-C', str(REPO_DIR), 'rev-parse', 'HEAD']).decode().strip()
print('Repository commit:', commit)

# Versions used by the original GPU run (experiments/handiprint_gpu/evidence/environment.json).
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q',
                       'scikit-learn==1.6.1', 'scikit-image==0.25.2', 'openpyxl'])
# If Colab asks to restart the session after this install, restart it and run again from Step 1.
sys.path.insert(0, str(REPO_DIR / 'experiments/occlusion_generalization'))
import occlusion_families as of
import sklearn, skimage, numpy, torchvision
print('sklearn', sklearn.__version__, '| skimage', skimage.__version__,
      '| numpy', numpy.__version__, '| torch', torch.__version__, '| torchvision', torchvision.__version__)

# Fill in any missing inputs from public sources: the split manifest from this repository,
# the metadata sheet and scans from the ShoeCase record. Every scan is checked against the manifest's SHA-256.
needed = [PROJECT_ROOT / 'data/split_manifest_final.csv', PROJECT_ROOT / 'data/Handiprint_database.xlsx']
manifest_rows = None
if all(p.exists() for p in needed):
    import pandas as _pd
    _m = _pd.read_csv(needed[0]); _m = _m[_m.split.isin(['train', 'val', 'test'])]
    manifest_rows = sum((PROJECT_ROOT / 'data/Handiprint_images' / p).exists() for p in _m.matched_path), len(_m)
if manifest_rows is None or manifest_rows[0] < manifest_rows[1]:
    subprocess.check_call([sys.executable, str(REPO_DIR / 'scripts/fetch_handiprint_images.py'),
                           '--project-root', str(PROJECT_ROOT), '--zip-path', '/content/handiprint.zip'])
for name in ['data/Handiprint_database.xlsx', 'data/split_manifest_final.csv', 'data/Handiprint_images']:
    assert (PROJECT_ROOT / name).exists(), f'Missing {PROJECT_ROOT / name}'
print('Project inputs ready.')
''')

md("## Step 3. Lock the evaluation plan before any results are computed")
code(r'''
import json, hashlib, datetime
STAMP = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
OUT = PROJECT_ROOT / 'results' / __OUTNAME__ / STAMP
OUT.mkdir(parents=True, exist_ok=False)

PLAN = {
    'question': __QUESTION__,
    'families': {f: of.ALL_FAMILIES[f] for f in FAMILIES_TO_RUN},
    'training_family': of.TRAINING_FAMILY,
    'removal_levels': of.REMOVAL_LEVELS,
    'degradation_levels': of.DEGRADATION_LEVELS,
    'draws_per_level': 5,
    'mask_seed': 2026,
    'bootstrap': {'resamples': 2000, 'unit': 'shoe pair within class', 'interval': '95% percentile'},
    'primary_estimate': __PRIMARY__,
    'secondary': ['validation split results', 'balanced accuracy versus realised ink coverage'],
    'status': 'exploratory: test pairs were examined in earlier work',
    'repository_commit': commit,
    'module_sha256': hashlib.sha256((REPO_DIR / 'experiments/occlusion_generalization/occlusion_families.py').read_bytes()).hexdigest(),
    'locked_at_utc': STAMP,
}
(OUT / 'evaluation_plan.json').write_text(json.dumps(PLAN, indent=2))
print('Plan locked:', hashlib.sha256((OUT / 'evaluation_plan.json').read_bytes()).hexdigest())
print('Outputs will be written to', OUT)
''')

md(r'''
## Step 4. Re-run the original Handiprint notebook in this kernel

This rebuilds the audited split, preprocessing, canvases and models exactly as in `experiments/handiprint_gpu/`. Its own outputs go to a new subfolder, so nothing earlier is overwritten. Expect most of the runtime here.
''')
code(r'''
# Set the paths both ways: as environment variables, and by working from the
# project folder, so the original notebook's '.' default also resolves correctly.
os.chdir(PROJECT_ROOT)
os.environ.update({
    'PROJECT_ROOT': str(PROJECT_ROOT),
    'IMAGE_DIR': str(PROJECT_ROOT / 'data/Handiprint_images'),
    'RESULTS_DIR': str(OUT / 'handiprint_rerun'),
    'NOTEBOOK_SMOKE': '0',
})
assert Path(os.environ['PROJECT_ROOT'], 'data/Handiprint_database.xlsx').is_file(), 'PROJECT_ROOT is wrong: re-run Step 1.'
print('Project folder:', os.getcwd())
source_nb = json.loads((REPO_DIR / 'experiments/handiprint_gpu/Handiprint_GPU_Reproduction.ipynb').read_text())
code_cells = [''.join(c['source']) for c in source_nb['cells'] if c['cell_type'] == 'code']
ip = get_ipython()
for i, src in enumerate(code_cells, 1):
    print(f'--- original notebook code cell {i}/{len(code_cells)}', flush=True)
    result = ip.run_cell(src)
    if not result.success:
        raise RuntimeError(f'Original notebook code cell {i} failed; see the error above.')
print('Original notebook finished.')
''')

md(r'''
## Step 5. Choose the models to evaluate and check they are the published ones

If `SAVED_RESULTS_DIR` is set, the published heads are loaded after checking their SHA-256 against `evidence/model_hashes.json`. Otherwise the heads retrained in Step 4 are used, and their hashes are compared with the published ones.

Either way, the 80% white-rectangle test result from the original extension is recomputed as a sanity check. It should match the published 53.75% / 95.00%.
''')
code(r'''
published = json.loads((REPO_DIR / 'experiments/handiprint_gpu/evidence/model_hashes.json').read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

orig_files = [f'models/resnet18_selected_frozen_backbone_seed{s}.pt' for s in SEEDS]
aug_files = [f'extension/occlusion_head_seed{s}.pt' for s in SEEDS]
model_source = {}

if SAVED_RESULTS_DIR is not None:
    base = Path(SAVED_RESULTS_DIR)
    def load_heads(files):
        models = []
        for f in files:
            assert sha(base / f) == published['results/' + f], f'Hash mismatch: {f}'
            m = ResNetHead(PRETRAINED, unfreeze_layer4=False).to(DEVICE)
            missing, unexpected = m.load_state_dict(torch.load(base / f, map_location=DEVICE), strict=False)
            assert not unexpected and all(k.startswith('backbone.') for k in missing)
            m.eval(); models.append(m)
        return models
    eval_original, eval_augmented = load_heads(orig_files), load_heads(aug_files)
    model_source = {'source': 'published heads', 'hashes_verified': True}
else:
    rerun = OUT / 'handiprint_rerun'
    match = {f: sha(rerun / f) == published['results/' + f] for f in orig_files + aug_files}
    eval_original, eval_augmented = original_models, occlusion_models
    model_source = {'source': 'retrained in this run', 'hash_matches_published': match}
print(json.dumps(model_source, indent=2))

# Sanity check against the published 80% extension result.
check = {}
for name, models in [('original', eval_original), ('occlusion_augmented', eval_augmented)]:
    batches, _ = masked_batches(te_df, 0.80)
    check[name] = float(np.mean([balanced_accuracy_score(yte, (ensemble_scores(models, b) > 0.5).astype(int)) for b in batches]))
published_80 = {'original': 0.5375, 'occlusion_augmented': 0.95}
print('80% white-rectangle test BA, recomputed:', check, '| published:', published_80)
model_source['sanity_check_80pct'] = {'recomputed': check, 'published': published_80}
(OUT / 'model_source.json').write_text(json.dumps(model_source, indent=2))
''')

md("## Step 6. Run the corruption families (validation first, then test)")
code(r'''
import pandas as pd
models = {'original': eval_original, 'occlusion_augmented': eval_augmented}

def split_inputs(df):
    canvases = [canv[k].astype(np.float32) / 255.0 for k in df['key']]
    boxes = [box_of(r) for _, r in df.iterrows()]
    return canvases, boxes, df['key'].tolist(), df['y'].to_numpy(), df['pair_id'].to_numpy()

all_metrics, all_diffs = [], []
for split_name, df in [('val', va_df), ('test', te_df)]:
    canvases, boxes, keys, y, pairs = split_inputs(df)
    metrics, diffs, preds, masks = of.evaluate(
        models, ensemble_scores, canvases, boxes, keys, y, pairs,
        seed=PLAN['mask_seed'], draws=PLAN['draws_per_level'],
        n_boot=PLAN['bootstrap']['resamples'], families=FAMILIES_TO_RUN)
    for rows, store in [(metrics, all_metrics), (diffs, all_diffs)]:
        store.extend({'split': split_name, **r} for r in rows)
    pd.DataFrame(preds).assign(split=split_name).to_csv(OUT / f'predictions_{split_name}.csv.gz', index=False)
    pd.DataFrame(masks).assign(split=split_name).to_csv(OUT / f'mask_log_{split_name}.csv.gz', index=False)
    print(split_name, 'done:', len(df), 'images')

metrics_df = pd.DataFrame(all_metrics); diffs_df = pd.DataFrame(all_diffs)
metrics_df.to_csv(OUT / 'metrics.csv', index=False)
diffs_df.to_csv(OUT / 'paired_differences.csv', index=False)
print('Saved metrics and paired differences.')
''')

md("## Step 7. Results")
code(r'''
pd.set_option('display.width', 160)
test = diffs_df[diffs_df.split == 'test'].copy()
test['gain_pp'] = (100 * test.delta_balanced_accuracy).round(1)
test['ci_pp'] = test.apply(lambda r: f'[{100*r.ci_low:.1f}, {100*r.ci_high:.1f}]', axis=1)
ba = metrics_df[metrics_df.split == 'test'].pivot_table(index=['family', 'level'], columns='model', values='balanced_accuracy')
table = ba.join(test.set_index(['family', 'level'])[['held_out', 'gain_pp', 'ci_pp']])
table['original'] = (100 * table['original']).round(1)
table['occlusion_augmented'] = (100 * table['occlusion_augmented']).round(1)
order = ['clean'] + list(FAMILIES_TO_RUN)
table = table.reset_index()
table['family'] = pd.Categorical(table['family'], order, ordered=True)
table = table.sort_values(['family', 'level'])
table.to_csv(OUT / 'summary_test.csv', index=False)
display(table)
''')
code(r'''
import matplotlib.pyplot as plt
fams = list(FAMILIES_TO_RUN)
ncol = 3; nrow = -(-len(fams) // ncol)
fig, axes = plt.subplots(nrow, ncol, figsize=(12, 3.4 * nrow), sharey=True, squeeze=False)
for ax in axes.ravel()[len(fams):]: ax.axis('off')
t = metrics_df[metrics_df.split == 'test']
for ax, fam in zip(axes.ravel(), fams):
    for model, colour in [('original', '#64748b'), ('occlusion_augmented', '#2563eb')]:
        d = t[(t.family == fam) & (t.model == model)].sort_values('level')
        ax.plot(d.level, 100 * d.balanced_accuracy, 'o-', color=colour, label=model)
        ax.fill_between(d.level, 100 * d.ci_low, 100 * d.ci_high, color=colour, alpha=0.15)
    ax.axhline(50, color='grey', ls=':', lw=0.8)
    ax.set_title(fam + ('' if fam != of.TRAINING_FAMILY else '  (training family)'), fontsize=10)
    ax.set_ylim(35, 102)
axes[0, 0].legend(fontsize=8)
for ax in axes[:, 0]: ax.set_ylabel('Test balanced accuracy (%)')
for ax in axes.ravel()[:len(fams)][-ncol:]: ax.set_xlabel('Level')
fig.suptitle('Original vs occlusion-augmented heads by corruption family (test set, 95% pair-bootstrap bands)')
fig.tight_layout(); fig.savefig(OUT / 'families_test.png', dpi=160); plt.show()

# Balanced accuracy versus realised ink coverage, removal families only.
preds = pd.read_csv(OUT / 'predictions_test.csv.gz')
masks = pd.read_csv(OUT / 'mask_log_test.csv.gz')
m = preds.merge(masks[['key', 'family', 'level', 'draw', 'ink_coverage']], on=['key', 'family', 'level', 'draw'])
m = m[m.family.map(of.ALL_FAMILIES).eq('removal')]
m['ink_bin'] = pd.cut(m.ink_coverage, [0, .2, .4, .6, .8, 1.0], include_lowest=True)
m['correct'] = ((m.score_nike > 0.5).astype(int) == m.y_true).astype(int)
by_bin = (m.groupby(['model', 'ink_bin', 'y_true'], observed=True).correct.mean()
            .groupby(['model', 'ink_bin'], observed=True).mean().unstack('model'))
counts = m[m.model == 'original'].groupby('ink_bin', observed=True).size().rename('n_image_draws')
by_bin = by_bin.join(counts)
by_bin.to_csv(OUT / 'ba_by_ink_coverage_test.csv')
display((by_bin[['original', 'occlusion_augmented']] * 100).round(1).join(counts))
''')

md("## Step 8. Package the results to send back")
code(r'''
import shutil
summary = {
    'plan_sha256': hashlib.sha256((OUT / 'evaluation_plan.json').read_bytes()).hexdigest(),
    'model_source': model_source,
    'n_test_images': int(len(te_df)), 'n_test_pairs': int(te_df.pair_id.nunique()),
    'n_val_images': int(len(va_df)), 'n_val_pairs': int(va_df.pair_id.nunique()),
}
(OUT / 'run_summary.json').write_text(json.dumps(summary, indent=2))
# Exclude the large re-run folder (models, cache); keep its small tables and evidence.
pack = OUT.parent / f'{__OUTNAME__}_{STAMP}'
shutil.copytree(OUT, pack, ignore=shutil.ignore_patterns('cache', 'models', '*.pt', '*.npz', '*.joblib', '*.zip'))
archive = shutil.make_archive(str(pack), 'zip', pack)
shutil.rmtree(pack)
print('Send this file back:', archive)
try:
    from google.colab import files
    files.download(archive)
except Exception as exc:
    print('Download it from Drive instead:', exc)
''')

