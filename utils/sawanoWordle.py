from calendar import c
import string
import numpy as np
import pandas as pd
from nltk.tokenize.util import is_cjk

# list of characters that most people can type
typeable = list(string.printable)


def count_cjk(text):
    cnt = 0
    for c in text:
        if is_cjk(c):
            cnt += 1
    return cnt


def count_num(text):
    cnt = 0
    for c in text:
        if c in "0123456789":
            cnt += 1
    return cnt


def count_space(text):
    cnt = 0
    for c in text:
        if c == " ":
            cnt += 1
    return cnt


class SWordle:

    def __init__(self, df):
        self.df = df
        self.ans = self.df.sample(1)['track_name'].values[0]

        self.current_guess = 0
        self.max_guess = round(1.25 * len(self.ans))

        # finding non type able from data set
        self.non_typeable = ""
        for track in df['track_name']:
            for c in track:
                if c not in typeable and c not in self.non_typeable:
                    self.non_typeable += c

        self.non_typeable_hint = self.get_non_typeable_hint()

    def get_non_typeable_hint(self):
        ans_non_typeable = ""
        for c in self.ans:
            if c not in typeable and c not in ans_non_typeable:
                ans_non_typeable += c
        ans_non_typeable = list(ans_non_typeable)

        amount = np.clip(15, len(ans_non_typeable), len(self.non_typeable) // 2)

        hint_non_typeable = np.random.choice(list(self.non_typeable), amount, replace=False).tolist()
        hint = ans_non_typeable + hint_non_typeable
        np.random.shuffle(hint)

        return hint

    def get_hint(self):
        hint = {
            "total length": len(self.ans),
            "cjk": count_cjk(self.ans),
            "num": count_num(self.ans),
            "space": count_space(self.ans),
            "non_typeable": " ".join(self.non_typeable_hint)
        }

        return hint

    def guess(self, guess):
        status = self.check_word_length(guess)

        if status:
            score = np.array(self.get_score(self.ans, guess), dtype=np.int)
            self.current_guess += 1
        else:
            score = np.array([0] * len(self.ans), dtype=np.int)

        ans = '-' * len(self.ans)
        if self.current_guess > self.max_guess or (score == 2).all():
            ans = self.ans

        guess_result = {
            'status': status,
            '#guess': self.current_guess,
            'max #guess': self.max_guess,
            'guessed word': guess,
            'score': score,
            'answer': ans
        }

        return guess_result

    def get_score(self, ans, guess):
        ans = ans.lower()
        guess = guess.lower()

        # amount of letters in ans
        ans_letters = {}
        for letter in ans:
            if letter in ans_letters.keys():
                ans_letters[letter] += 1
            else:
                ans_letters[letter] = 1

        score = []
        # check if letters are in the correct position
        for i, letter in enumerate(guess):
            if letter == ans[i]:
                score.append(2)
                ans_letters[letter] -= 1
            else:
                score.append(0)

        # check if letters in guess are not used, score = 1
        # if it is used exceed the limit, score = 0
        for i, letter in enumerate(guess):
            if score[i] == 0 and letter in ans_letters.keys():
                if ans_letters[letter] - 1 >= 0:
                    ans_letters[letter] -= 1
                    score[i] = 1

        return score

    def check_word_length(self, guess):
        if len(guess) == len(self.ans):
            return True
        else:
            print(f"Guessed word length is not equal to {len(self.ans)}.")
            return False
