from bs4 import BeautifulSoup
from tqdm import tqdm
from os import listdir
from math import log
from textprocessor import TextProcessor

import pandas as pd
import json


class HtmlProcessor:

    def __init__(self, directory="./htmls/", MAX_DOCUMENTS=10000):
        # directory where all the .html file are stored
        self.directory = directory
        # this variable is the number of ads needed to perform the analysis
        self.MAX_DOCUMENTS = MAX_DOCUMENTS
        # this variable will contain the text processor object needed to extract info
        # by the descriptions of the house advertisements
        self.tp = None
        # the tfidf dictionary that will contain each tfidf value is initalized
        self.tfidf = {}
        # this variable will contain the euclidean of each document(description) in the corpus(collection of ads)
        self.euclidean_norm = {}
        # this variable contains the tfidf values but normalized such that the tfidf vector
        # of each document has a unit euclidean norm.
        self.tfidf_normalized = {}

    def createFirstDataset(self):
        # variable useful to keep track of the index of each house ad
        ad_index = 0
        # fields contained into the JSON value and that are interest for the purposes of the assignment
        fields = ['locali', 'bagni', 'prezzo', 'superficie']
        # lists that will contain the values of each column of the dataframe
        price = []
        locali = []
        superficie = []
        bagni = []
        piano = []
        allFeatures = [price, locali, superficie, bagni, piano]
        # this list will contain the index of the dataframe
        indexes = []
        # start a row sample with the fields set to 0
        row_sample = dict.fromkeys(fields, 0)
        # this variable will contains the sample for the 'piano' variable
        piano_sample = None
        # name of the attribute that contains the piano value
        attribute_name_piano = 'title'

        # for each html file
        for filePath in tqdm(listdir(self.directory)):
            if (ad_index >= self.MAX_DOCUMENTS):
                break
            with open(self.directory + filePath, "r") as filereader:
                html = filereader.read()
            # Initialize the BeautifulSoup parser
            soup = BeautifulSoup(html, 'html.parser')
            # find the json document where most of the features are contained
            jsonFile = soup.find(id='js-hydration').text.strip()
            # extract a python dictionary value from the JSON value
            metadata = json.loads(jsonFile)
            # toCheck is an auxiliary variable to control the flow
            # in fact since there are more than one loop, it is not possible
            # to use only the 'continue' statement to manage the flow.
            # the var/flag @toCheck is True, at the beginning, and if something bad happens
            # its state is changed to False and, once the code is back into the main loop,
            # the 'continue' statement is involved
            toCheck = True
            for field in fields:
                # if one of the fields is not present then it is a 'bad' house ad
                # Three checks are performed:
                # 1- if the current @field is not present in the @metadata dictionary
                # then the house ad is not good and so the flag @toCheck is uploaded
                # 2- check if the flag @toCheck is already false and sequently 'break' the loop
                # 3- If the JSON value is None then the features of interest aren't present
                # and the loop must be broken.
                if field not in metadata or not toCheck or metadata[field] is None:
                    toCheck = False
                    break
                # now I am sure that the field is present
                # Three checks are performed:
                # 1- The '+'(plus) char in the string. This is due to the fact that sometimes
                # the exact info about how many 'locali' or 'bagni' isn't present, so the advertiser
                # put at the end of the number a plus sign(so '5+' means 5,6,7,...,N locali)
                # 2- The '-' character is present when the advertiser want to put a range of values
                # for instance an house price could be '180.000-300.000', it means from 180k to 300k
                # 3- The 'da' string means literally 'from' and it means that the advertiser wants to put
                # a lower limit to one of the features.
                # All 3 cases need to be avoided because the assignment requires a unique value
                # for every feature.
                if not ('+' in metadata[field] or '-' in metadata[field] or 'da' in metadata[field]):
                    # split the value
                    tmp = metadata[field].split(' ')
                    # the flag state is put to False
                    toCheck = False
                    for string in tmp:
                        # on the string is invoked a replace of the '€' and '.' character
                        # because of the encoding the advertiser use for the price
                        if (string.replace('.', '').replace('€', '').isdigit()):
                            # if the string is a digit then the flag can be newly be
                            # assigned to True
                            toCheck = True
                            row_sample[field] = int(string.replace('.', '').replace('€', ''))
                else:
                    # if one of the previous condition is encountered then it is not possible
                    # to include the house ad to the collection for the sequent analysis
                    toCheck = False
                    break

            # at this point, the code flow is back into the main loop and if the flag is not True
            # then a 'continue' statement is invoked
            if not toCheck:
                continue
            # now it remains to extract the piano, the description and the link
            # extracting piano field
            piano_abbr = soup.find('abbr', attrs={'class': 'text-bold im-abbr'})
            # if the tag where the 'piano' value can be found it is not present in the html
            # or the tag doesn't have the attribute with the 'piano' value, then the house ad
            # must be discarded
            if (not piano_abbr is None) and attribute_name_piano in piano_abbr.attrs:
                # if the piano is 'terra'(T),'rialzato'(R) or 'seminterrato'(S)
                # the piano field is set to 1.
                if piano_abbr.attrs[attribute_name_piano] in {'T', 'R', 'S', 'Piano terra'}:
                    piano_sample = 1
                elif piano_abbr.attrs[attribute_name_piano].isdigit():
                    piano_sample = int(piano_abbr.attrs[attribute_name_piano])
                else:
                    continue
            else:
                # the ad doesn't contain the piano info therefore it is a 'bad' ad
                continue

            # extracting description
            description_div = soup.find('div', attrs={'class': 'col-xs-12 description-text text-compressed'})
            # if the tag where the description is contained it is not present in the html file
            # then the house ad must be discarded
            if (description_div is None):
                continue
            # extract the link
            link_tag = soup.find('link', attrs={'rel': 'canonical'})
            # if the tag where the link is contained it is not present in the html file
            # then the house ad must be discarded
            if not 'href' in link_tag.attrs:
                continue
            # At this point of the code flow, it is possible to say surely that the house ad
            # can be included in the collection for the sequent analysis.
            #
            # open a file and store the description
            # save the description on a textfile
            with open("./descriptions/descriptionAD#" + str(ad_index) + ".txt", "w") as text_file:
                text_file.write(description_div.text.strip())
            # retrieve the link value in the 'href' attribute of the tag
            adLink = link_tag.attrs['href']
            # upload the value of the ad_index
            ad_index += 1
            # Now it's possible to appreciate the use of additional variables for the fields of interest
            # they are useful because if each variable is appended to the list immediately
            # then anytime an issue involves(every time a "break" or "continue" statement appears)
            # it is needed to pop the element from the list.
            # Instead, with the use of auxiliary variable it is possible to first assign it
            # and then append all of them at the end, when we are sure no issues are present
            # for that specific house ad.
            indexes.append(adLink)
            price.append(row_sample['prezzo'])
            locali.append(row_sample['locali'])
            superficie.append(row_sample['superficie'])
            bagni.append(row_sample['bagni'])
            piano.append(piano_sample)

        # columns of the dataframe
        columnsDf = ["price", "locali", "superficie", "bagni", "piano"]
        # initialize the dataframe to be stored on the filesystem
        toReturn = pd.DataFrame()
        # iterate over each column of the dataframe to be returned
        # and assign the column to the corresponding list of values
        for i in range(len(columnsDf)):
            # assign the list of values to the specific column
            toReturn[columnsDf[i]] = allFeatures[i]
        # upload the indexes
        toReturn.index = indexes
        # save the dataframe on the filesystem
        toReturn.to_csv('dataframe1.tsv', sep='\t')

    def createSecondDataset(self, datasetFileName="df2.tsv"):
        # the text processor object is initialized
        self.tp = TextProcessor()
        # the term encoding is built
        self.tp.buildEncoding("encoding.pickle")
        # the term frequency dictionary is built
        self.tp.buildTf(fileName='tf.pickle')
        # the function which build the tfidf, still not normalized, is invoked
        self._createtfidf()
        # the function which computes the euclidean norm of the description in the house ad collection
        self._computeEuclideanNorm()
        # this function creates the tfidf dictionary but normalized
        self._createNormalizedtfidf()
        # the dataframe is created
        pd.DataFrame.from_dict(data=self.tfidf_normalized, columns=range(1, self.tp.VOCABULARY_SIZE + 1),
                               orient='index').to_csv(datasetFileName, sep='\t')

    def _createNormalizedtfidf(self):
        # now it will be created the dictionary that contains the tfidf values NORMALIZED
        # so each tfidf value will be divided by the euclidean norm of the document into
        # which the word is contained.
        # iterating over the keys of the @tfidf dictionary.REMEMBER: this dict has as keys the
        # doc indexes.
        for doc_index in self.tfidf:
            # at the beginning the tfidf vector will be a vector of zero
            self.tfidf_normalized[doc_index] = [0] * self.tp.VOCABULARY_SIZE
            # the tfidf values for that document are retrieve
            tfidf_list = self.tfidf[doc_index]
            # iterate over each tuple @tfidfTuple(structure: (wordId, tfidf{wordID,doc_index}))
            for tfidfTuple in tfidf_list:
                # this line access the tfidf vector in position @tfidfTuple[0]-1 which is the index
                # of the word related and update the vector with the tfidf value divided by the euclidean
                # norm of the document
                self.tfidf_normalized[doc_index][tfidfTuple[0] - 1] = (tfidfTuple[1] / self.euclidean_norm[doc_index])

    # compute the euclidean norm of each document
    def _computeEuclideanNorm(self):
        # for each doc_index in the tfidf dictionary.
        # REMEMBER: Why are you using as key of the @tfidf dictionary the doc_index?
        # because in this way it will be much easier to build the final matrix
        # containing the tfidf values
        for doc_index in self.tfidf:
            sum_of_squares = 0
            # all the words contained in the document @doc_index is retrieved together with
            # the related tf-idf value(both contained in the @tfidfTuple)
            tfidf_list = self.tfidf[doc_index]
            # iterate over each tuple @tfidfTuple(structure: (wordId, tfidf{wordID,doc_index}))
            for tfidfTuple in tfidf_list:
                # retrieve the tfidf value
                tmp = tfidfTuple[1]
                sum_of_squares += (tmp ** 2)
            # the euclidean norm is equal to the square root of the sum of the squares of
            # each component of the vector
            self.euclidean_norm[doc_index] = sum_of_squares ** 0.5

    def _createtfidf(self):
        # for each word(equal to for each column in the tfidf matrix)
        for word in self.tp.tf:
            # df is the document frequency of the word, so the number of documents into which
            # the word is contained, therefore given the structure of the @tp.tf dictionary
            # the 'df' is equal to the length of the list given by tp.tf[word]
            df = len(self.tp.tf[word])
            # the wordID is given by the term encoding given by the dictionary @tp.term_enc
            wordId = self.tp.term_enc[word]
            # for each tuple contained in the list @tp.tf[word]. REMEMBER: the tuple has a length of 2.
            # the first element is the doc_index and the second is the tf value
            for tfTuple in self.tp.tf[word]:
                # retrieve the doc_index
                doc_index = int(tfTuple[0])
                # retrieve the term frequency of that word in the document @doc_index
                tfValue = tfTuple[1]
                # calculate the idf value
                idf = log(self.tp.NUMBER_OF_DOCS / df + 1)
                # if the doc_index is already a key in the dictionary then the new tuple
                # is only appended
                if doc_index in self.tfidf:
                    self.tfidf[int(doc_index)].append((int(wordId) - 1, tfValue * idf))
                # otherwise a new entry corresponding to that doc_index is added and the value
                # is a list with a single element which is the tuple (wordId, tfidf{wordID,doc_index})
                else:
                    self.tfidf[int(doc_index)] = [(int(wordId) - 1, tfValue * idf)]