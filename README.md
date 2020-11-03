# Solmax_IT

## extract_from_text

Python functions to extract unstructured information from text.

### Requirements

- Develop extractors to retrieve each of the following information from a string:
  - Emails
  - URLs
  - Phone numbers
  - Cities, states / provinces, countries
  - Job titles
  - Quantities
- Normalize the data found
  - Phone number: E.164
  - Geography: ISO 
- Output result in a list of json-ld schema.org records
  - email: https://schema.org/ContactPoint 
  - phone: https://schema.org/ContactPoint
  - url: https://schema.org/WebPage
- Develop test cases for each extractors that includes the following scenarios:
  - Valid, typical input
  - Null input
  - Non-string input
  - Non-existing object in string (for example, testing the phone extractor and no phone number is in the test input string).
  - Multiple object in string

## input:
string: the text to extract information from
You can enter text as you like just enter y or Y to continue

## output:
json list of structured records

## Description
The function accepts a string or list of string and returns a list of structured records. The information is extracted using regex or python libraries. 

Each record contains a reference to the extractor that has been used. 
For example, the string "Steve can be reached at steve@apple.com" would give:
```
    {
    "@type": schema:contactpoint",
    "schema:email": "steve@apple.com",
    "kraken:extractor": "extract_from_text-email_extractor",
    "kraken:extracteddate": 2020-10-28T20:43:55+00:00
    }
```

### Extractors:

Object extracted | Extractor name | Library
-----------------|----------------|--------
Emails | email_extractor_regex | regex
URLs | url_extractor_ioc-finder | ioc-finder
URLs | url_extractor_regex | regex
Phone numbers | phone_extractor_ioc_finder | ioc-finder
City, state, country | geo_extractor_spacy | spacy
Job title | title_extractor | pycorenlp
Quantities | qty_extractor_quantulum3 | quantulum3

### Steps for Windows usage:

1. Download Latest version of java. You can download it freely from here https://www.java.com/en/download/
2. Download the JAR files for the StanfordCoreNLP libraries "English models only" from here https://stanfordnlp.github.io/CoreNLP/download.html
3. Unzip the downloaded folder and Navigate to the path where you unzipped the JAR files folder.
4. Execute the following command on the command prompt : java -mx1g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 100000000
5. Use python version 3.7.9 and pip version 20.2.4 
6. Execute the following command on the command prompt : git clone https://github.com/Eng-MohamedHussien/Solmax_IT.git
7. Execute the following command on the command prompt : pip install -r requirements.txt
8. Finally, execute the following command on the command prompt : python extractor.py