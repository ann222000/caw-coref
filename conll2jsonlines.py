import spacy_udpipe
import jsonlines
import os

DATA_DIR = "dutch_data"

if __name__ == "__main__":
    with jsonlines.open("data/dutch.jsonlines", mode="w") as outf:
        nlp = spacy_udpipe.load_from_path("nl", path='dutch-alpino-ud-2.5-191206.udpipe')
        for file_conll in os.listdir(os.path.join(DATA_DIR, "conll_files")):
            doc = {"document_id": "nw/" + file_conll[:-5],
                   "cased_words": [],
                   "pos": [],
                   "head_word": [],
                   "head": [],
                   "sent_id": [],
                   "clusters": [],
                   "speaker": []}
            sentence = -1
            with open(os.path.join(DATA_DIR, 'conll_files', file_conll)) as inf:
                text = ""
                cluster_labels = []
                for line in inf.readlines():
                    if line == "\n":
                        sentence += 1
                    elif not line.startswith("#begin") and not line.startswith("#end"):
                        word, tag = line.split('\t')[2:4]
                        text = text + " " + word
                        cluster_labels.append(tag)
                        doc["cased_words"].append(word)
                        doc["sent_id"].append(sentence)
                        doc["speaker"].append("Someone")

            tokens = nlp(text)
            for token, word in zip(tokens, doc["cased_words"]):
                if str(token) != word:
                    print(file_conll, token, word)
            for token in tokens:
                pos = token.pos_
                doc["pos"].append("CC" if pos == "CCONJ" else pos)
                head = token.head
                # if doc["document_id"] == "ParlaMint-NL_2018-12-11-tweedekamer-3." and str(token) in ['het', 'Amsterdam', 'Medisch', 'Centrum']:
                #     print(token, head)
                doc["head_word"].append(None if head == token else str(head))
            print(len(doc["cased_words"]), len(doc["pos"]), len(doc["head_word"]))
            clusters_dict = {}
            cur_span = 0
            # Clusters. Possible cases (num) (num num) - out of span or in span
            possible_heads_dict = {}
            # possible_heads_dict = {token: [head1, head2, ...]} headi - all tokens in its span except token
            for word_number, word in enumerate(cluster_labels):
                # if doc["document_id"] == 'ParlaMint-NL_2017-12-19-tweedekamer-4.' and word_number in range(1400, 1500):
                #     print(doc["cased_words"][word_number], word_number, word)
                if word[0] == '(' and word.endswith(")\n"):
                    if word[1:-2] in clusters_dict.keys():
                        clusters_dict[word[1:-2]].append([word_number, word_number + 1])
                    else:
                        clusters_dict[word[1:-2]] = [[word_number, word_number + 1]]
                    possible_heads_dict[word_number] = ["null"]
                elif word[0] == '(':
                    cur_span = word[1:-1]
                    if cur_span in clusters_dict.keys():
                        clusters_dict[cur_span].append([word_number])
                    else:
                        clusters_dict[cur_span] = [[word_number]]
                elif word[-2] == ')':
                    clusters_dict[word[:-2]][-1].append(word_number + 1)
                    cur_span = 0
                    for token in clusters_dict[word[:-2]][-1]:
                        possible_heads_dict[token] = [head for head in clusters_dict[word[:-2]][-1] if
                                                      token != head]
                else:
                    continue
            # Head
            for word_number, head_word in enumerate(doc["head_word"]):
                head = None
                if head_word:
                    # word in any coref span
                    # if word_number in possible_heads_dict.keys():
                    #     if possible_heads_dict[word_number] == ["null"]:
                    #          doc["head"].append(None)
                    #     else:
                    #         possible_head_words = {doc["cased_words"][word_n]: word_n for word_n in
                    #                                    possible_heads_dict[word_number]}
                    #         if doc["head_word"][word_number] in possible_head_words.keys():
                    #             doc["head"].append(possible_head_words[doc["head_word"][word_number]])
                    #         else:
                    #             doc["head"].append(max(possible_heads_dict[word_number]))
                    #         # word not in coref span
                    # else:
                    for i in range(1, 15):
                        if head_word == doc["cased_words"][min(word_number + i, len(doc["head_word"]) - 1)]:
                            head = min(word_number + i, len(doc["head_word"]) - 1)
                            break
                        elif head_word == doc["cased_words"][max(word_number - i, 0)]:
                            head = max(word_number - i, 0)
                            break
                doc["head"].append(head)
            doc["clusters"] = [cluster for cluster in clusters_dict.values()]
            # if doc["document_id"] == 'ParlaMint-NL_2017-12-19-tweedekamer-4.':
            #     outf.write(doc)
            #     exit(0)
            # del doc["head_word"]
            outf.write(doc)
    with jsonlines.open("data/dutch.jsonlines", mode="r") as inf:
        docs = [doc for doc in inf]
        with jsonlines.open("data/dutch_train.jsonlines", mode="w") as outf:
            for doc in docs[:60]:
                outf.write(doc)
        with jsonlines.open("data/dutch_development.jsonlines", mode="w") as outf:
            for doc in docs[60:67]:
                outf.write(doc)
        with jsonlines.open("data/dutch_test.jsonlines", mode="w") as outf:
            for doc in docs[67:]:
                outf.write(doc)
