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

## Log output transcript by the timestamp when the program was run 
FILETIME = str(time.time())

### Print output to a transcript file 
def transcript(string):
    with open(FILETIME + '.log', 'a+') as f:
        print(string)
        f.write(string+'\n')


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
                output += '{} '.format(t)
    transcript('\tFetching text from url ...')
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


## Runs first pipeline (NER annotators to get qualifying sentences) and calls pipeline2
def run_pipelines(file_name, relation, threshold):

    annotators_ner = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner'] 
    places = ["LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]

    with open(file_name + ".txt", 'r') as f: text = f.read()

    ## start session
    with CoreNLPClient(timeout=300000, memory = '4G',be_quiet=False) as pipeline:

        ann_ner = pipeline.annotate(text,annotators = annotators_ner)
        num_sentences = len(ann_ner.sentence)
        transcript('\tAnnotating the webpage using [tokenize, ssplit, pos, lemma, ner] annotators ...\n\tExtracted '+str(num_sentences)+' sentences. Processing each sentence one by one to check for presence of right pair of named entity types; if so, will run the second pipeline ...')

        # Get qualifying sentences 
        qualifying_sentences = []
        ct_processed = 0

        for s in ann_ner.sentence:
            ct_processed += 1
            sentence_string = ""
            has_person = False
            has_org = False
            has_place = False

            for word in s.token:
                if word.ner == "PERSON": has_person = True
                if word.ner == "ORGANIZATION": has_org = True
                if word.ner in places: has_place == True

            if relation  == "per:cities_of_residence" and has_person and has_place:
                for word in s.token:
                    sentence_string = sentence_string + " " + word.word
            elif has_person and has_org:
                for word in s.token:
                    sentence_string = sentence_string + " " + word.word
            if sentence_string != "":
                qualifying_sentences.append((sentence_string,ct_processed))

        return pipeline2(qualifying_sentences, num_sentences, pipeline, relation, threshold)


## Pipeline 2 KBP annotators to get correct relations satisfying threshold 
def pipeline2(qualifying_sentences, num_sentences, pipeline, relation, threshold):

    annotators_kbp = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse', 'coref', 'kbp']
    ct_relation = 0
    sent_with_kbp = 0
    tuples = dict()

    for sent in qualifying_sentences:

        ann_kbp = pipeline.annotate(sent[0], annotators = annotators_kbp)
        transcript('\tProcessed '+ str(sent[1])+' / '+str(num_sentences))

        for sentence in ann_kbp.sentence:
            for kbp_triple in sentence.kbpTriple:
                if kbp_triple.relation == relation:

                    ct_relation +=1
                    sent_with_kbp += 1
                    transcript('\t\t=== Extracted Relation ===\n\t\tSentence: '+ str(sent[0]))
                    transcript(f"\t\tConfidence: {kbp_triple.confidence}; Subject: {kbp_triple.subject}; Relation: {kbp_triple.relation}; Object: {kbp_triple.object}")
                    
                    if kbp_triple.confidence >= threshold:
                        tup = (kbp_triple.subject,kbp_triple.relation,kbp_triple.object)
                        if tup not in tuples:
                            tuples[tup] = kbp_triple.confidence
                            transcript('\t\tAdding to set of extracted relations')
                        elif kbp_triple.confidence > tuples[tup]:
                            tuples[tup] = kbp_triple.confidence
                            transcript('\t\tThe same relation is already present but with a lower confidence. Just updating the confident value.')

                    else: transcript('\t\tConfidence is lower than threshold confidence. Ignoring this.')
                    transcript('\t\t==========================')

    transcript('\tExtracted kbp annotations for '+str(sent_with_kbp)+ ' out of total '+str(num_sentences)+' sentences')

    return tuples, ct_relation


### annotate and extract relevant tuples from a text file
def annotate_kbp(file_name, relation, threshold):
    return run_pipelines(file_name, relation, threshold)


### iterative set expansion
def ise():
    iteration = 0
    X = dict() # relation set
    queried = set() # queries that have been made
    fstart = time.time()
    
    results = make_request(G_API_KEY, G_ENGINE_ID, query)
    
    '''urls = ['https://www.nytimes.com/2020/03/13/technology/bill-gates-microsoft-board.html',
            'https://www.cnbc.com/2020/03/13/bill-gates-leaves-microsoft-board.html',
            'https://www.theverge.com/2020/3/13/21179214/bill-gates-steps-down-microsoft-board-philanthropy',
            'https://techcrunch.com/2020/03/13/bill-gates-leaves-microsofts-board/',
            'https://www.wired.com/story/bill-gates-steps-down-microsoft-board/',
            'https://en.wikipedia.org/wiki/Bill_Gates',
            'https://www.bbc.com/news/business-51883377',
            'https://news.microsoft.com/2020/03/13/microsoft-announces-change-to-its-board-of-directors/',
            'https://www.cnn.com/2020/03/13/business/bill-gates-microsoft-berkshire-boards/index.html',
            'https://arstechnica.com/information-technology/2020/03/bill-gates-steps-down-from-microsoft-board/']'''

    while len(X) < K:

        transcript('=========== Iteration: ' + str(iteration) + ' - Query: ' + query + ' =========== ')

        for idx, val in enumerate(results):
            relct = 0
            url = val['link']
            #url = urls[idx]
            transcript('URL (' + str(idx+1)+' / 10): '+ url)

            ## only check webpages that have not been visited before 
            if url in visited_urls: continue
            else: visited_urls.add(url)

            ## Get webpage and strip for plain text. Save plain text in file by index: <index>.txt
            r = requests.get(url)
            if r.status_code == 200:
                plain_text = get_text_from_html(r.content)[:20000]
                transcript('\tWebpage length (num characters): ' + str(len(plain_text)))
                with open(str(idx)+'.txt', 'w+') as file:
                    file.write(plain_text)

            ## Annotate webpage and get qualifying relations to be added to X
            new_tuples, num_rel = annotate_kbp(str(idx),RELATION,THRESHOLD)

            for tup in new_tuples:
                if tup not in X or X[tup] < new_tuples[tup]:
                    X[tup] = new_tuples[tup]
                    relct +=1

            transcript('\tRelations extracted from this website: '  +  str(relct) +  '  (Overall: ' +  str(num_rel)+')\n')

        ## Sort set X of relations by the confidence scores of the relation in decreasing order
        X = {k:v for k, v in sorted(X.items(), key=lambda item: item[1], reverse=True)}

        ## Return X if it has enough relations
        if len(X) >= K:
            #topK = list(X.keys())[:int(K)]
            #res_X = dict()
            #for x in X:
            #    if x in topK: res_X[x] = X[x]
            return X, iteration

        ## Attempt another iteration by generating new query 
        ## Create query by selecting relation Y (previously unqueried) from X with highest confidence score 
        else:
            Y = None
            for y in X:
                if y not in queried:
                    queried.add(y)
                    Y = y
                    break
            if not Y:
                transcript('ISE has "stalled" before retrieving k high-confidence tuples')
                return
            new_query = Y[0] + ' ' + Y[1] + ' ' + Y[2]
            results = make_request(G_API_KEY, G_ENGINE_ID, new_query)
        iteration +=1




### Get Input
G_API_KEY = sys.argv[1]
G_ENGINE_ID = sys.argv[2]
RELATION = float(sys.argv[3]) # 1 for Schools_Attended, 2 for Work_For, 3 for Live_In, 4 for Top_Member_Employees
THRESHOLD = float(sys.argv[4]) # extraction confidence threshold
query = sys.argv[5] # seed query for relation to extract
K = float(sys.argv[6]) # number of tuples requested in output

visited_urls = set()

### Validate Input
if not (1 <= RELATION <= 4 and RELATION.is_integer()):
    transcript('Incorrect value for R (Relation). \nUsage: python3 iterative_set_expansion.py <api-key> <engine-id> <relation> <threshold> <"query"> <k>')
    sys.exit()
if not 0 <= THRESHOLD <= 1:
    transcript('Incorrect value for T (Threshold). \nUsage: python3 iterative_set_expansion.py <api-key> <engine-id> <relation> <threshold> <"query"> <k>')
    sys.exit()
if not (K >= 0 and K.is_integer()):
    transcript('Incorrect value for K. \nUsage: python3 iterative_set_expansion.py <api-key> <engine-id> <relation> <threshold> <"query"> <k>')
    sys.exit()

### Convert relation keys
if RELATION == 1: RELATION = "per:schools_attended"
if RELATION == 2: RELATION = "per:employee_or_member_of"
if RELATION == 3: RELATION = "per:cities_of_residence"
if RELATION == 4: RELATION = "org:top_members_employees"

transcript('----\nParameters:\nClient key\t= <'+G_API_KEY+'>\nEngine key\t= <'+G_ENGINE_ID+'>')
transcript('Relation\t= '+ RELATION+'\nThreshold\t= '+str(THRESHOLD)+'\nQuery\t\t= '+query+'\n# of Tuples\t= '+ str(K)+'\n')
transcript('Loading necessary libraries; This should take a minute or so ... \n')





### Run Iterative Set Expansion 
start = time.time()
X, iterations = ise()
end = time.time()

### Print Outputted Relations
transcript('\n\n================== ALL RELATIONS (' + str(len(X)) + ') ==================')
for x in X:
    conf = X[x]
    sub = x[0]
    rel = x[1]
    obj = x[2]
    transcript("Confidence: " + "{:.4f}".format(conf) + "  | Subject: " + "{:<15}".format(sub) + '   | Relation: ' + "{:<15} ".format(rel) + '   | Object: ' + '{:<15}'.format(obj))
transcript('Total Runtime: ' + str((end-start)/60))
transcript('Num_Iterations: '+str(iterations))



