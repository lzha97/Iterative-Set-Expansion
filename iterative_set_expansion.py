'''''''''''''''''''''
Lillian Zha & Emily Hao
Project 2
COMS6111 Advanced Databases 
25 March 2020 
'''''''''''''''''''''

from bs4 import BeautifulSoup
import sys 
import requests


### Extract Plain Text From HTML
def get_text_from_html(html): 
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.find_all(text=True)
    blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'title', 'head', 'input', 'script', 'style']
    output = ''
    for t in text: 
        if t.parent.name not in blacklist: 
            output += '{} '.format(t)
    return output 


### Get Input 
G_API_KEY = sys.argv[1]
G_ENGINE_ID = sys.argv[2]
RELATION = float(sys.argv[3]) # 1 for Schools_Attended, 2 for Work_For, 3 for Live_In, 4 for Top_Member_Employees
THRESHOLD = float(sys.argv[4]) # extraction confidence threshold
QUERY = sys.argv[5] # seed query for relation to extract
K = float(sys.argv[6]) # number of tuples requested in output 

if not (1 <= RELATION <= 4 and RELATION.is_integer()): 
    print('Incorrect value for R (Relation). \nUsage: python3 iterative_set_expansion.py <api-key> <engine-id> <relation> <threshold> <"query"> <k>') 
    sys.exit()
if not 0 <= THRESHOLD <= 1: 
    print('Incorrect value for T (Threshold). \nUsage: python3 iterative_set_expansion.py <api-key> <engine-id> <relation> <threshold> <"query"> <k>') 
    sys.exit()
if not (K > 0 and K.is_integer()): 
    print('Incorrect value for K. \nUsage: python3 iterative_set_expansion.py <api-key> <engine-id> <relation> <threshold> <"query"> <k>') 
    sys.exit()



### Make Request to Custom Search API
base_url = "https://www.googleapis.com/customsearch/v1"
payload = {'key': G_API_KEY, 'cx': G_ENGINE_ID, 'q': QUERY, 'alt': 'json'}
headers={'Accept': 'application/json'}
results = '' 
response = requests.get(base_url, params=payload, headers=headers)
if response.status_code == 200: 
    results = response.json()['items']


webpages = dict()
print('RESULTS:')
for idx, val in enumerate(results): 
    print(str(idx+1)+':', val['title'])
    link = val['link']
    r = requests.get(link)
    if r.status_code == 200: 
        plain_text = get_text_from_html(r.content)[:20000]
        webpages[idx] = plain_text
        print(len(plain_text))
        print()


#use webpages here: webpages = {0: some webpage, 1: some other webpage ..... 9: some last webpage}

