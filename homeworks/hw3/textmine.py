import nltk
from pprint import pprint


def get_data():
    with open('1984', 'r') as f:
        text = f.read()

    return text


def get_pos_tags(text):  # POS tagging
    sentences = nltk.sent_tokenize(text)
    tokens = [nltk.word_tokenize(sent) for sent in sentences]
    tagged = [nltk.pos_tag(sent) for sent in tokens]

    return tagged


def get_named_entities(text):  # NER with entity classification (using nltk.ne_chunk)
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    ne_chunked = nltk.ne_chunk(tagged, binary=True)

    data = {}
    for entity in ne_chunked:
        if isinstance(entity, nltk.tree.Tree):
            text = " ".join([word for word, tag in entity.leaves()])
            ent = entity.label()
            data[text] = ent
        else:
            continue

    return data


text = get_data()
tagged_tokens = get_pos_tags(text)
named_tokens = get_named_entities(text)
pprint(named_tokens)
