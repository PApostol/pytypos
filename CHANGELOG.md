### Pytypos

#### 1.4.0 (under development)
- TBD

##### 1.3.0 (2022-12-03)
Features
- `pytypos.Pytypos` now takes keyword arguments only

Misc/Internal
- Refactor to `blue` coding style

##### 1.2.1 (2022-01-15)
Misc/Internal
- Refactor to comply with `pylint`, `isort` and `mypy` checks
- Minor improvements

##### 1.2.0 (2021-12-09)
Features
- Obtain available dictionary languages with `pytypos.available_languages`

Improvements
- Use consistent path separators where possible
- Use more generic typing

##### 1.1.0 (2021-11-13)
Features
- `Pytypos` object now takes `exclude_file_list`, `exclude_word_list` and `exclude_word_file` arguments

Improvements
- Don't return typo `dict` with `pytypos.Pytypos.find_typos`

##### 1.0.0 (2021-10-29)
- First release
