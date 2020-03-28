from stanfordnlp.server import CoreNLPClient

# example text
print('---')
print('input text')
print('')

text = "Chris Manning is a nice person. Chris wrote a simple sentence. He also gives oranges to people."
text1 = "Joe Smith was born in Oregon."
print(text1)

# set up the client
print('---')
print('starting up Java Stanford CoreNLP Server...')

# set up the client
#with CoreNLPClient(annotators=['tokenize','ssplit','pos','lemma','ner', 'parse', 'depparse','coref'], timeout=30000, memory='16G') as client:
annotators_ner = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner']
annotators_kbp = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse', 'coref', 'kbp']

with CoreNLPClient(timeout=10000, memory = '4G',endpoint="http://localhost:9001") as pipeline:
    for j in range(100):
        #print(f">>>Repeating {j}th time.")
        # submit the request to the server
        """ann_ner = pipeline.annotate(text,annotators = annotators_ner)
        qualifying_sentences = []
        for s in ann_ner.sentence:
            is_person = False
            for word in s.token:
                if word.ner == "PERSON":
                    is_person = True
            if is_person == True:
                qualifying_sentences.append(s)
        #print("qualifying sentences: ")
        #print(qualifying_sentences)"""
        print("here")
        ann_kbp = pipeline.annotate(text1, annotators = annotators_kbp)
        print("after kbp")
        for sentence in ann_kbp.sentence:
            print("in here")
            for kbp_triple in sentence.kbpTriple:
                print("in here now")
                print(f"\t Confidence: {kbp_triple.confidence};\t Subject: {kbp_triple.subject};\t Relation: {kbp_triple.relation}; Object: {kbp_triple.object}")
