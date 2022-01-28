from turtle import pos
import numpy as np
import pandas as pd
import os

from .wordle import Wordle
import re

encoding_table = {'2': 'O', '1': '-', '0': 'X'}


def encode_score(score):
    score_str = "".join([str(i) for i in score])
    for key in list(encoding_table.keys()):
        score_str = re.sub(key, encoding_table[key], score_str)
    return score_str


def decode_score(score_str):
    score = []
    decode_table = dict()
    for key in encoding_table.keys():
        decode_table[encoding_table[key]] = key
    for s in score_str:
        score.append(int(decode_table[s]))
    return score


def get_score_matrix(wordle_file, score_file):

    df = pd.read_csv(wordle_file)

    vocab = list(df['word'])

    if not os.path.exists(score_file):
        score_matrix = []
        for ans in df['word']:

            # using function from wordle core
            wd = Wordle(wordle_file)

            # score for this ans
            score_arr = []
            for guess in df['word']:
                encoded_score = encode_score(wd.get_score(ans, guess), encoding_table)
                score_arr.append(encoded_score)
            score_matrix.append(score_arr)

        df = pd.DataFrame(columns=vocab, data=score_matrix)
        df.to_csv(score_file, index=False)

    df = pd.read_csv(score_file)

    return df


def filter_possible_words(score_df, prev_possible_index, guess, guess_result):
    # get score_df with prev_possible_index to create V(i-1)
    # V(i-1): vocab of previous turn
    # we make a guess turn i g(i) based on V(i-1)
    # and we get score i s(i)

    # filter V(i-1) based on g(i) and s(i)
    possible_df = score_df.loc[prev_possible_index]

    # filter new Vi
    possible_df = possible_df[possible_df[guess] == guess_result][guess]
    possible_words = list(score_df.columns[possible_df.index])

    return list(possible_df.index), possible_words


def expected_vocab_size(guess_df):
    # get guess seires i.e. df[guess]

    guess_outcomes_count = guess_df.value_counts()

    # calculate expected Vi size based on gi
    # size of V(i-1)
    prev_vocab_size = np.sum(guess_outcomes_count)
    prob_of_result = guess_outcomes_count / prev_vocab_size

    # Expected size of Vi
    expected_value = np.sum(guess_outcomes_count * prob_of_result)

    return np.round(expected_value, 1)


def find_best_guess(score_df, prev_possible_index, use_all_word=False):
    # base on current information V(i-1)
    # What is the best word g(i) to choose

    possible_df = score_df.loc[prev_possible_index]
    prev_vocab = list(score_df.columns[prev_possible_index])
    vocab_size = len(possible_df)

    if use_all_word == True:
        guess_vocab = list(score_df.columns)
    else:
        guess_vocab = prev_vocab

    best_expected_vocab_size = expected_vocab_size(possible_df[prev_vocab[0]])
    best_word = prev_vocab[0]

    if len(possible_df) > 1:
        for guess_word in guess_vocab:
            guess_val = expected_vocab_size(possible_df[guess_word])

            # guess by previous possible word
            if guess_val < best_expected_vocab_size and guess_word in list(prev_vocab):
                best_word = guess_word
                best_expected_vocab_size = guess_val
            elif guess_val < best_expected_vocab_size and use_all_word:
                best_word = guess_word
                best_expected_vocab_size = guess_val

        print(f"{best_word}: expected vocab size = {best_expected_vocab_size}")

    return best_word