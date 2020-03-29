from bs4 import BeautifulSoup, Comment
import sys
import requests
import argparse
from stanfordnlp.server import CoreNLPClient

def annotate_kbp(plain_text):
    #annotate text with KBPAnnotator
    #extract all relations specified by input parameter r.

    #parser = argparse.ArgumentParser()
    #parser.add_argument('--input_text_file_path', '-i', required=True, help="Path to the text file to be parsed")
    #args = parser.parse_args()

    with open(plain_text+".txt", 'r') as f:
        text = f.read()

    #text = "Chris Manning is a nice person. Chris wrote a simple sentence. He also gives oranges to people."
    print('---')
    print('starting up Java Stanford CoreNLP Server...')

    # set up the client
    annotators_ner = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner']
    annotators_kbp = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse', 'coref', 'kbp']

    with CoreNLPClient(timeout=10000, memory = '4G',be_quiet=True) as pipeline:
        ann_ner = pipeline.annotate(text,annotators = annotators_ner)
        qualifying_sentences = []
        for s in ann_ner.sentence:
            sentence_string = ""
            is_person = False
            for word in s.token:
                if word.ner == "PERSON":
                    is_person = True
            if is_person == True:
                for word in s.token:
                    sentence_string = sentence_string + " " + word.word
            if sentence_string != "":
                qualifying_sentences.append(sentence_string)
    print("qualifying sentences: ")
    print(qualifying_sentences)
    print(len(qualifying_sentences))

annotate_kbp("8")
