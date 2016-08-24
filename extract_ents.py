#!/usr/bin/env python3
import json

code2type = {
    u'151': 'geo',
    u'451': 'geo',
    u'130': 'work',
    u'430': 'work',
    u'110': 'org',
    u'410': 'org',
    u'111': 'meet',
    u'411': 'meet',
    u'100': 'person',
    u'400': 'person'
}


def extract_data_from_json_record(record):
    ent_aliases = []
    ent_type = "other"
    ent_id = -1
    for item in record['items']:
        if item.get('attrs', None):
            tag = item['attrs'].get('tag', None)
            if tag:
                if tag == u'001':
                    ent_id = int(item['items'][0])
                elif tag[0] in ['1', '4']:
                    ent_type = code2type.get(tag, "other")
                    its = item.get('items')
                    if its and len(its) > 0 and item.get('items'):
                        alias = its[0]['items'][0]
                        ent_aliases.append(alias)

    return {"id": ent_id, "type": ent_type, "aliases": ent_aliases}


# mail from Eyal:
wanted_fields = ("100", "400", "110", "410", "150", "450", "151", "451")


def extract_data_from_entity_dict(record):
    ent_primary_aliases = []
    ent_secondary_aliases = []
    ent_type = "other"
    ent_id = -1
    ent_years = None

    for k, v in record.items():
        if k == u'001':
            ent_id = int(v[0]['#text'])
        elif k in wanted_fields:
            ent_type = code2type.get(k, "other")
            if ent_type == "person":
                try:
                    ent_years = v[0]['d']
                except KeyError:
                    pass

            for i in v:
                alias = i['a']
                if k[0] == '1':
                    ent_primary_aliases.append(alias)
                elif k[0] == '4':
                    ent_secondary_aliases.append(alias)

    if len(ent_primary_aliases):
        return {"id": ent_id,
                "type": ent_type,
                "primary_aliases": ent_primary_aliases,
                "secondary_aliases": ent_secondary_aliases,
                "years": ent_years}
    else:
        return None


if __name__ == "__main__":
    ents = []
    data = ''
    with open('nnl2_test.json', 'r') as inputfile:
        for line in inputfile:
            data += line
    js = json.loads(data, 'utf-8')

    for record in js['items'][:10]:
        ents.append(extract_data_from_json_record(record))

    with open('entities_test.json', 'w') as outfile:
        json.dump(ents, outfile, ensure_ascii=False)
