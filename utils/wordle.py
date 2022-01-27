import numpy as np
import pandas as pd


class Wordle:

    def __init__(self, file, allow_random=False):
        self.df = pd.read_csv(file)
        self.ans = self.df.sample(1)['word'].values[0]

        self.current_guess = 0
        self.max_guess = round(1.25 * len(self.ans))
        self.allow_random = allow_random

    def guess(self, guess):
        # return  is_pass, current_guess, score

        status = self.check_word_length(guess) & self.check_word_in_dictionary(guess)

        if status:
            score = np.array(self.get_score(self.ans, guess), dtype=np.int)
            self.current_guess += 1
        else:
            score = np.array([0] * len(self.ans), dtype=np.int)

        ans = '-' * len(self.ans)
        if self.current_guess > self.max_guess:
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

    def check_word_in_dictionary(self, guess):
        if guess in list(self.df['word']) or self.allow_random:
            return True
        else:
            print("Guessed word in not in dictionary.")
            return False