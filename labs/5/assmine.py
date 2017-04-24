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


def generate_rules(frequent_itemsets, supports, min_confidence, sort_by_confidence=False, metric="confidence"):
    rules = []

    for itemset in frequent_itemsets:
        if len(itemset) < 2:
            continue

        for entry in generate_left_and_right_sides(itemset):
            left_side, right_side = entry
            if metric == "confidence":
                rule_confidence = supports[itemset] / supports[frozenset(left_side)]
            elif metric == "lift":
                rule_confidence = supports[itemset] / (supports[frozenset(left_side)] * supports[frozenset([right_side])])
            elif metric == "conviction":
                denominator = 1-supports[itemset] / supports[frozenset(left_side)]
                if denominator:
                    rule_confidence = (1-supports[frozenset([right_side])]) / (denominator)
                else:
                    rule_confidence = 0
            else:
                raise ValueError("Metric must be confidence or lift or conviction.")
            if rule_confidence >= min_confidence:
                rules.append((left_side, right_side, rule_confidence))

    if sort_by_confidence:
        rules = sorted(rules, key=lambda rule: rule[2], reverse=True)

    for rule in rules[:100]:
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


def get_dataset_uci(filename):
    df = pd.read_csv(filename)
    # del df["id"]
    # df["income"] = pd.cut(df["income"], 10)
    dataset = []
    for index, row in df.iterrows():
        row = [col + "=" + str(row[col]) for col in list(df)]
        dataset.append(row)

    return dataset


def main():
    # dataset = get_dataset_shopping()
    # dataset = get_dataset_uci("./bank-data.csv")
    dataset = get_dataset_uci("./zoo.csv")

    # print(dataset)

    frequent_itemsets, supports = apriori(dataset, 0.3)
    print("="*120)
    print("CONFIDENCE:")
    generate_rules(frequent_itemsets, supports, 0.7, sort_by_confidence=True, metric="confidence")
    print("="*120)
    print("LIFT:")
    generate_rules(frequent_itemsets, supports, 1.03, sort_by_confidence=True, metric="lift")
    print("="*120)
    print("CONVICTION:")
    generate_rules(frequent_itemsets, supports, 1.1, sort_by_confidence=True, metric="conviction")

    # ...
    # {'car=YES'} => married=YES, 0.3233333333333333, 0.6554054054054054
    # ...
    # {'married=YES', 'save_act=YES'} => current_act=YES, 0.3433333333333333, 0.7436823104693141


if __name__ == '__main__':
    main()
