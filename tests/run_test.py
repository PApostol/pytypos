"""Simple pytypos test"""
import pprint

from pytypos import Pytypos

typos_py = Pytypos(target='tests/resources/pyfile.py', suggestions=True)
typos_py.find_typos()
#typos_py.fix_typos()

typos_rst = Pytypos(target='tests/resources/', recursive=True, match_identifier='',
                    file_extension='rst', exclude_word_list=['RST'])
typos_rst.find_typos()
#typos_rst.fix_typos()

pp = pprint.PrettyPrinter()
pp.pprint(typos_py.typo_details)
pp.pprint(typos_rst.typo_details)

"""
Output:
{'resources/pyfile.py': [{'commetn': ['comment', 'comet']},
                         {'anothr': ['another', 'anthrop']}]}

{'tests/resources/foo.rst': ['cdoe', 'proply']}
"""
