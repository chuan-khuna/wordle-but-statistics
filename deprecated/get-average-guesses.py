import pandas as pd
import numpy as np

import re

from utils.wordle import Wordle
from utils.reverse_wordle import *

import os

from multiprocessing import Pool

# Wordle Game Setting
n_letter = 5
wordle_file = f"./data/common {n_letter}-letter words.csv"
wddf = pd.read_csv(wordle_file)
wddf = wddf.dropna()

score_file = f"./guess score matrix {n_letter}-letter words.csv"
vocab = list(wddf['word'])
df = get_score_matrix(wordle_file, score_file)

n_try = 5000


def random_method(ans):

    # fixed answer
    wd = Wordle(wordle_file)
    wd.ans = ans

    guess = None
    correct = False
    n = 0
    possible_ind = range(len(df))

    # play wordle
    while not (correct):
        # guess turn i
        n += 1
        if guess == None:
            guess = np.random.choice(vocab, 1)[0]
        else:
            guess = np.random.choice(possible_words, 1)[0]

        wd_result = wd.guess(guess)
        guess_result = encode_score(wd_result['score'])

        possible_ind, possible_words = filter_possible_words(df, possible_ind, guess, guess_result)
        correct = (wd_result['score'] == 2).all()

    return n


def minimise_vocab_size_method(ans):

    wd = Wordle(wordle_file)
    wd.ans = ans

    guess = None
    correct = False
    n = 0
    possible_ind = range(len(df))

    while not (correct):
        n += 1
        if guess == None:
            guess = find_best_guess(df, range(len(vocab)), use_all_word=True, verbose=False)
        else:
            guess = find_best_guess(df, possible_ind, use_all_word=True, verbose=False)

        wd_result = wd.guess(guess)
        guess_result = encode_score(wd_result['score'])

        possible_ind, possible_words = filter_possible_words(df, possible_ind, guess, guess_result)
        correct = (wd_result['score'] == 2).all()

    return n



if __name__ == '__main__':
    answers = np.random.choice(vocab, n_try)

    with Pool(5) as p:
        random_guess_numbers = p.map(random_method, answers)
        
    with Pool(5) as p:
        minimise_vocab_guess_numbers = p.map(minimise_vocab_size_method, answers)


    df = pd.DataFrame({
        'answer': answers,
        'random_guesses': random_guess_numbers,
        'minimise_vocab_guesses': minimise_vocab_guess_numbers
    })

    df.to_csv("guesses-count.csv", index=False)