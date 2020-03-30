'''''''''''''''''''''
Lillian Zha & Emily Hao
Project 2
COMS6111 Advanced Databases
25 March 2020
'''''''''''''''''''''

from bs4 import BeautifulSoup, Comment
import sys
import requests
import argparse
from stanfordnlp.server import CoreNLPClient
import time


### Extract Plain Text From HTML
def get_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.find_all(text=True)
    for element in text:
        if isinstance(element, Comment): element.extract()
    blacklist = ['form', 'button', 'svg', '[document]', 'noscript', 'header', 'html', 'meta', 'title', 'head', 'code', 'input', 'script', 'style']
    output = ''
    for t in text:
        if t.parent:
            if t.parent.name not in blacklist:
                #print(t.parent.name)
                output += '{} '.format(t)
    return output


### Make Request to Custom Search API
def make_request(G_API_KEY, G_ENGINE_ID, query):
   
    base_url = "https://www.googleapis.com/customsearch/v1"
    payload = {'key': G_API_KEY, 'cx': G_ENGINE_ID, 'q':query, 'alt': 'json'}
    headers={'Accept': 'application/json'}
    results = ''
    response = requests.get(base_url, params=payload, headers=headers)
    if response.status_code == 200:
        results = response.json()['items']
    return results


##annotate and extract relevant tuples from a text file
def annotate_kbp(file_name, relation, threshold):
    places = ["LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]
    tuples = dict()

    with open(file_name + ".txt", 'r') as f:
        text = f.read()

    annotators_ner = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner']
    annotators_kbp = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse', 'coref', 'kbp']

    with CoreNLPClient(timeout=300000, memory = '4G',be_quiet=True as pipeline:
        ann_ner = pipeline.annotate(text,annotators = annotators_ner)
        qualifying_sentences = []
        for s in ann_ner.sentence:
            sentence_string = ""
            has_person = False
            has_org = False
            has_place = False
            for word in s.token:
                if word.ner == "PERSON":
                    has_person = True
                if word.ner == "ORGANIZATION":
                    has_org = True
                if word.ner in places:
                    has_place == True
            if relation  == "per:cities_of_residence" and has_person and has_place:
                for word in s.token:
                    sentence_string = sentence_string + " " + word.word
            elif has_person and has_org:
                for word in s.token:
                    sentence_string = sentence_string + " " + word.word
            if sentence_string != "":
                qualifying_sentences.append(sentence_string)

        for sentence in qualifying_sentences:
            ann_kbp = pipeline.annotate(sentence, annotators = annotators_kbp)
            for sentence in ann_kbp.sentence:
                for kbp_triple in sentence.kbpTriple:
                    print(f"Confidence: {kbp_triple.confidence};\t Subject: {kbp_triple.subject};\t Relation: {kbp_triple.relation}; Object: {kbp_triple.object}\n")
                    if kbp_triple.relation == relation and kbp_triple.confidence >= threshold:
                        tup = (kbp_triple.subject,kbp_triple.relation,kbp_triple.object)
                        if tup not in tuples or kbp_triple.confidence > tuples[tup]:
                            tuples[tup] = kbp_triple.confidence
                            print('ADDED: ', tup)
    print('NEW_TUPLES:', tuples)                  
    return tuples


### Get Input
G_API_KEY = sys.argv[1]
G_ENGINE_ID = sys.argv[2]
RELATION = float(sys.argv[3]) # 1 for Schools_Attended, 2 for Work_For, 3 for Live_In, 4 for Top_Member_Employees
THRESHOLD = float(sys.argv[4]) # extraction confidence threshold
query = sys.argv[5] # seed query for relation to extract
print(query)
K = float(sys.argv[6]) # number of tuples requested in output

if not (1 <= RELATION <= 4 and RELATION.is_integer()):
    print('Incorrect value for R (Relation). \nUsage: python3 iterative_set_expansion.py <api-key> <engine-id> <relation> <threshold> <"query"> <k>')
    sys.exit()
if not 0 <= THRESHOLD <= 1:
    print('Incorrect value for T (Threshold). \nUsage: python3 iterative_set_expansion.py <api-key> <engine-id> <relation> <threshold> <"query"> <k>')
    sys.exit()
if not (K >= 0 and K.is_integer()):
    print('Incorrect value for K. \nUsage: python3 iterative_set_expansion.py <api-key> <engine-id> <relation> <threshold> <"query"> <k>')
    sys.exit()

if RELATION == 1: RELATION = "per:schools_attended"
if RELATION == 2: RELATION = "per:employee_or_member_of"
if RELATION == 3: RELATION = "per:cities_of_residence"
if RELATION == 4: RELATION = "per:top_members_employees"


def ise():
    results = make_request(G_API_KEY, G_ENGINE_ID, query)

    X = dict()
    queried = set() 
    fstart = time.time()
    while len(X) < K: 
        for idx, val in enumerate(results):
            r = requests.get(val['link'])
            if r.status_code == 200:
                plain_text = get_text_from_html(r.content)[:20000]
                with open(str(idx)+'.txt', 'w+') as file:
                    file.write(plain_text)
              
            new_tuples = annotate_kbp(str(idx),RELATION,THRESHOLD)
            for tup in new_tuples:
                if tup not in X or X[tup] < new_tuples[tup]:
                    X[tup] = new_tuples[tup]

        X = {k:v for k, v in sorted(X.items(), key=lambda item: item[1], reverse=True)}
        print('\n\n\n\n', (time.time() - fstart)/ 60, "\t", len(X), "\n", X, '\n\n\n\n')
        if len(X) >= K: 
            print('here')
            return list(X.keys[:K])
        
        else: 
            Y = None
            for y in X: 
                if y not in queried: 
                    queried.add(y)
                    Y = y 
                    break
            if not Y: 
                print('ISE has "stalled" before retrieving k high-confidence tuples')
                return 
            new_query = Y[0] + ' ' + Y[1] + ' ' + Y[2]
            results = make_request(G_API_KEY, G_ENGINE_ID, new_query)
            
start = time.time()
X = ise()
end = time.time()
print('RESULTS:\n', X)
print('Total Time: ', (end-start)/60)
#webpages are saved by index in files <index>.txt
