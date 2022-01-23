import pandas as pd
import numpy as np


class Wordle:

    def __init__(self, file="./data/5-latter words.csv", check_random=False):
        self.df = pd.read_csv(file)
        self.word = self.df.sample(1)['word'].values[0]
        self.try_ = 0
        self.max_try = round(1.25 * len(self.word))
        self.correct = 0
        self.check_random = check_random

    def guess(self, guess):

        error_message = ""
        if self._check_word_list(guess) and self.check_random:
            error_message += self._check_word_list(guess) + "\n"
        if self._check_length(guess):
            error_message += self._check_length(guess) + "\n"
        if error_message:
            return error_message

        # check number of try
        # if current try is not exceed and the answer is not correct
        if self.try_ + 1 < self.max_try and self.correct == 0:
            self.try_ += 1
            if self.word == guess:
                self.correct = 1
            return self.try_, self._check_guess(guess), guess
        # if current try is exceed, return the correct answer
        elif self.try_ + 1 == self.max_try and self.correct == 0:
            self.try_ += 1
            self.correct = 1
            print(f"the answer is {self.word}")
            guess = self.word
            return self.try_, self._check_guess(guess), guess
        else:
            return self.try_, self._check_guess(self.word), self.word

    def _check_word_list(self, guess):
        if guess not in list(self.df['word']):
            return f"{guess} is not in word list"

    def _check_length(self, guess):
        if len(guess) != len(self.word):
            return f"expected word length={len(self.word)}, but {guess}'s length is {len(guess)}"

    def _check_guess(self, guess):
        # mask used letters is a word
        word_letters = list(self.word)
        score = []

        for i in range(len(guess)):
            guess_letter = guess[i]
            s = 0
            # if the guess letter possifion is correct
            if guess_letter == self.word[i]:
                s = 2
                word_letters[i] = ''
                score.append(s)
                # skip to next guess letter
                continue
            # if the possition is wrong
            else:
                for j in range(len(self.word)):
                    # if there is a guess letter is unused
                    if guess_letter == word_letters[j]:
                        s = 1
                        word_letters[j] = ''
                        break
                score.append(s)
        return np.array(score)