"""Pytypos class functionality"""
import codecs
import glob
import logging
import os
import re
from itertools import chain
from typing import Any, Dict, List, Optional

import enchant

from .exceptions import SuggestionsNotFound


class Pytypos:
    """Pytypos class can be used to identify possible pytypos in source code comments and other text files

    Parameters
        target (str): file or directory to scan for pytypos
        match_identifier (str): identifier to look for (leave blank to scan the entire file, default: '#')
        file_extension (str): file extension to look for in case `target` is a directory (default: 'py')
        recursive (bool): whether to scan recursively in case `target` is a directory (default: False)
        dictionary (str): language dictionary to use (default: 'en_US')
        suggestions (bool): whether to generate suggestions for any pytypos detected (default: False)
        exclude_file_list (List[str]): a list of files to exclude from typo checking (default: None)
        exclude_word_list (List[str]): a list of words to exclude from typo checking (default: None)
        exclude_word_file (str): path to a text file with words to exclude from typo checking, one word per line (default: None)

    Returns:
        Typos: a Pytypos object

    Examples:
        Recursively scan "my/path/project/" for comments (i.e. "# this is a comment") in Python files
        `Pytypos(target='my/path/project/', match_identifier='#', file_extension='py', recursive=True)`

        Recursively scan "foo/bar/" for any text in RST files and give suggestions, but skip file "foo/UPDATE.rst" and exclude the words "repos" and "GitHub"
        `Pytypos(target='foo/bar/', match_identifier='', file_extension='rst', recursive=True, suggestions=True, exclude_file_list=['foo/UPDATE.rst'], exclude_word_list=['repos', 'GitHub'])`

        Scan the "a/b/c.java" Java file for comments (i.e. "// this is a comment") and give suggestions with a french dictionary, but exclude words found in "exclusions.txt"
        `Pytypos(target='a/b/c.java', match_identifier='//', dictionary='fr', suggestions=True, exclude_word_file='exclusions.txt')`

        Note: you can only use dictionaries that you have installed. Pytypos uses dictionaries from PyEnchant: https://pyenchant.github.io/pyenchant/
    """

    def __init__(self, target: str,
                 match_identifier: str = '#',
                 file_extension: str = 'py',
                 recursive: bool = False,
                 dictionary: str = 'en_US',
                 suggestions: bool = False,
                 exclude_file_list: Optional[List[str]] = None,
                 exclude_word_list: Optional[List[str]] = None,
                 exclude_word_file: Optional[str] = None
                 ) -> None:

        self.target = target.replace(os.path.sep, '/')
        self.file_extension = file_extension
        self.re_match = f'{match_identifier}(.+)\n'
        self.recursive = recursive
        self.dictionary = enchant.Dict(dictionary)
        self.suggestions = suggestions
        self.exclude_files = set(f.replace(os.path.sep, '/') for f in exclude_file_list) if isinstance(exclude_file_list, List) else set()
        self.exclude_words = set(exclude_word_list) if isinstance(exclude_word_list, List) else set()

        if exclude_word_file and os.path.isfile(exclude_word_file):
            with codecs.open(exclude_word_file, 'r', encoding='utf-8') as f:
                words = f.read().splitlines()
            if words:
                self.exclude_words |= set(w.strip() for w in words if w)
        elif exclude_word_file:
            raise FileNotFoundError(f'No such file or directory: {exclude_word_file}')

        self.typo_list: List[str] = []
        self.typo_details: Dict[str, Any] = {}


    def add_to_dictionary(self, word_list: List[str], persistent: bool = True) -> None:
        """Adds custom word list to dictionary

        Parameters
            word_list (List[str]): list of words to add to dictionary
            persistent (bool): whether the word list addition should be persistent or temporary for current session (default: True)

        Returns:
            None
        """
        if persistent:
            for word in word_list:
                self.dictionary.add(word)
        else:
            for word in word_list:
                self.dictionary.add_to_session(word)
        logging.info('Word list added to %s.', 'persistent dictionary' if persistent else 'current session')


    def add_to_exclusions(self, word_list: List[str]) -> None:
        """Removes custom word list from dictionary

        Parameters
            word_list (List[str]): list of words to remove from dictionary

        Returns:
            None
        """
        for word in word_list:
            self.dictionary.remove(word)
        logging.info('Word list added to exclusions.')


    def replace_word(self, word_mappings: Dict[str, str]) -> None:
        """Replaces words in dictionary

        Parameters
            word_mappings (Dict[str, str]): dictionary with keys as words to replace and values as words to replace the keys with

        Returns:
            None
        """
        for old_word, new_word in word_mappings.items():
            self.dictionary.store_replacement(old_word, new_word)
        logging.info('Word mappings replaced.')


    def _match_from_file(self, file: str) -> List[str]:
        with codecs.open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = re.findall(self.re_match, content)
        strip_chars = {'.', ',', ';', '?', '(', ')', '&', '"', "'", '{', '}', '@', '[', ']', '#'}
        strip_str = ''.join(list(strip_chars))
        return list(set(word.strip(strip_str) for match in matches for word in match.split() if word.strip(strip_str).isalpha()))


    def _find_files(self) -> List[str]:
        if os.path.isfile(self.target):
            files = [self.target]
        elif os.path.isdir(self.target):
            file_pattern = self.target + ('/**/*.' if self.recursive else '/*.') + self.file_extension
            files = [f.replace(os.path.sep, '/') for f in glob.glob(file_pattern, recursive=self.recursive)]
        else:
            raise FileNotFoundError(f'No such file or directory: {self.target}')
        return files


    def _get_typos_list(self) -> List[str]:
        if self.typo_details:
            if self.suggestions:
                typo_list = [list(word_dict.keys()) for word_list in self.typo_details.values() for word_dict in word_list]
            else:
                typo_list = list(self.typo_details.values())

            typo_list_flat = list(chain.from_iterable(typo_list))
            return sorted(list(set(typo_list_flat)), key=str.casefold)
        return []


    def find_typos(self) -> None:
        """Finds typos in target file or directory

        Returns:
            None
        """
        typo_details: Dict[str, Any] = {}
        for file in self._find_files():
            if file not in self.exclude_files:
                for word in self._match_from_file(file):
                    if word and word not in self.exclude_words and not self.dictionary.check(word):
                        if file in typo_details:
                            typo_details[file].append({word: self.dictionary.suggest(word)} if self.suggestions else word)
                        else:
                            typo_details[file] = [{word: self.dictionary.suggest(word)} if self.suggestions else word]
        if typo_details:
            self.typo_details = typo_details
            self.typo_list = self._get_typos_list()
            logging.info('Possible typos found.')
        else:
            logging.info('No typos were found.')


    def fix_typos(self) -> None:
        """Fixes typos found in-between spaces with the most likely replacement.

        Returns:
            None
        """
        if not self.suggestions:
            raise SuggestionsNotFound('No suggestions exist, please re-check for typos with `suggestions=True`.')

        if not self.typo_details:
            logging.info('No typos to fix.')
        else:
            for file, typo_list in self.typo_details.items():
                with codecs.open(file, 'r+', encoding='utf-8') as f:
                    content = f.read()
                    f.seek(0)
                    for entry in typo_list:
                        for typo, suggestions in entry.items():
                            content = content.replace(f' {typo} ', f' {suggestions[0]} ')
                    f.write(content)
                    f.truncate()
            logging.info('Typos fixed with the most likely replacement.')
