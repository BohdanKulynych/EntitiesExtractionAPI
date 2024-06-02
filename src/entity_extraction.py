import spacy
from typing import Dict, List


def extract_ordinary_entities(text: str, model='en_core_web_sm') -> Dict[str, str]:
    """
    Given function aims to extract ordinary entities, as port of text preprocessing. We aim to solve the problem
    of mismatch between name of drug and name of researcher from the paper.
     Find all possible entites here [https://dataknowsall.com/blog/ner.html]

    We're going to remove only following entities:
    PERSON:      People, including fictional.
    ORP:        Nationalities or religious or political groups
    GPE:         Countries, cities, states.
    LOC:         Non-GPE locations, mountain ranges, bodies of water.

    This entity seems resonable to remove, however it may be mismatched with disease name (TBD)
    ORG:         Companies, agencies, institutions, etc.

    :param text: partially cleaned text
    :param model: en_core_web_sm, default entity extraction model
    :return:
    """
    nlp = spacy.load(model)
    doc = nlp(text)
    entities = {}
    for token in doc.ents:
        entities[token.text] = token.label_

    return entities


def extract_clinical_entities(text: str, model='en_ner_bc5cdr_md') -> List[Dict]:
    """
    This function extracts only clinical and drug entities
    :param text: cleaned text
    :param model: en_ner_bc5cdr_md - extracts mostly disease entities, en_core_med7_lg - extracts drug entities
    :return: list of entites
    """
    nlp = spacy.load(model)
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({
            "entity": ent.text,
            "label": ent.label_,
            "context": text[max(ent.start_char - 30, 0):min(ent.end_char + 30, len(text))],
            "start": ent.start_char,
            "end": ent.end_char
        })
    return entities
