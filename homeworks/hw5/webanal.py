import pandas


def read_dataset(filename):
    df = pandas.read_csv(filename)
    # del df["id"]
    # df["income"] = pd.cut(df["income"], 10)
    dataset = []
    for index, row in df.iterrows():
        row = [col + "=" + str(row[col]) for col in list(df)]
        dataset.append(row)

    return dataset

def main():
    dataset = read_dataset('data/visitors.csv')

if __name__ == '__main__':
    main()