import argparse

import jsonlines
import math

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("part")
    args = argparser.parse_args()

    with jsonlines.open("data/temp.jsonlines", mode="a") as outf:
        with jsonlines.open("data/dutch_train.jsonlines", mode="r") as inf:
            docs = [doc for doc in inf]
            for doc in docs[:math.trunc(args.part * len(docs))]:
                outf.write(doc)
