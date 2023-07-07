import pandas as pd
from typing import List, Dict, Tuple

from .wordle_settings import *
from .wordle_base import WordleGameLogicBase


class Wordle(WordleGameLogicBase):

    def __init__(self, file: str, allow_random: bool = False, icon_score: bool = True) -> None:
        super.__init__(file, allow_random, icon_score)
        # game mechanic
        self.df = pd.read_csv(file).dropna().reset_index(drop=True)
        self.ans = self._sample_word()
        self.max_guess = round(1.5 * len(self.ans))
        self.help = self._WordleGameLogicBase__help()

    def reset(self):
        """Reset states of the wordle game
        - random new `ans` - target word
        - set `num_guess` to zero
        """
        self.ans = self._sample_word()
        self.num_guess = 0

    def _sample_word(self) -> str:
        return list(self.df['word'].sample(1))[0]

    def compute_score(self, guess: str, ans: str) -> str:
        letters_count = self._WordleGameLogicBase__generate_letters_count(ans)

        # initialise score
        score = [NOT_CONTAIN] * len(ans)

        # First priority:
        # Check if the letter is in the correct place
        for i, letter in enumerate(guess):
            if ans[i] == guess[i]:
                score[i] = CORRECT
                letters_count[letter] -= 1

        # When the GREEN guess is checked -> check ORANGE
        # check if the letter is in the ans
        for i, letter in enumerate(guess):
            if (score[i] == NOT_CONTAIN) and (letter in letters_count.keys()) and (
                    letters_count[letter] - 1 >= 0):
                # check if the letter in the guess isn't used exeed the limit
                letters_count[letter] -= 1
                score[i] = WRONG_PLACE

        return ''.join(score)

    def guess(self, word: str) -> Tuple[int, str | None]:
        is_correct_length = self._WordleGameLogicBase__validate_word_length(word)
        is_allowed = self._WordleGameLogicBase__validate_allowed(word)
        is_exceed = self._WordleGameLogicBase__validate_exceed()

        score = None

        pass_condition = is_correct_length & is_allowed
        if pass_condition:
            score = self.compute_score(word, self.ans)
            self.num_guess += 1

        score = self.iconise(score) if score and self.icon_score else score

        return self.num_guess, score
