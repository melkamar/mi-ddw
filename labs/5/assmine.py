# Lab #5 - Association Rules Mining
# Generating rules - only one item on the right side

from collections import Counter
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


def generate_rules(frequent_itemsets, supports, min_confidence):
    print(" .... ")


def main():
    df = pd.read_csv("./bank-data.csv")
    del df["id"]
    df["income"] = pd.cut(df["income"], 10)
    dataset = []
    for index, row in df.iterrows():
        row = [col + "=" + str(row[col]) for col in list(df)]
        dataset.append(row)
    frequent_itemsets, supports = apriori(dataset, 0.3)
    generate_rules(frequent_itemsets, supports, 0.5)

    # ...
    # {'car=YES'} => married=YES, 0.3233333333333333, 0.6554054054054054
    # ...
    # {'married=YES', 'save_act=YES'} => current_act=YES, 0.3433333333333333, 0.7436823104693141


if __name__ == '__main__':
    main()
