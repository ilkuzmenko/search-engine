import re
from typing import Generator

from nltk import ngrams, stem


class BuildIndex:

    def __init__(self, files):
        self.tf: dict = {}
        self.df: dict = {}
        self.filenames: list = files

        self.file_terms: dict = self._process_files()
        self.vocabulary: list = self._distinct_sorted_terms()

        self.incidence_matrix: Generator[tuple, None, None] = self._term_file_incidence_matrix()

        self.file_posting_list: Generator[tuple, dict, None] = self._coord_index()
        self.term_posting_list: dict = self._inverted_coord_index()

        self.term_permutation_index: Generator[tuple, None, None] = self._permutation_index()
        self.term_trigram_index: Generator[tuple, None, None] = self._terms_trigram_index()

    def _process_files(self) -> dict:
        """ :return: = {filename: [term1, term2]} """
        stemmer = stem.SnowballStemmer('english')
        stopwords = open('tools/stopwords.txt').read()
        file_to_terms = {}
        for file in self.filenames:
            pattern = re.compile(r'[\W_]+')
            file_to_terms[file] = open(file, 'r', encoding='utf-8').read().lower()
            file_to_terms[file] = pattern.sub(' ', file_to_terms[file])
            re.sub(r'[\W_]+', '', file_to_terms[file])
            file_to_terms[file] = file_to_terms[file].split()
            file_to_terms[file] = [_ for _ in file_to_terms[file] if _ not in stopwords]
            file_to_terms[file] = [stemmer.stem(_) for _ in file_to_terms[file]]
        return file_to_terms

    def _distinct_sorted_terms(self) -> list:
        """ :return: = ['aterm', 'bterm', 'cterm'] """
        return sorted(set([_ for __ in self.file_terms.values() for _ in __]))

    def _term_file_incidence_matrix(self) -> Generator[tuple, list, None]:
        """ :return: ('term', [0, 0, 1, 0, 0, 1, 0, 0, 1, 0]) """
        for term in self.vocabulary:
            yield term, [1 if term in self.file_terms[_] else 0 for _ in self.file_terms]

    def index_one_file(self, term_list: dict) -> dict:
        """ :param: = [term1, term2, ...]
            :return: = {term1: [pos1, pos2], term2: [pos2, pos8], ...} """
        file_index = {}
        for index, term in enumerate(term_list):
            if term in file_index.keys():
                file_index[term].append(index)
            else:
                file_index[term] = [index]
        return file_index

    def _coord_index(self) -> Generator[tuple, dict, None]:
        """ :param: = {filename: [term1, term2, ...], ...}
            :return: = {filename: {term: [pos1, pos2, ...]}, ...} """
        for filename in self.filenames:
            yield filename, self.index_one_file(self.file_terms[filename])

    def _inverted_coord_index(self) -> dict:
        """ :param: = {filename: {term: [pos1, pos2, ...], ... }}
            :return: = {term: {filename: [pos1, pos2]}, ...}, ...} """
        inverted_index = {}
        file_posting_list = {key: value for key, value in self._coord_index()}
        for filename in file_posting_list.keys():
            self.tf[filename] = {}
            for term in file_posting_list[filename].keys():
                self.tf[filename][term] = len(file_posting_list[filename][term])
                if term in self.df.keys():
                    self.df[term] += 1
                else:
                    self.df[term] = 1
                if term in inverted_index.keys():
                    if filename in inverted_index[term].keys():
                        inverted_index[term][filename].append(file_posting_list[filename][term][:])
                    else:
                        inverted_index[term][filename] = file_posting_list[filename][term]
                else:
                    inverted_index[term] = {filename: file_posting_list[filename][term]}
        return inverted_index

    def _permutation_index(self) -> Generator[tuple, list, None]:
        """ :return: permutation index for terms """
        for term in list(self.vocabulary):
            jok_term = term + '$'
            yield term, [jok_term[_:] + jok_term[:_] for _ in range(len(jok_term))]

    def _terms_trigram_index(self) -> Generator[tuple, list, None]:
        """ :return: trigrams for terms """
        for term in self.vocabulary:
            yield term, list(ngrams(term, 3))


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
