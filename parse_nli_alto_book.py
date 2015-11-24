#! /usr/bin/python3
# coding=utf-8

from lxml import etree
from pprint import pprint
from pathlib import Path
import db_api


def extract_words_from_alto_xml(filepath):
    """
    extract words from an xml file in alto format
    return list of words, each word is accompanied with metadata
    to locate its source

    """
    with filepath.open() as f:
        tree = etree.parse(f)
    words = []
    for word in tree.xpath("//String[@CONTENT]"):
        words.append({"ID": word.get("ID"),
                      "CONTENT": word.get("CONTENT"),
                      "PARENT": word.getparent().get("ID"),
                      "GRANDPARENT": word.getparent().getparent().get("ID"),
                      "PAGE_FILE": filepath,
                      })
    return words


def lookup(candidate, entities):
    """
        return first record in entities that match candidate
    """
    for record in entities:
        if candidate == record['name']:
            return record['id']
    return None


def slice(l, size):
    for i in range(len(l) + 1 - size):
        yield l[i:i + size]


def candidate2text(candidate):
    return " ".join([w['CONTENT'] for w in candidate])


def generate_candidate_variants(candidate):
    candidate_as_str = candidate2text(candidate)
    yield candidate_as_str
    candidate_as_str = candidate2text(candidate[::-1])
    yield candidate_as_str


def look_for_entities(words, entities):
    res = []
    for candidate in slice(words, 2):
        for candidate_as_str in generate_candidate_variants(candidate):
            t = db_api.lookup(candidate_as_str, None)
            if t:
                res.append((t['id'], candidate, candidate_as_str))
    return res


def gather_info_from_folder(path):
    folder = Path(path)
    res = []
    l = list(folder.glob('*.xml'))
    l = sorted(l)
    for f in l:
        words = extract_words_from_alto_xml(f)
        res += words
    return res


if __name__ == "__main__":
    path = "../nli_entities_sample_data/additional_books/IE26721743/REP26723234/"
    words = gather_info_from_folder(path)
    # pprint(res)
    entities = [
        {'id': 1, 'name': 'לחוק, התורהl', },
        {'id': 2, 'name': 'חייבים, לשמוע', },
        {'id': 3, 'name': 'ישראל, בניגוד', },
        {'id': 4, 'name': 'לחוק, בניגוד', },
    ]
    # TODO probably send source (name of file which contains page?) also
    res = look_for_entities(words, entities)
    print("number of result: {}".format(len(res)))
    pprint(res)
