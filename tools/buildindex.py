import re
from typing import Generator

from nltk import ngrams, stem


class BuildIndex:

    def __init__(self, files):
        self.tf: dict = {}
        self.df: dict = {}
        self.filenames: list = files
        self.file_term_index = self._process_files()
        self.term_vocabulary: list = self._distinct_sorted_terms()

    # PREPROCESSING DATA
    def _process_files(self) -> dict:
        """ :return: = {filename: [term1, term2, ...], ...} """
        stemmer = stem.SnowballStemmer('english')
        stopwords = open('tools/stopwords.txt').read()
        file_to_terms = {}
        for file in self.filenames:
            pattern = re.compile(r'[\W_]+')
            file_to_terms[file] = open(f"corpus/{file}", 'r', encoding='utf-8').read().lower()
            file_to_terms[file] = pattern.sub(' ', file_to_terms[file])
            re.sub(r'[\W_]+', '', file_to_terms[file])
            file_to_terms[file] = file_to_terms[file].split()
            file_to_terms[file] = [_ for _ in file_to_terms[file] if _ not in stopwords]
            file_to_terms[file] = [stemmer.stem(_) for _ in file_to_terms[file]]
        return file_to_terms

    def _distinct_sorted_terms(self) -> list:
        """ :return: = ['aterm', 'bterm', 'cterm', ...] """
        return sorted(set([_ for __ in self.file_term_index.values() for _ in __]))

    # BUILDING INDEXES
    def _term_incidence_matrix(self) -> Generator[tuple, list, None]:
        """ :return: Generator - ('term', [0, 0, 1, 0, 0, 1, 0, 0, 1, 0]) """
        f = self.file_term_index
        for term in self.term_vocabulary:
            yield term, [1 if term in f[_] else 0 for _ in f]

    def index_one_file(self, term_list: dict) -> dict:
        """ :param: = [term1, term2, ...]
            :return: = {term1: [pos1, pos2], term2: [pos2, pos8, ...], ...} """
        file_index = {}
        for pos_index, term in enumerate(term_list):
            if term in file_index.keys():
                file_index[term].append(pos_index)
            else:
                file_index[term] = [pos_index]
        return file_index

    def _coord_index(self, file_term_index: dict) -> Generator[tuple, dict, None]:
        """ :param: = {filename: [term1, term2, ...], ...}
            :return: = {filename: {term: [pos1, pos2, ...]}, ...} """
        for filename in self.filenames:
            yield filename, self.index_one_file(file_term_index[filename])

    def _inverted_coord_index(self, file_index: dict) -> dict:
        """ :param: = {filename: {term: [pos1, pos2, ...], ... }}
            :return: = {term: {filename: [pos1, pos2]}, ...}, ...} """
        inverted_index = {}
        for filename in file_index.keys():
            self.tf[filename] = {}
            for term in file_index[filename].keys():
                self.tf[filename][term] = len(file_index[filename][term])
                if term in self.df.keys():
                    self.df[term] += 1
                else:
                    self.df[term] = 1
                if term in inverted_index.keys():
                    if filename in inverted_index[term].keys():
                        inverted_index[term][filename].append(file_index[filename][term][:])
                    else:
                        inverted_index[term][filename] = file_index[filename][term]
                else:
                    inverted_index[term] = {filename: file_index[filename][term]}
        return inverted_index

    def _permutation_index(self) -> Generator[tuple, list, None]:
        """ :return: Generator - ('hero', ['hero$', 'ero$h', 'ro$he', 'o$her', '$hero']) """
        for term in list(self.term_vocabulary):
            jok_term = term + '$'
            yield term, [jok_term[_:] + jok_term[:_] for _ in range(len(jok_term))]

    def _terms_trigram_index(self) -> Generator[tuple, list, None]:
        """ :return: Generator - ('hero', [('h', 'e', 'r'), ('e', 'r', 'o')]) """
        for term in self.term_vocabulary:
            yield term, list(ngrams(term, 3))

    def incidence_matrix(self) -> dict:
        """ :return: {term_file_incidence_matrix}"""
        return {key: value for key, value in self._term_incidence_matrix()}

    def files_coord_index(self, n_gram_count: int = 1) -> tuple:
        """ :return: (files_coord_index: dict, inverted_files_coord_index: dict)"""
        file_term_index = self.file_term_index

        if n_gram_count > 1:
            for file in file_term_index.keys():
                file_term_index[file] = list(map(' '.join, ngrams(file_term_index[file], n_gram_count)))

        files_index = {key: value for key, value in self._coord_index(file_term_index=file_term_index)}
        inverted_index = self._inverted_coord_index(files_index)
        return files_index, inverted_index

    def terms_index(self) -> tuple:
        """ :return: (term_permutation_index: dict, term_trigram_index: dict)"""
        permutation = {key: value for key, value in self._permutation_index()}
        trigram = {key: value for key, value in self._terms_trigram_index()}
        return permutation, trigram


if __name__ == '__main__':
    filenames = [
        'corpus/The-Romance-of-a-Sho-Amy-Levy.txt',
        'corpus/An-English-Grammar-J-W-Sewell.txt',
        'corpus/Cunningham-s-manual-D-J-Daniel-J.txt',
        'corpus/Famous-Composers-and-Various.txt',
        'corpus/On-Sunset-Highways-Thomas-D-Murph.txt',
        'corpus/Passages-from-the-Li-Charles-Babbage.txt',
        'corpus/Secret-Adversary-Agatha-Christie.txt',
        'corpus/Sir-Edwin-Landseer-Frederick-G-St.txt',
        'corpus/Telescopic-Work-for-William-F-Denn.txt',
        'corpus/The-Letters-of-a-Por-Marianna-Alcofo.txt'
    ]
    index = BuildIndex(filenames)
