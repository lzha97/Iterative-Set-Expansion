# Iterative-Set-Expansion

## Project 2 for COMS6111 Advanced Databases

The following project implements a version of the Iterative Set Expansion (ISE) algorithm using Google Custom Search API, Stanford's CoreNLP library, and Beautiful Soup. In this project we retrieve and parse webpages, prepare and annotate text on the webpages and extract structured relational information from the webpages. 

## Names and UNI: 
Lillian Zha (lz2527), Emily Hao (esh2160)
 
## Files Included: 
- Iterative_set_expansion.py
- README.md
- transcripts/
 
## Usage:  
```python3 iterative_set_expansion.py <api_key> <engine_id> <relation> <threshold> <query> <k>``` 
 
## Usage Example: 
```python3 iterative_set_expansion.py <api_key> <engine_id> 4 0.7 "bill gates Microsoft" 10```

## Requirements:
The project was developed and run using Google Cloud infrastructure. To run the program, you need a Google Custom Search API key and a Google Search Engine ID which are both free. We used a 'n1-standard-4 (4 vCPU, 15 GB memory)' Google VM to avoid memory issues during the annotation portion (for which we used CoreNLP).

## Dependencies:
- Beautiful Soup
    ```
    sudo apt-get install python3-bs4
    ```
- Stanford CoreNLP
    ```sudo apt-get update
    # Get Stanford CoreNLP
    wget  http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip
    sudo apt-get install unzip
    unzip stanford-corenlp-full-2018-10-05.zip
    export CORENLP_HOME=/home/username/stanford-corenlp-full-2018-10-05``` 
- Java 13 
    ```wget https://download.java.net/java/GA/jdk13.0.2/d4173c853231432d94f001e99d882ca7/8/GPL/openjdk-13.0.2_linux-x64_bin.tar.gz
    tar -xvzf openjdk-13.0.2_linux-x64_bin.tar.gz
    export PATH=/home/username/jdk-13.0.2/bin:$PATH
    export JAVA_HOME=/home/username/jdk-13.0.2```
 
## Implementation Description: 
As described in the assignment instructions, our program takes in a relation, a threshold, a query, and a number of desired tuples and extracts the appropriate tuples from web pages. 
 
First, our program validates the input and makes a request to the CustomSearch API with the query inputted to get the top 10 results. Using beautiful soup, we strip the html of each result for just plain text and write the text to a file named by < result_index >.txt for each webpage. 
 
(Step 3) For each text file, `run_pipelines` annotates and extracts tuples in two pipelines. The first pipeline, consisting of `tokenize`, `ssplit`, `pos`, `lemma`, and `ner`, is applied to the entire text. If a sentence returned by the annotator contains the right entities for the specified relation, then the sentence qualifies for the second pipeline and is added to a list of qualified sentences. `pipeline2` then receives that list and applies `tokenize`, `ssplit`, `pos`, `lemma`, `ner`, `depparse`, `coref`, and `kbp` to each of the qualifying sentences. The annotator returns the tuples found in that sentence. If the tuple has high enough confidence, the right relation, and is either not in the set of tuples for that text file or has higher confidence score, then it is added to the set, which `run_pipelines` then returns. 
 
For each relation returned by `annotate_kbp`, if the tuple was not in set X or if it had a higher confidence score, then it is added to X (replacing previous identical tuples if already in X). After all 10 web pages have been processed, the tuples in X are sorted by confidence score and X is returned and outputted if it contains more results than the input K. Otherwise, a new query is selected from X, built from the tuple previously un-queried with the highest confidence score.
 
## Additional Info: 
The implementation generates 10 text files containing the plain text of the webpages returned by the CustomSearch API. The permissions on these files must be readable by the program. The permissions on the folder must also allow the program to create and write to these files. The program will also generate a log file named < time_stamp >.log that contains a transcript of the output for the parameters inputted. 
 