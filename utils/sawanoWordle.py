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