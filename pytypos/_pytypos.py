import codecs
import enchant
import glob
import logging
import re
import os
from itertools import chain

class Pytypos:
    """Pytypos class can be used to identify possible pytypos in source code comments and other text files

    Parameters
        target (str): file or directory to scan for pytypos
        match_identifier (str): identifier to look for (leave blank to scan the entire file, default: '#')
        file_extension (str): file extension to look for in case `target` is a directory (default: 'py')
        recursive (bool): whether to scan recursively in case `target` is a directory (default: False)
        dictionary (str): language dictionary to use (default: 'en_US')
        suggestions (bool): whether to generate suggestions for any pytypos detected (default: False)

    Returns:
        Typos: a Pytypos object

    Examples:
        Recursively scan `target` for comments (i.e. "# this is a comment") in Python files
        `Pytypos(target='/my/path/project/', match_identifier='#', file_extension='py', recursive=True)`

        Recursively scan `target` for any text in RST files and give suggestions
        `Pytypos(target='/foo/bar/', match_identifier='', file_extension='rst', recursive=True, suggestions=True)`

        Scan the `target` Java file for comments (i.e. "// this is a comment") and give suggestions with a french dictionary
        `Pytypos(target='/a/b/c.java', match_identifier='//', dictionary='fr', suggestions=True)`

        Note: you can only use dictionaries that you have installed. Pytypos uses dictionaries from PyEnchant: https://pyenchant.github.io/pyenchant/
    """
    def __init__(self, target: str, match_identifier: str='#', file_extension: str='py', recursive: bool=False, dictionary: str='en_US', suggestions=False) -> None:
        self.target = target
        self.file_extension = file_extension
        self.re_match = f'{match_identifier}(.+)\n'
        self.recursive = recursive
        self.dictionary = enchant.Dict(dictionary)
        self.suggestions = suggestions
        self.typo_list = None
        self.typo_details = None


    def add_to_dictionary(self, word_list: list, persistent: bool=True) -> None:
        """Adds custom word list to dictionary

        Parameters
            word_list (list): list of word strings to add to dictionary
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
        logging.info('Word list added to {0}.'.format('persistent dictionary' if persistent else 'current session'))


    def add_to_exclusions(self, word_list: list) -> None:
        """Removes custom word list from dictionary

        Parameters
            word_list (list): list of word strings to remove from dictionary

        Returns:
            None
        """
        for word in word_list:
            self.dictionary.remove(word)
        logging.info('Word list added to exclusions.')


    def replace_word(self, word_mappings: dict) -> None:
        """Replaces words in dictionary

        Parameters
            word_mappings (dict): dictionary with keys as words to replace and values as words to replace the keys with

        Returns:
            None
        """
        for old_word, new_word in word_mappings.items():
            self.dictionary.store_replacement(old_word, new_word)
        logging.info('Word mappings replaced.')


    def _match_from_file(self, file: str) -> list:
        with codecs.open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = re.findall(self.re_match, content)
        strip_chars = {'.', ',', ';', '?', '(', ')', '&', '"', "'", '{', '}', '@', '[', ']', '#'}
        strip_str = ''.join([c for c in strip_chars])
        return list(set([word.strip(strip_str) for match in matches for word in match.split() if word.strip(strip_str).isalpha()]))


    def _find_files(self) -> list:
        if os.path.isfile(self.target):
            files = [self.target]
        elif os.path.isdir(self.target):
            file_pattern = self.target + ('/**/*.' if self.recursive else '/*.') + self.file_extension
            files = [file for file in glob.glob(file_pattern, recursive=self.recursive)]
        else:
            raise FileNotFoundError(f'No such file or directory: {self.target}')
        return files


    def _get_typos_list(self) -> list:
        if self.typo_details:
            if self.suggestions:
                typo_list = [list(word_dict.keys()) for word_list in self.typo_details.values() for word_dict in word_list]
            else:
                typo_list = list(self.typo_details.values())

            typo_list_flat = list(chain.from_iterable(typo_list))
            return sorted(list(set(typo_list_flat)), key=str.casefold)


    def find_typos(self) -> dict:
        """Finds typos in target file or directory

        Returns:
            typo_details (dict): details of typos found (returns None if no typos found)
        """
        typo_details = {}
        for file in self._find_files():
            for word in self._match_from_file(file):
                if word and not self.dictionary.check(word):
                    if file in typo_details:
                        typo_details[file].append({word: self.dictionary.suggest(word)} if self.suggestions else word)
                    else:
                        typo_details[file] = [{word: self.dictionary.suggest(word)} if self.suggestions else word]
        if typo_details:
            logging.info('Possible typos found.')
            self.typo_details = typo_details
            self.typo_list = self._get_typos_list()
            return self.typo_details
        else:
            logging.info('No typos were found.')


    def fix_typos(self) -> None:
        """Fixes typos found in-between spaces with the most likely replacement.

        Returns:
            None
        """
        if not self.suggestions:
            raise Exception('No suggestions exist, please re-check for typos with `suggestions=True`.')
        elif not self.typo_details:
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
