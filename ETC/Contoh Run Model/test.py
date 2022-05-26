import os
import sys
os.environ['CHAINER_SEED'] = '0'
import random
random.seed(0)
import numpy as np
np.random.seed(0)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pickle

import chainer.functions as F
from chainer import iterators
from chainer import cuda
from chainer import serializers

# from src.model.layered_model import Model, Evaluator, Updater
from server.models.utils.layered_model import Model
from server.models.utils.loader import update_tag_scheme, parse_config
from server.models.utils.loader import prepare_dataset


def predict(data_iter, model, mode):
    """
    Iterate data with well - trained model
    """
    for batch in data_iter:
        raw_words = [x['str_words'] for x in batch]
        words = [model.xp.array(x['words']).astype('i') for x in batch]
        chars = [model.xp.array(y).astype('i') for x in batch for y in x['chars']]
        tags = model.xp.vstack([model.xp.array(x['tags']).astype('i') for x in batch])

        # Init index to keep track of words
        index_start = model.xp.arange(F.hstack(words).shape[0])
        index_end = index_start + 1
        index = model.xp.column_stack((index_start, index_end))

        # Maximum number of hidden layers = maximum nested level + 1
        max_depth = len(batch[0]['tags'][0])
        sentence_len = np.array([x.shape[0] for x in words])
        section = np.cumsum(sentence_len[:-1])
        predicts_depths = model.xp.empty((0, int(model.xp.sum(sentence_len)))).astype('i')

        for depth in range(max_depth):
            next, index, extend_predicts, words, chars = model.predict(chars, words, tags[:, depth], index, mode)
            predicts_depths = model.xp.vstack((predicts_depths, extend_predicts))
            if not next:
                break

        predicts_depths = model.xp.split(predicts_depths, section, axis=1)
        ts_depths = model.xp.split(model.xp.transpose(tags), section, axis=1)
        yield ts_depths, predicts_depths, raw_words


def load_mappings(mappings_path):
    """
    Load mappings of:
      + id_to_word
      + id_to_tag
      + id_to_char
    """
    with open(mappings_path, 'rb') as f:
        mappings = pickle.load(f)
        id_to_word = mappings['id_to_word']
        id_to_char = mappings['id_to_char']
        id_to_tag = mappings['id_to_tag']

    return id_to_word, id_to_char, id_to_tag

def collect_entity(lst):
    """
    Collect predicted tags(e.g. BIO)
    in order to get entities including nested ones
    """
    entities = []
    for itemlst in lst:
        for i, tag in enumerate(itemlst):
            if tag.split('-', 1)[0] == 'B':
                entities.append([i, i + 1, tag.split('-', 1)[1]])
            elif tag.split('-', 1)[0] == 'I':
                entities[-1][1] += 1

    entities = remove_dul(entities)

    return entities

def remove_dul(entitylst):
    """
    Remove duplicate entities in one sequence.
    """
    entitylst = [tuple(entity) for entity in entitylst]
    entitylst = set(entitylst)
    entitylst = [list(entity) for entity in entitylst]

    return entitylst

def main(config_path, path_model, path_mapping, inputKalimat, mode = 0 ):
    args = parse_config(config_path)

    # Load sentences
    # symbols = ",'!#$%&()*+-/:;<=>?@[\]^_`{|}~\n"
    s = []
    sentences = inputKalimat
    sentences.lower()
    
    # print(sentences)
    sentences = sentences.split(".")
    # for i in symbols:
    #     sentences = np.char.replace(sentences, i, ' ' + i )
    for sentence in sentences:
        if sentence != '':
            sentence = sentence.split(" ")
            for word in sentence:
                if word != '':
                    s.append([word,'O','O','O','O','O'])
            s.append([".",'O','O','O','O','O'])
    test_sentences = [] 
    test_sentences.append(s)
    # print(test_sentences)
    # Update tagging scheme (IOB/IOBES)
    update_tag_scheme(test_sentences, args["tag_scheme"])

    # Load mappings from disk
    id_to_word, id_to_char, id_to_tag = load_mappings(path_mapping)
    word_to_id = {v: k for k, v in id_to_word.items()}
    char_to_id = {v: k for k, v in id_to_char.items()}
    tag_to_id  = {v: k for k, v in id_to_tag.items()}

    # Index data
    test_data = prepare_dataset(test_sentences, word_to_id, char_to_id, tag_to_id, None, args["lowercase"])
    # print(test_data)
    test_iter = iterators.SerialIterator(test_data, args["batch_size"], repeat=False, shuffle=False)

    model = Model(len(word_to_id), len(char_to_id), len(tag_to_id), args)

    serializers.load_npz(path_model, model)

    model.id_to_tag = id_to_tag
    model.parameters = args

    device = args['gpus']
    if device['main'] >= 0:
        cuda.get_device_from_id(device['main']).use()
        model.to_gpu()

    pred_tags = []
    gold_tags = []
    words = []

    # Collect predictions
    for ts, ys, xs in predict(test_iter, model, args['mode']):
        gold_tags.extend(ts)
        pred_tags.extend(ys)
        words.extend(xs)

    y_preds = pred_tags
    list_hasil = []
    if mode == 0:
        for i, se in enumerate(words):
            p_tags = [[id_to_tag[int(y)] for y in y_pred] for y_pred in y_preds[i]]
            p_entities = collect_entity(p_tags)
            for entity in p_entities:
                kata = ""
                for i in range(entity[0],entity[1]):
                    kata += se[i] + " " 
                list_hasil.append(
                    {
                            "kata" : kata,
                            "entity" : entity[2]
                    }
                )
    else:
        list_hasil = []
        for i, se in enumerate(words):
            p_tags = [[id_to_tag[int(y)] for y in y_pred] for y_pred in y_preds[i]]
            p_entities = collect_entity(p_tags)
            for entity in p_entities:
                index_awal = 0
                index_akhir = 0
                for i in range(0, entity[0]):
                    index_awal += len(se[i])
                    index_awal += 1
                    # print(se[i])
                    # for j in symbols:
                    #     if (j == se[i]) :
                    #         index_awal = 1
                kata = ""
                for i in range(entity[0],entity[1]):
                    kata += se[i] + " " 
                    index_akhir += len(se[i]) + 1
                list_hasil.append(
                    {
                        "index_awal" : index_awal,
                        "index_akhir" : index_akhir - 1 + index_awal,
                        "kata" : kata,
                        "entity" : entity[2]
                    }
                )
    # newlist = sorted(list_hasil, key=lambda x: len(list_hasil.entity), reverse=True)
    # print(newlist)
    return list_hasil
    # print(list_hasil)


# if __name__ == '__main__':
#     sentences = "two cdna clones were sequenced and provided 0,000 nucleotides (nt) of dna sequence information. there is a single methionine codon-initiated open reading frame of 0,000 nt in frame with a homeobox and a cax repeat, and the open reading frame is predicted to encode a protein of 00,000 daltons."
#     main('../src/config', sentences)
