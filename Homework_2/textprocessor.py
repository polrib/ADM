# Importing all necessary libraries
from collections import Counter
from os.path import isdir
import pandas as pd
from os import listdir
from os.path import isfile
from nltk import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import pickle
import inflect


# This class aims to process text and corpus of documents.
class TextProcessor():

    def __init__(self, dir_path="./descriptions/"):
        # this is the path where all the text files are contained
        self.dir_path = dir_path
        # this dictionary will contain the integer encoding for each word(String)
        self.term_enc = {}
        # this is the size of the corpus vocabulary
        self.VOCABULARY_SIZE = 1
        # this dictionary contains the term frequency of each word
        self.tf = {}
        # this is the number of docs into the corpus
        self.NUMBER_OF_DOCS = 10000

        # Lazy initialization of nltk objects for preprocessing
        self.tokenizer = None
        self.stopwords = None
        self.stemmer = None
        self.number_to_words = None

    def _nltkProcess(self, string):

        # Transform all words to lowercase
        string = string.lower()
        # Setup nltk objects to perform preprocessing
        self._setupNltk(language='italian')
        # Tokenize the string removing puntuactions
        tokens = self.tokenizer.tokenize(string)
        # Create new sentence
        new_sentence = []
        # Scroll through each word and stemming it
        for word in tokens:
            word = self.stemmer.stem(word)
            # exclude the word if it is a stopword
            if not word in self.stopwords:
                # if the word has length greater than one, it has sufficient information
                # value to be added
                if len(word) > 1:
                    new_sentence.append(word)
                # if the word length is equal to one and it is numeric
                # then the string representation of the number is added
                elif word.isnumeric():
                    new_sentence.append(self.number_to_words.number_to_words(word))
        # Since the object must later be saved on a .tsv file,
        # it is needed to return a string rather than a list of words
        return new_sentence

    def _setupNltk(self, language):
        # Lazy initialization of objects needed to preprocess strings
        if self.tokenizer == None:
            self.tokenizer = RegexpTokenizer(r'\w+')
        if self.stopwords == None:
            self.stopwords = set(stopwords.words(language))
        if self.stemmer == None:
            self.stemmer = SnowballStemmer(language)
        if self.number_to_words == None:
            self.number_to_words = inflect.engine()

    def buildEncoding(self, fileName):

        # If the file already exists then we load it, instead to compute it another time.
        if isfile(fileName):
            with open(fileName, 'rb') as handle:
                self.term_enc = pickle.load(handle)
                self.VOCABULARY_SIZE = len(list(self.term_enc.keys()))
            return

        # Iterate over each text file containing the description
        for filePath in listdir(self.dir_path):
            # open the file and read the description
            with open(self.dir_path + filePath, 'r') as fileDescription:
                description = fileDescription.read()

            # get the list of words after having processed the description text
            processedDescription = self._nltkProcess(description)
            # for each word contained in the title and description fields
            for word in processedDescription:
                # if the word is not encoded yet
                if word not in self.term_enc.keys():
                    # store the encoding into the @term_enc dictionary
                    self.term_enc[word] = self.VOCABULARY_SIZE
                    # update the vocabulary size variable
                    self.VOCABULARY_SIZE += 1

        # In the end, the dictionary is saved on the filesystem to be loaded further.
        with open(fileName, 'wb') as handle:
            pickle.dump(self.term_enc, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def buildTf(self, fileName):
        # if the file @fileName already exists on the filesystem, then the tf dictionary
        # is imported instead to be newly computed
        if isfile(fileName):
            with open(fileName, 'rb') as handle:
                self.tf = pickle.load(handle)
                return

        for filePath in listdir(self.dir_path):
            # open the file and read the description
            with open(self.dir_path + filePath, 'r') as fileDescription:
                description = fileDescription.read()
            # get the list of words after having processed the description text
            processedDescription = self._nltkProcess(description)
            # dictionary that maps each word to the frequency in the given document
            counts = Counter(processedDescription)
            # retrieve the doc index
            doc_index = int(filePath[:-4][filePath.index('#') + 1:])
            # for each word in the description
            for word in counts:
                # if the word is in the tf dictionary then the tuple (doc_id,tf(word,doc_id)) is appended
                if word in self.tf:
                    self.tf[word].append((doc_index, counts[word]))
                    # otherwise a new list is created with as element the tuple (doc_id,tf(word,doc_id))
                else:
                    self.tf[word] = [(doc_index, counts[word])]

        # In the end, the dictionary is saved on the filesystem to be loaded further.
        with open(fileName, 'wb') as handle:
            pickle.dump(self.tf, handle, protocol=pickle.HIGHEST_PROTOCOL)