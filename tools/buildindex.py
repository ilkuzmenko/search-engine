import re
import itertools
import pandas as pd


class BuildIndex:

    def __init__(self, files):
        self.tf = {}
        self.df = {}
        self.filenames = files
        self.file_terms = self.process_files()
        self.terms_collection = self.terms_collecting()
        self.incidence_matrix = self.term_file_list()  # incidence_matrix
        self.file_terms_indices = self.make_indices()
        self.inverted_index = self.files_posting_list()  # inverted_index

    def process_files(self) -> dict:
        """ :param: = [file1, file2, ...]
            :return: = {filename: [term1, term2]} """
        file_to_terms = {}
        for file in self.filenames:
            stopwords = open('tools/stopwords.txt').read()
            pattern = re.compile(r'[\W_]+')
            file_to_terms[file] = open(file, 'r', encoding='utf-8').read().lower()
            file_to_terms[file] = pattern.sub(' ', file_to_terms[file])
            re.sub(r'[\W_]+', '', file_to_terms[file])
            file_to_terms[file] = file_to_terms[file].split()
            file_to_terms[file] = [w for w in file_to_terms[file] if w not in stopwords]
            # file_to_terms[file] = [stemmer.stem_word(w) for w in file_to_terms[file]]
        return file_to_terms

    def terms_collecting(self) -> list:
        """ :return: list of distinct sorted terms """
        return sorted(set(list(itertools.chain.from_iterable(self.file_terms.values()))))

    def term_file_list(self) -> pd.DataFrame:
        """ :return: DataFrame with incidence matrix """
        incidence_matrix = pd.DataFrame(self.terms_collection, columns={'terms_collection'})
        for file in self.filenames:
            incidence_matrix[file] = incidence_matrix['terms_collection'].isin(self.file_terms[file])
        # Count values by file
        # print(incidence_matrix)
        # print(incidence_matrix.drop(['terms_collection'], axis=1).apply(pd.Series.value_counts))
        return incidence_matrix

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

    def make_indices(self) -> dict:
        """ :param: = {filename: [term1, term2, ...], ...}
            :return: = {filename: {term: [pos1, pos2, ...]}, ...} """
        file_terms_indices = {}
        for filename in self.file_terms.keys():
            file_terms_indices[filename] = self.index_one_file(self.file_terms[filename])
        return file_terms_indices

    def files_posting_list(self) -> dict:
        """ :param: = {filename: {term: [pos1, pos2, ...], ... }}
            :return: = {term: {filename: [pos1, pos2]}, ...}, ...} """
        inverted_index = {}
        file_terms_indices = self.file_terms_indices
        for filename in file_terms_indices.keys():
            self.tf[filename] = {}
            for term in file_terms_indices[filename].keys():
                self.tf[filename][term] = len(file_terms_indices[filename][term])
                if term in self.df.keys():
                    self.df[term] += 1
                else:
                    self.df[term] = 1
                if term in inverted_index.keys():
                    if filename in inverted_index[term].keys():
                        inverted_index[term][filename].append(file_terms_indices[filename][term][:])
                    else:
                        inverted_index[term][filename] = file_terms_indices[filename][term]
                else:
                    inverted_index[term] = {filename: file_terms_indices[filename][term]}
        return inverted_index
