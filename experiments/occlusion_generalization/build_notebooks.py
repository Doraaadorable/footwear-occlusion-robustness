"""Build the Colab notebooks for this experiment from one source.

Run `python build_notebooks.py` after editing; it rewrites both .ipynb files.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

MAIN_INTRO = r'''
# Does occlusion augmentation generalise to unseen occluders?

The occlusion-augmented Handiprint heads were **trained and tested with the same white-rectangle generator**. This notebook asks whether the benefit survives occluders and degradations the model never saw: irregular blobs, stripes, partial contact, dark and textured rectangles, fading, noise and blur.

**Run this notebook, not `experiments/handiprint_gpu/Handiprint_GPU_Reproduction.ipynb`.** This one runs that notebook for you with the right paths.

**What you need:** a Colab GPU runtime (T4 is fine) and a Google Drive folder. Missing inputs are filled in Step 2 from public sources: the split manifest from this repository, and the scans from the ShoeCase record (about 2.1 GB, each checked against the manifest's SHA-256).

**Runtime:** about 30–40 minutes, mostly re-running the Handiprint stage to rebuild canvases and models.

**Interpretation rules, fixed before running:** the test pairs were examined in earlier work, so results are exploratory. The primary estimate is the augmented-minus-original balanced accuracy for each family and level, with a 95% pair-bootstrap interval. Every family is reported.
'''

FOLLOWUP_INTRO = r'''
# Follow-up: does the partial-contact result depend on fragment position?

In the first run, both models stayed at 100% when the toe or heel end of the impression was removed, even at 80% of its length. The remaining fragment kept its original position on the canvas, so its height may reveal the shoe's length, and crop geometry alone predicts the class at 93.75% on clean images.

This run removes **the same rows from the same random draws**, then moves the remaining fragment:

| Family | Fragment position |
|---|---|
| `partial_contact` | original position (repeats the first run exactly) |
| `partial_contact_centered` | moved to the centre of the canvas |
| `partial_contact_shifted` | moved to a random height |

**Pre-specified reading:** if accuracy stays near 100% after the fragment is moved, the result reflects tread in the fragment. If it falls well below the in-place value, position (shoe length) was carrying information. The fragment's width is unchanged, so width-related size cues remain in all three.

**Run this notebook, not the Handiprint notebook.** It needs a Colab GPU runtime and a Drive folder; inputs are filled from public sources in Step 2. Runtime is about 30–40 minutes.
'''

VARIANTS = [
    {
        "file": "Occlusion_Generalization_Colab.ipynb",
        "intro": MAIN_INTRO,
        "__FAMILIES__": "['rect_white', 'blob_white', 'stripes_white', 'partial_contact', 'rect_dark',\n                   'rect_texture', 'fade', 'noise', 'blur']",
        "__QUESTION__": "'Does the occlusion-augmentation benefit carry over to held-out occluder and degradation families?'",
        "__PRIMARY__": "'augmented minus original balanced accuracy, per family and level, on the test split'",
        "__OUTNAME__": "'occlusion_generalization'",
    },
    {
        "file": "Partial_Contact_Followup_Colab.ipynb",
        "intro": FOLLOWUP_INTRO,
        "__FAMILIES__": "['partial_contact', 'partial_contact_centered', 'partial_contact_shifted']",
        "__QUESTION__": "'Does accuracy on partial-contact impressions depend on where the remaining fragment sits on the canvas?'",
        "__PRIMARY__": "'balanced accuracy of each model for centered and shifted fragments compared with in-place fragments, per level, on the test split'",
        "__OUTNAME__": "'partial_contact_followup'",
    },
]

BODY = (HERE / 'notebook_cells.py').read_text().split('\n', 1)[1]
def build(variant):
    cells = []

    def md(s):
        cells.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n")})

    def code(s):
        cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                      "outputs": [], "source": s.strip("\n")})

    md(variant["intro"])
    body = BODY
    for key in ("__FAMILIES__", "__QUESTION__", "__PRIMARY__", "__OUTNAME__"):
        body = body.replace(key, variant[key])
    exec(body, {"md": md, "code": code})
    nb = {"cells": cells, "metadata": {"accelerator": "GPU", "colab": {"provenance": []},
          "kernelspec": {"display_name": "Python 3", "name": "python3"},
          "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    for i, c in enumerate(nb["cells"]):
        c["id"] = f"cell-{i:02d}"
        c["source"] = c["source"].splitlines(keepends=True)
    (HERE / variant["file"]).write_text(json.dumps(nb, indent=1) + "\n")
    print("wrote", variant["file"])


if __name__ == "__main__":
    for v in VARIANTS:
        build(v)
