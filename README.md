# CALICOlib
CALICOlib is a framework to help facilitate problem creation on DOMjudge. Currently, the library helps with test generation and creating problem zip, which is based on the ICPC problem package specification

## Installing
```
python -m pip install calico_lib
# or use uv
uv pip install calico_lib
```
Alternatively, install the development version using flit.
```
brew install flit # or another package manager like pip or pipx
git clone https://github.com/calico-team/CALICOlib.git
cd CALICOlib

PIP_BREAK_SYSTEM_PACKAGES=1 flit install --symlink
# or use uv
uv pip install -e .
# to install to another project's venv
uv pip install -e . --python /path/to/other-project/.venv
```

## Quick Start
See examples/add. Also see https://github.com/calico-team/CALICOlib/blob/main/examples/add/main.py

## Development
Bump version number in `__init__.py` and run `flit publish` or another build tool. See [documentation for flit](https://flit.pypa.io/en/stable/).

## Roadmap
- [ ] Support test case from file
- [X] Upload problem to testing contest
- [X] Create contest
- [X] Create contest.zip
- [ ] Tests
- [ ] Docs
- [ ] Remove legacy
- [ ] Default validation (trailing white space / empty lines... etc)
- [ ] Backward compatible

## Similar tools
https://github.com/RagnarGrootKoerkamp/BAPCtools
