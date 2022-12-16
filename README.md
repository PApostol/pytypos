## Pytypos

[![PyPI version](https://badge.fury.io/py/pytypos.svg)](https://badge.fury.io/py/pytypos)
[![Downloads](https://static.pepy.tech/personalized-badge/pytypos?period=month&units=international_system&left_color=grey&right_color=yellowgreen&left_text=total%20downloads)](https://pepy.tech/project/pytypos)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pytypos)](https://pypi.org/project/pytypos/)
[![](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Code style: blue](https://img.shields.io/badge/code%20style-blue-blue.svg)](https://blue.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license "Go to license section")
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/PApostol/spark-submit/issues)

### Description
Pytypos is a typo and spelling checker used to identify spelling mistakes in comments of a various programming languages,
such as Python, Java, C++, C#, Matlab, and others. In addition, it can check other text-oriented files such as MD, RST, TXT, or similar.

Spell checking uses dictionaries installed on the host computer.
The dictionary language can be defined in the `Pytypos` object with `dictionary='de'` for German, for instance.
For installation and management of dictionaries, see the documentation of [pyenchant](https://pyenchant.github.io/pyenchant/).
To list available dictionary languages on the host system, print `pytypos.available_languages()`.

### Installation
The easiest way to install is using `pip`:

`pip install pytypos`

To install from source:
```
git clone https://github.com/PApostol/pytypos.git
cd pytypos
python setup.py install
```

For usage details check `help(pytypos)`.

### Usage Examples
The below will recursively scan `my/path/project/` for comments (i.e. `# this is a comment`) in Python files:
```
from pytypos import Pytypos
prj = Pytypos(target='my/path/project/', match_identifier='#', file_extension='py', recursive=True)
prj.find_typos()
print(prj.typo_list)
print(prj.typo_details)
```
`Pytypos.typo_list` stores a list of all possible typos found.

`Pytypos.typo_details` stores a dictionary with the following structure:

If `suggestions = False` (default):
```
{'file1': ['typo1', 'typo2'],
 'file2': ['typo1', 'typo2']
}
```

If `suggestions = True`:
```
{'file1': [{'typo1': ['suggestion1a', 'suggestion1b'],
            'typo2': ['suggestion2a', 'suggestion2b']
           },
 'file2': [{'typo1': ['suggestion1a', 'suggestion1b'],
            'typo2': ['suggestion2a', 'suggestion2b']
           }
}
```
The above can be nicely printed on stdout with Python's built-in [pprint](https://docs.python.org/3/library/pprint.html).

#### Other Examples
```
# recursively scan "foo/bar/" for any text in RST files and give suggestions, but skip file "foo/UPDATE.rst" and exclude the words "repos" and "GitHub"
Pytypos(target='foo/bar/', match_identifier='', file_extension='rst', recursive=True, suggestions=True, exclude_file_list=['foo/UPDATE.rst'], exclude_word_list=['repos', 'GitHub'])

# scan the "a/b/c.java" Java file for comments (i.e. "// this is a comment") and give suggestions with a french dictionary, but exclude words found in "exclusions.txt"
Pytypos(target='a/b/c.java', match_identifier='//', dictionary='fr', suggestions=True, exclude_word_file='exclusions.txt')
```

#### Testing

You can do some simple testing after cloning the repo.

Note any additional requirements for running the tests: `pip install -r tests/requirements.txt`

`python tests/run_integration_test.py`

#### Additional methods

`Pytypos.fix_typos()`: Fixes typos found in-between spaces with the most likely replacement

`Pytypos.add_to_dictionary()`: Adds custom word list to dictionary

`Pytypos.add_to_exclusions()`: Removes custom word list from dictionary

`Pytypos.replace_word()`: Replaces words in dictionary

### License

Released under [MIT](/LICENSE) by [@PApostol](https://github.com/PApostol)

- You can freely modify and reuse.
- The original license must be included with copies of this software.
- Please link back to this repo if you use a significant portion the source code.
