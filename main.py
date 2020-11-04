import re
from datetime import datetime
from ioc_finder import find_iocs
from quantulum3 import parser
import flask
import json
import spacy
from stanfordcorenlp import StanfordCoreNLP
nlp = spacy.load("en_core_web_sm")


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


def extract_from_text(request):

    request_json = request.get_json(silent=True)
    get_request_args = request.args
    post_request_args = request.form

    if request_json and 'input' in request_json:
        text = request_json['input']
    elif get_request_args and 'input' in get_request_args:
        text = get_request_args['input']
    elif post_request_args and 'input' in post_request_args:
        text = post_request_args['input']

    full_result = dict()

    if text == '':
        return 'You have to pass string or list of strings !!!!'

    if type(text) == str:
        result = []
        if check_emails_regex(text):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:email"] = extract_emails_regex(text)
            loc_result["kraken:extractor"] = "extract_from_text-email_extractor"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)

        if check_urls_ioc_finder(text):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:url"] = extract_urls_ioc_finder(text)
            loc_result["kraken:extractor"] = "extract_from_url_extractor_ioc-finder"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)

        if check_urls_regex(text):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:url"] = extract_urls_regex(text)
            loc_result["kraken:extractor"] = "extract_from_url_extractor_regex"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)

        if check_phone_numbers_ioc_finder(text):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:phone-numbers"] = extract_phone_numbers_ioc_finder(text)
            loc_result["kraken:extractor"] = "extract_from_phone_extractor_ioc_finder"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)

        if check_geography(text):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:city-state-country"] = extract_geography(text)
            loc_result["kraken:extractor"] = "extract_from_spacy_ner"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)

        if check_quantities(text):
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:quantities"] = extract_quantities(text)
            loc_result["kraken:extractor"] = "extract_from_qty_extractor_quantulum3"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)

        stanford_core_nlp = StanfordCoreNLP(r'stanford-corenlp-4.1.0', memory='1g')
        entities = stanford_core_nlp.ner(text)
        stanford_core_nlp.close()
        job_titles = []
        for j in range(len(entities)):
            if entities[j][1] == 'TITLE':
                if j == 0:
                    job_titles.append(entities[j][0])
                else:
                    if entities[j - 1][1] == 'TITLE':
                        job_titles[len(job_titles) - 1] = job_titles[len(job_titles) - 1] + ' ' + entities[j][0]
                    else:
                        job_titles.append(entities[j][0])

        if len(job_titles) != 0:
            loc_result = dict()
            loc_result["@type"] = "schema:contactpoint"
            loc_result["schema:job-title"] = job_titles
            loc_result["kraken:extractor"] = "extract_from_title_extractor"
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
            loc_result["kraken:extracteddate"] = dt_string
            result.append(loc_result)
        full_result[text] = result

    elif isinstance(text, list):
        for txt in text:
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

            stanford_core_nlp = StanfordCoreNLP(r'stanford-corenlp-4.1.0', memory='1g')
            entities = stanford_core_nlp.ner(txt)
            stanford_core_nlp.close()
            job_titles = []
            for j in range(len(entities)):
                if entities[j][1] == 'TITLE':
                    if j == 0:
                        job_titles.append(entities[j][0])
                    else:
                        if entities[j-1][1] == 'TITLE':
                            job_titles[len(job_titles) - 1] = job_titles[len(job_titles) - 1] + ' ' + entities[j][0]
                        else:
                            job_titles.append(entities[j][0])

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
    return json.dumps(full_result), 200, {'Content-Type': 'application/json'}







