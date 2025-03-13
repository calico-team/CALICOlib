# CALICOlib
CALICOlib is a framework to help facilitate problem creation on DOMjudge. Currently, the library helps with test generation and creating problem zip, which is based on the ICPC problem package specification

## Installing
```
python -m pip install calico_lib
```
Alternatively, install the development version using flit.
```
brew install flit # or another package manager like pip or pipx
git clone https://github.com/calico-team/CALICOlib.git
cd CALICOlib
flit install --symlink
```

## Quick Start
See examples/add. Also see https://github.com/calico-team/CALICOlib/blob/main/examples/add/main.py

## Development
Bump version number in `__init__.py` and run `flit publish` or another build tool. See [documentation for flit](https://flit.pypa.io/en/stable/).

## Roadmap
Problem / Test Generation / Test Verification:
- [ ] Support test case from file
- [ ] Rethink API (Subproblem should be Problem and Problem should be MultipartProblem)

Other stuff:
- [ ] Upload problem to testing contest
- [ ] Create contest
- [ ] Create contest.zip

## Similar tools
https://github.com/RagnarGrootKoerkamp/BAPCtools
