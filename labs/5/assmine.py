# Lab #5 - Association Rules Mining
# Generating rules - only one item on the right side

from collections import Counter
from pprint import pprint
import itertools

import pandas as pd


def frequent_items(transactions, support):
    counter = Counter()
    for trans in transactions:
        counter.update(frozenset([t]) for t in trans)
    return set(item for item in counter if counter[item] / len(transactions) >= support), counter


def generate_candidates(L, k):
    candidates = set()
    for a in L:
        for b in L:
            union = a | b
            if len(union) == k and a != b:
                candidates.add(union)
    return candidates


def filter_candidates(transactions, itemsets, support):
    counter = Counter()
    for trans in transactions:
        subsets = [itemset for itemset in itemsets if itemset.issubset(trans)]
        counter.update(subsets)
    return set(item for item in counter if counter[item] / len(transactions) >= support), counter


def apriori(transactions, support):
    result = list()
    resultc = Counter()
    candidates, counter = frequent_items(transactions, support)
    result += candidates
    resultc += counter
    k = 2
    while candidates:
        candidates = generate_candidates(candidates, k)
        candidates, counter = filter_candidates(transactions, candidates, support)
        result += candidates
        resultc += counter
        k += 1
    resultc = {item: (resultc[item] / len(transactions)) for item in resultc}
    return result, resultc


def generate_left_and_right_sides(itemset: frozenset):
    itemlist = list(itemset)
    res = []
    for item in itemlist:
        newlist = list(itemlist)
        newlist.remove(item)
        res.append((newlist, item))
    return res


def generate_rules(frequent_itemsets, supports, min_confidence, sort_by_confidence=False):
    rules = []

    for itemset in frequent_itemsets:
        if len(itemset) < 2:
            continue

        for entry in generate_left_and_right_sides(itemset):
            left_side, right_side = entry
            rule_confidence = supports[itemset] / supports[frozenset(left_side)]
            if rule_confidence >= min_confidence:
                rules.append((left_side, right_side, rule_confidence))

    if sort_by_confidence:
        rules = sorted(rules, key=lambda rule: rule[2])

    for rule in rules:
        left_side = rule[0]
        right_side=rule[1]
        rule_confidence=rule[2]
        print(f"{left_side} => {right_side}: {rule_confidence}")

# pprint(supports)

def get_dataset_shopping():
    return [
        ['bread', 'milk'],
        ['bread', 'diaper', 'beer', 'egg'],
        ['milk', 'diaper', 'beer', 'cola'],
        ['bread', 'milk', 'diaper', 'beer'],
        ['bread', 'milk', 'diaper', 'cola'],
    ]


def get_dataset_bank():
    df = pd.read_csv("./bank-data.csv")
    del df["id"]
    df["income"] = pd.cut(df["income"], 10)
    dataset = []
    for index, row in df.iterrows():
        row = [col + "=" + str(row[col]) for col in list(df)]
        dataset.append(row)

    return dataset


def main():
    # dataset = get_dataset_shopping()
    dataset = get_dataset_bank()

    print(dataset)

    frequent_itemsets, supports = apriori(dataset, 0.3)
    generate_rules(frequent_itemsets, supports, 0.5, sort_by_confidence=True)

    # ...
    # {'car=YES'} => married=YES, 0.3233333333333333, 0.6554054054054054
    # ...
    # {'married=YES', 'save_act=YES'} => current_act=YES, 0.3433333333333333, 0.7436823104693141


if __name__ == '__main__':
    main()
