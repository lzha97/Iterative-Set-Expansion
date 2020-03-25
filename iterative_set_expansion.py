import bs4 as bs 
import sys 
import requests

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


### Build Request

base_url = "https://www.googleapis.com/customsearch/v1"
payload = {'key': G_API_KEY, 'cx': G_ENGINE_ID, 'q': QUERY, 'alt': 'json'}
headers={'Accept': 'application/json'}


### Make Request

response = requests.get(base_url, params=payload, headers=headers)
results = response.json()['items']

print('RESULTS:')
for idx, val in enumerate(results): 
    print(str(idx+1)+':', val['title'])

