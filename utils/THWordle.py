import os
import numpy as np

import pythainlp

from .reverse_wordle import *

base_letters = pythainlp.thai_consonants + pythainlp.thai_lead_vowels + pythainlp.thai_follow_vowels + "ฤฦ"
lower_letters = pythainlp.thai_below_vowels
upper_letters = pythainlp.thai_above_vowels[:-1]
upper_mods = pythainlp.thai_tonemarks + "์" + "็"

allowed_letters = base_letters + lower_letters + upper_letters + upper_mods


def split_word_by_base(word):
    word_by_base = []

    for i, letter in enumerate(word):

        group = [''] * 4

        if letter in base_letters:
            group[0] = letter

            # serch for next non-base letters
            # group with this current letter
            j = i + 1
            if j >= len(word):
                next_letter = ''
            else:
                next_letter = word[j]
            while j < len(word) and next_letter not in base_letters:

                next_letter = word[j]

                if next_letter in lower_letters:
                    group[1] = next_letter
                if next_letter in upper_letters:
                    group[2] = next_letter
                if next_letter in upper_mods:
                    group[3] = next_letter
                j += 1

            word_by_base.append(group)

    return word_by_base


def pretty_print(word, print_split_word=True):
    print(f"word: {word}")
    print(f"length: {len(word)}")

    if print_split_word:
        split_word = split_word_by_base(word)
        text = ""
        for s in split_word:
            text += (''.join(s) + " ")
        print(f"split word by base: {text}")
        print(f"base length: {len(split_word)}")


def get_th_score_matrix(vocab_df, score_file):

    vocab = list(vocab_df['word'])

    if not os.path.exists(score_file):
        score_matrix = []
        for ans in vocab_df['word']:

            # using function from wordle core
            wd = THWordle(vocab_df)

            # score for this ans
            score_arr = []
            for guess in vocab_df['word']:
                encoded_score = encode_score([j for i in wd.get_score(ans, guess) for j in i])
                score_arr.append(encoded_score)
            score_matrix.append(score_arr)

        df = pd.DataFrame(columns=vocab, data=score_matrix)
        df.to_csv(score_file, index=False)

    df = pd.read_csv(score_file)

    return df


class THWordle:

    def __init__(self, df, allow_random=False):
        self.df = df
        self.ans = self.df.sample(1)['word'].values[0]

        self.current_guess = 0
        self.max_guess = round(1.25 * len(split_word_by_base(self.ans)))
        self.allow_random = allow_random

    def guess(self, guess):
        status = self.check_word_length(guess) & self.check_word_in_dictionary(guess)

        ans_length = len(split_word_by_base(self.ans))

        if status:
            # calculate score
            self.current_guess += 1
            score = self.get_score(self.ans, guess)
            score_normalised = self.get_normalised_score(score)
            hint = self.get_hint(self.ans, guess, score)
        else:
            # do nothing // print
            score = np.array([0] * ans_length, dtype=np.int)
            score_normalised = np.array([0] * ans_length, dtype=np.int)
            hint = []
            pass

        ans = "-" * ans_length
        if self.current_guess > self.max_guess:
            ans = self.ans

        guess_result = {
            "status": status,
            "#guess": self.current_guess,
            "max #guess": self.max_guess,
            "guessed word": guess,
            "score": score,
            "base score": score_normalised,
            "hint": hint,
            "ans": ans
        }

        return guess_result

    def get_score(self, ans, guess):
        ans_split = split_word_by_base(ans)
        guess_split = split_word_by_base(guess)

        # amount of letters in ans
        ans_letters = {}
        for group in ans_split:
            for letter in group:
                if letter in ans_letters.keys() and letter != '':
                    ans_letters[letter] += 1
                elif letter not in ans_letters.keys() and letter != '':
                    ans_letters[letter] = 1

        score = []
        for i, group in enumerate(guess_split):
            group_score = []
            for j, letter in enumerate(group):
                if letter == ans_split[i][j] and letter != '':
                    group_score.append(2)
                    ans_letters[letter] -= 1
                elif  letter == ans_split[i][j] and letter == '':
                    group_score.append(2)
                else:
                    group_score.append(0)
            score.append(group_score)
 
        for i, group in enumerate(guess_split):
            for j, letter in enumerate(group):
                if score[i][j] == 0 and letter in ans_letters.keys():
                    if ans_letters[letter] - 1 >= 0:
                        ans_letters[letter] -= 1
                        score[i][j] = 1
        return np.array(score, dtype=np.int)

    def get_normalised_score(self, score):
        return np.array(score)[:, 0]

    def get_hint(self, ans, guess, score):
        ans_split = split_word_by_base(ans)
        guess_split = split_word_by_base(guess)
        normalised_score = self.get_normalised_score(score)

        # create base dictionary
        base_dict = {}
        for group in ans_split:
            if group[0] in base_dict.keys():
                base_dict[group[0]].append("".join(group))
            else:
                base_dict[group[0]] = ["".join(group)]

        hints = []
        for i, s in enumerate(normalised_score):
            if s >= 1:
                hint_key = guess_split[i][0]
                rand_hint = np.random.choice(base_dict[hint_key])
                hints.append(rand_hint)
        return hints


    def check_word_length(self, guess):
        guess_length = len(split_word_by_base(guess))
        ans_length = len(split_word_by_base(self.ans))

        if guess_length == ans_length:
            return True
        else:
            print(f"Guessed word '{guess}' length is not equal to {ans_length}.")
            return False

    def check_word_in_dictionary(self, guess):
        if guess in list(self.df['word']) or self.allow_random:
            return True
        else:
            print("Guessed word in not in dictionary.")
            return False