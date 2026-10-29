"""Apply the provenance and descriptor-probe review to the verified integrated ZIP.

Source experiments are retained. Default execution does not retrain any model.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json

SOURCE_SHA = 'fa4c9f522cd0e6a29de139485080fa473513d4a047b28add14e1781eb5606d77'


def load_builder():
    path=Path(__file__).with_name('build_integrated_submission.py')
    spec=importlib.util.spec_from_file_location('reviewed_integration_builder',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def revise(source_zip,output_dir,run=False):
    builder=load_builder()
    source_zip=Path(source_zip).resolve()
    output=Path(output_dir).resolve()
    assert builder.sha(source_zip)==SOURCE_SHA,'Unexpected integrated source version. Preserve it and request review.'
    output.mkdir(parents=True,exist_ok=True)
    project=output/'MGSC673_Integrated_Project'
    assert not project.exists(),'Use a new output directory; old projects are not overwritten.'
    root,inventory=builder.extract_verified(source_zip,output,SOURCE_SHA)
    assert root==project
    notebook_path=project/'MGSC673_Project.ipynb'
    notebook=json.loads(notebook_path.read_text())
    original_training_source=next(''.join(c['source']) for c in notebook['cells'] if ''.join(c['source']).startswith('HANDIPRINT_TRAINING_SOURCE ='))
    changes=[]
    for index,cell in enumerate(notebook['cells']):
        source=''.join(cell['source'])
        if source.startswith("lock=json.loads((HROOT/'results/plan_lock.json')"):
            cell['source']=builder.HP_ANALYSIS.splitlines(keepends=True)
            changes.append({'cell':index,'purpose':'display existing descriptor controls; unchanged predictions and bootstrap method'})
        elif source.startswith('import matplotlib.pyplot as plt\nfrom matplotlib.patches import FancyBboxPatch'):
            cell['source']=builder.REPORT.splitlines(keepends=True)
            changes.append({'cell':index,'purpose':'add qualified descriptor-probe and mask-range interpretation to Stage 1 report'})
        elif cell['cell_type']=='markdown' and 'Save the executed notebook before running the independent packager.' in source:
            cell['source']=source.replace('Save the executed notebook before running the independent packager.','Tables, figures, the integrated report and preserved evidence are available in the documented package directories. Packaging instructions are in README.md.').splitlines(keepends=True)
            changes.append({'cell':index,'purpose':'remove author-facing packaging reminder'})
        if cell['cell_type']=='code':
            ast.parse(''.join(cell['source']))
            cell['outputs']=[]
            cell['execution_count']=None
    assert len(changes)==3,changes
    assert next(''.join(c['source']) for c in notebook['cells'] if ''.join(c['source']).startswith('HANDIPRINT_TRAINING_SOURCE ='))==original_training_source
    notebook_path.write_text(json.dumps(notebook,indent=1)+'\n')
    before_provenance=builder.sha(project/'DATA_PROVENANCE.md')
    (project/'DATA_PROVENANCE.md').write_text(builder.PROVENANCE)
    (project/'README.md').write_text(builder.README)
    (project/'build_submission.py').write_text(builder.PACKAGER)
    (project/'REVISION_NOTES.json').write_text(json.dumps({
        'source_integrated_archive_sha256':SOURCE_SHA,
        'source_inventory_entries_verified':len(inventory),
        'changes':changes,
        'previous_data_provenance_sha256':before_provenance,
        'revised_data_provenance_sha256':builder.sha(project/'DATA_PROVENANCE.md'),
        'models_predictions_inputs_and_split_preserved':True,
        'new_cnn_training':False,
        'interpretation':'Unmodified-image descriptor controls do not demonstrate CNN feature use or explain masked performance causally. The 80% target is limited nominal-severity extrapolation within one simulator family.'
    },indent=2)+'\n')
    # The verified source inventory no longer describes the edited clone.
    # Keep the original ZIP untouched; the packager creates a new ZIP inventory.
    (project/'PACKAGE_SHA256.json').unlink()
    if run:
        builder.execute(project)
        # Require every immutable input, model and recorded source table unchanged.
        for relative,digest in inventory.items():
            if relative.startswith(('input/','legacy/','histories/','reproduction_check/')):
                assert builder.sha(project/relative)==digest,relative
        return builder.package(project)
    print('Revised candidate assembled, not executed:',project)
    return project


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-zip',required=True,type=Path)
    parser.add_argument('--output-dir',required=True,type=Path)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    revise(args.source_zip,args.output_dir,args.execute)


if __name__=='__main__':main()
