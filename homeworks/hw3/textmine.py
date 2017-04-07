import nltk
from pprint import pprint


def get_data():
    with open('1984', 'r') as f:
        text = f.read()

    return text[:5000]


def get_pos_tags(text):  # POS tagging
    sentences = nltk.sent_tokenize(text)
    tokens = [nltk.word_tokenize(sent) for sent in sentences]
    tagged = [nltk.pos_tag(sent) for sent in tokens]

    return tagged


def get_named_entities(text):  # NER with entity classification (using nltk.ne_chunk)
    """ Return dictionary 'EntityName':[TYPE, count] """
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    ne_chunked = nltk.ne_chunk(tagged)

    data = {}
    for entity in ne_chunked:
        if isinstance(entity, nltk.tree.Tree):
            text = " ".join([word for word, tag in entity.leaves()])
            ent = entity.label()
            if text not in data:
                data[text] = [ent, 0]
            data[text][1] += 1
        else:
            continue

    return data


def custom_entity_to_str(entity):
    """ Entity = [[word,tag], [word,tag] ...]"""
    return " ".join([word[0] for word in entity])


def get_custom_parsed_entities(tagged_list):
    """
    # (determiner)? (adjective)* (preposition (determiner)? )? [NNP or NNPS]

    (determiner)? (adjective)* [NNP or NNPS]

    Args:
        tagged_list:

    Returns:

    """
    tagged_entities = {}
    entity = []

    determiners = ['DT']
    adjectives = ['JJ']
    # nouns = ['NN', 'NNS', 'NNP', 'NNPS']
    nouns = ['NNP', 'NNPS']

    # By default, if continue is not called in the loop, current entity is deleted
    for tagged_sentence in tagged_list:
        for tagged_word in tagged_sentence:
            word_txt = tagged_word[0]
            word_tag = tagged_word[1]
            if not entity:  # entity empty -> accept DT or ADJ or NNP/S
                if word_tag in determiners + adjectives:
                    entity.append(tagged_word)
                    continue

                elif word_tag in nouns:  # If first word is a proper noun, use as entity
                    entity.append(tagged_word)
                    entity_str = custom_entity_to_str(entity)
                    if entity_str not in tagged_entities:
                        tagged_entities[entity_str] = [entity, 0]
                    tagged_entities[entity_str][1] += 1

            else:  # Entity not empty -> accept depending on the last item in it
                if entity[-1][1] in determiners + adjectives:  # Current state is DT or JJ
                    if word_tag == 'JJ':  # If received JJ, add it to list
                        entity.append(tagged_word)
                        continue

                    elif word_tag in nouns:  # If received NNP/S, entity is finalized
                        entity.append(tagged_word)
                        entity_str = custom_entity_to_str(entity)
                        if entity_str not in tagged_entities:
                            tagged_entities[entity_str] = [entity, 0]
                        tagged_entities[entity_str][1] += 1

            entity = []

    return tagged_entities


def main():
    limit_results = 20

    text = get_data()
    tagged_tokens = get_pos_tags(text)
    print("=" * 80)
    print("Tokens (truncated):")
    pprint(tagged_tokens[:limit_results], indent=2)
    print("=" * 80)

    named_entities = get_named_entities(text)
    print("=" * 80)
    print("Top entities:")
    # Sort by value (entity[1]), using its second field (i.e. count)
    sorted_entities = sorted(named_entities.items(), key=lambda entity: entity[1][1], reverse=True)
    pprint(sorted_entities[:limit_results])

    custom_parsed_entities = get_custom_parsed_entities(tagged_tokens)
    print("=" * 80)
    print("Top custom tagged entities:")
    # Sort by value (entity[1]), using its second field (i.e. count)
    sorted_entities = sorted(custom_parsed_entities.items(), key=lambda entity: entity[1][1], reverse=True)
    for custom_entity in sorted_entities[:limit_results]:
        print("({}x) {}".format(custom_entity[1][1], custom_entity))


if __name__ == '__main__':
    main()
