"""Run the preserved Handiprint analysis in a fresh CUDA kernel and unique folder."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True, type=Path)
    args = parser.parse_args()
    import torch
    import nbformat
    from nbclient import NotebookClient

    if not torch.cuda.is_available():
        raise RuntimeError('CUDA is required; CPU fallback is disabled.')
    project = args.project_root.resolve()
    manifest = project / 'data/split_manifest_final.csv'
    expected = '20f942824a8c45c102837998cf2eb0b9f6d8cc9b243fa1ae87bef3db4f03d11d'
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == expected
    assert (project / 'data/Handiprint_database.xlsx').is_file()
    assert (project / 'data/Handiprint_images').is_dir()
    source = Path(__file__).resolve().parents[1] / 'experiments/handiprint_gpu/Handiprint_GPU_Reproduction.ipynb'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run = project / 'results/handiprint_gpu_reproduction' / stamp
    run.mkdir(parents=True, exist_ok=False)
    source_copy = run / source.name
    source_copy.write_bytes(source.read_bytes())
    notebook = nbformat.read(source_copy, as_version=4)
    notebook_path = run / 'Handiprint_GPU_Reproduction_Executed.ipynb'
    config = {
        'PROJECT_ROOT': str(project),
        'IMAGE_DIR': str(project / 'data/Handiprint_images'),
        'RESULTS_DIR': str(run / 'results'),
        'NOTEBOOK_SMOKE': '0',
    }
    (run / 'run_config.json').write_text(json.dumps(config, indent=2))
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in [manifest, project / 'data/Handiprint_database.xlsx']}
    log = (run / 'execution_log.txt').open('x', encoding='utf-8')

    def emit(message):
        print(message, flush=True)
        log.write(message + '\n')
        log.flush()

    def starting(cell, cell_index, **kwargs):
        if cell.cell_type == 'code':
            emit(f'Executing cell {cell_index + 1}/{len(notebook.cells)}')

    def finished(cell, **kwargs):
        for output in cell.get('outputs', []):
            if output.get('output_type') == 'stream':
                emit(output.get('text', '').rstrip())

    previous = {key: os.environ.get(key) for key in config}
    try:
        os.environ.update(config)
        subprocess.check_call([sys.executable, '-m', 'ipykernel', 'install', '--user', '--name', 'handiprint_gpu_cli', '--display-name', 'Handiprint GPU CLI'])
        emit('Starting separate GPU reproduction; prior test exposure remains exploratory.')
        NotebookClient(notebook, timeout=None, kernel_name='handiprint_gpu_cli', resources={'metadata': {'path': str(run)}}, on_cell_start=starting, on_cell_executed=finished).execute()
        for path, digest in before.items():
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        environment = json.loads((run / 'results/environment.json').read_text())
        assert environment['device'] == 'cuda'
        assert (run / 'results/extension/test_metrics.csv').is_file()
        emit(f'Complete. Outputs: {run}')
    finally:
        nbformat.write(notebook, notebook_path)
        log.close()
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == '__main__':
    main()
