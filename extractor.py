import re
import json
from datetime import datetime
from ioc_finder import find_iocs
from quantulum3 import parser
from pycorenlp import StanfordCoreNLP
import spacy
nlp = spacy.load("en_core_web_sm")
nlp_wrapper = StanfordCoreNLP('http://localhost:9000')


def check_emails_regex(txt):
    regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    if re.search(regex, txt):
        return True
    else:
        return False


def extract_emails_regex(txt):
    regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return re.findall(regex, txt)


def check_urls_regex(txt):
    regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    if re.search(regex, txt):
        return True
    else:
        return False


def extract_urls_regex(txt):
    regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    return re.findall(regex, txt)


def check_urls_ioc_finder(txt):
    iocs = find_iocs(txt)
    if len(iocs['urls']) != 0:
        return True
    else:
        return False


def extract_urls_ioc_finder(txt):
    iocs = find_iocs(txt)
    return iocs['urls']


def check_phone_numbers_ioc_finder(txt):
    iocs = find_iocs(txt)
    if len(iocs['phone_numbers']) != 0:
        return True
    else:
        return False


def extract_phone_numbers_ioc_finder(txt):
    iocs = find_iocs(txt)
    return iocs['phone_numbers']


def check_geography(txt):
    doc = nlp(txt)
    if len(doc.ents) != 0:
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                return True
    return False


def extract_geography(txt):
    locations = []
    doc = nlp(txt)
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            locations.append(ent.text)
    return locations


def check_quantities(txt):
    quants = parser.parse(txt)
    if len(quants) != 0:
        return True
    else:
        return False


def extract_quantities(txt):
    quants = parser.parse(txt)
    return [quant.surface for quant in quants]


def main():
    lst_inputs = []
    while True:
        text = input('Enter text to be fetched: ')
        if text == '':
            print('You have to enter string !!!!')
            continue
        lst_inputs.append(text)
        answer = input('Do you want to continue? Y or N : ')
        if answer == 'N' or answer == 'n':
            break

    full_result = dict()
    for txt in lst_inputs:
        result = []
        if check_emails_regex(txt):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:email"] = extract_emails_regex(txt)
            loc_result["kraken:extractor"] = "extract_from_text-email_extractor"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)
        if check_urls_ioc_finder(txt):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:url"] = extract_urls_ioc_finder(txt)
            loc_result["kraken:extractor"] = "extract_from_url_extractor_ioc-finder"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)
        if check_urls_regex(txt):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:url"] = extract_urls_regex(txt)
            loc_result["kraken:extractor"] = "extract_from_url_extractor_regex"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)
        if check_phone_numbers_ioc_finder(txt):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:phone-numbers"] = extract_phone_numbers_ioc_finder(txt)
            loc_result["kraken:extractor"] = "extract_from_phone_extractor_ioc_finder"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)
        if check_geography(txt):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:city-state-country"] = extract_geography(txt)
            loc_result["kraken:extractor"] = "extract_from_spacy_ner"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)
        if check_quantities(txt):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:quantities"] = extract_quantities(txt)
            loc_result["kraken:extractor"] = "extract_from_qty_extractor_quantulum3"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)
        output = nlp_wrapper.annotate(txt, properties={'annotators': 'ner', 'outputFormat': 'json', 'timeout': 1000})
        job_titles = []
        for entity in output['sentences'][0]['entitymentions']:
            if entity['ner'] == 'TITLE':
                job_titles.append(entity['text'])
        if len(job_titles) != 0:
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:job-title"] = job_titles
            loc_result["kraken:extractor"] = "extract_from_title_extractor"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)
        full_result[txt] = result
    y = json.dumps(full_result)
    print(y)


if __name__ == "__main__":
    main()



