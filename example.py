from bs4 import BeautifulSoup, Comment
import sys
import requests
import argparse
from stanfordnlp.server import CoreNLPClient

def annotate_kbp(file_name,relation,threshold):
    tuples = []

    with open(file_name + ".txt", 'r') as f:
        text = f.read()

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

        for sentence in qualifying_sentences:
            ann_kbp = pipeline.annotate(sentence, annotators = annotators_kbp)
            for sentence in ann_kbp.sentence:
                for kbp_triple in sentence.kbpTriple:
                    print(f"\t Confidence: {kbp_triple.confidence};\t Subject: {kbp_triple.subject};\t Relation: {kbp_triple.relation}; Object: {kbp_triple.object}")
                    if kbp_triple.relation == relation and kbp_triple.confidence >= threshold:
                        tuples.append((kbp_triple.subject,kbp_triple.relation,kbp_triple.object))
    return tuples

annotate_kbp("example","per:exmployee_or_member_of",0.7)
