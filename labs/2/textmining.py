import pprint
from collections import Counter
import string
import nltk
from nltk.stem import WordNetLemmatizer


def get_sentences(text):
    sentences = nltk.sent_tokenize(text)
    return sentences


def get_words(text):
    sentences = nltk.sent_tokenize(text)
    tokens = [nltk.word_tokenize(sent) for sent in sentences]
    return tokens


def get_tags(text):
    sentences = nltk.sent_tokenize(text)
    tokens = [nltk.word_tokenize(sent) for sent in sentences]
    tagged = [nltk.pos_tag(sent) for sent in tokens]
    return tagged


def get_lemmas(text):
    lemmatizer = WordNetLemmatizer()
    tokens = nltk.word_tokenize(text)

    lemmas = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmas


def get_lemmas_from_tokens(tokens):
    lemmatizer = WordNetLemmatizer()

    lemmas = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmas


def _extract_entities(ne_chunked):
    data = {}
    for entity in ne_chunked:
        if isinstance(entity, nltk.tree.Tree):
            text = " ".join([word for word, tag in entity.leaves()])
            ent = entity.label()
            data[text] = ent
        else:
            continue
    return data


def get_entities(text):
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)

    ne_chunked = nltk.ne_chunk(tagged, binary=True)
    return _extract_entities(ne_chunked)


def get_sentiment(text):
    # import nltk.sentiment.util
    from nltk.sentiment import SentimentIntensityAnalyzer

    vader_analyzer = SentimentIntensityAnalyzer()
    return vader_analyzer.polarity_scores(text)


def get_token_count(tokens):
    counts = Counter(tokens)
    return sorted(counts.items(), key=lambda count: count[1], reverse=True)


def print_heading(title):
    print("-" * 80)
    print(title)
    print("-" * 80)


def main():
    with open('book.txt') as f:
        txt = f.read()

    print_heading("Top tokens before preprocessing: ")
    tokens = nltk.word_tokenize(txt)
    pprint.pprint(get_token_count(tokens)[:25])

    print_heading("Top tokens after preprocessing: ")
    filtered_tokens = [token for token in tokens if token not in string.punctuation]
    filtered_tokens = [token for token in filtered_tokens if token not in nltk.corpus.stopwords.words('english')]
    pprint.pprint(get_token_count(filtered_tokens)[:25])

    print_heading("Top lemmas: ")
    pprint.pprint(get_token_count(get_lemmas_from_tokens(filtered_tokens))[:25])

    print_heading("Top verbs: ")
    verbs = []
    for sentence in get_tags(txt):
        sentence_verbs = [word[0] for word in sentence if word[1].lower().startswith('vb')]
        for verb in sentence_verbs:
            verbs.append(verb)

    pprint.pprint(get_token_count(verbs)[:25])

    print_heading("Top entities: ")
    entities = get_entities(txt)
    entities_list = []
    for key, value in entities.items():
        entities_list.append(key)
    pprint.pprint(get_token_count(entities_list))

    # print(get_sentences(txt))
    # print(get_words(txt))
    # print(get_tags(txt))
    # print(get_lemmas(txt))
    # print(get_entities(txt))
    # pprint.pprint(get_sentiment(txt))


if __name__ == '__main__':
    main()
