# `neha/`: process artifacts (nothing here is needed to run the project)

The project lives in the parent folder (`../Project4_Merged.ipynb`, `../data/`, `../output/`). This folder keeps the two versions the merge was built from. See `../MERGE.md` for exactly what came from where.

| Path | What it is | How to run it |
|---|---|---|
| `Project4_Neha.ipynb` | Our independent version (written without copying the classmate's code). Reads `../data/`; writes its tables and figures to `neha/output/`. | From this folder, with the project environment: `python -m jupyter nbconvert --to notebook --execute --inplace Project4_Neha.ipynb` |
| `output/` | The tables and figures that version produced (cited by `MERGE.md` for the version-to-version comparison). | – |
| `classmate_original/` | The classmate's notebook and README, byte-identical to the originals. The notebook expects a `data/` folder next to it, so it does not run in place. | Copy `Project4_Credit_Spread_Liquidity.ipynb` into the project root (it only needs the 5 files it always used, which are in `../data/`) and run it there. |
