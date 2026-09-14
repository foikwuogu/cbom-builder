# Contributing

Issues and pull requests are welcome, especially:

- **New crosswalk rows** for a protocol not yet covered (see LIMITATIONS.md). A good
  pull request adds a row to `code/01_build_crosswalk.py` with a real
  `source_spec`/`source_url`, re-runs `python code/01_build_crosswalk.py`, and adds a
  test in `tests/test_crosswalk.py` if the row introduces a new pattern.
- **New parsers** under `src/cbom_builder/parsers/` (see NEXT_STEPS.md for planned
  ones). A parser's only job is to produce an inventory-row dict; it should not know
  anything about the crosswalk itself.
- Corrections to an existing row's characterization — please cite the specification
  section you're correcting against.

## Running the tests

```
pip install -e ".[test]"
python -m unittest discover -s tests -v
```

## Before submitting

- `python code/01_build_crosswalk.py` (if you touched the crosswalk) and
  `python code/02_build_web.py` (if you touched `web/index_template.html` or the
  crosswalk) so the generated files stay in sync — never hand-edit
  `src/cbom_builder/data/pqc_crosswalk.json`, `data/processed/pqc_crosswalk.*`, or
  `web/index.html` directly.
- The test suite passes.
- New/changed facts cite a public, dated source.
