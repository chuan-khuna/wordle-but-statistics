import pandas as pd
from typing import List, Dict, Tuple

from .wordle_settings import *


class Wordle:

    def __init__(self, file: str, allow_random: bool = False, icon_score: bool = True) -> None:

        # game mechanic
        self.df = pd.read_csv(file).dropna().reset_index(drop=True)
        self.ans = self._sample_word()
        self.max_guess = round(1.5 * len(self.ans))
        self.help = self.__help()
        self.allow_random = allow_random
        self.icon_score = icon_score

        # game state
        self.num_guess = 0

    def reset(self):
        """Reset states of the wordle game
        - random new `ans` - target word
        - set `num_guess` to zero
        """
        self.ans = self._sample_word()
        self.num_guess = 0

    def __help(self) -> str:
        help_message = f"""
        {ICONS[CORRECT]}|{CORRECT} = Correct
        {ICONS[WRONG_PLACE]}|{WRONG_PLACE} = Contain but wrong place
        {ICONS[NOT_CONTAIN]}|{NOT_CONTAIN} = Not contain
        {ICONS[DONT_CARE]}|{DONT_CARE} = Don't care
        """
        return help_message

    def _sample_word(self) -> str:
        return list(self.df['word'].sample(1))[0]

    def __generate_letters_count(self, word: str) -> Dict[str, int]:
        quota = {}
        for char in word:
            if char not in quota:
                quota[char] = 1
            else:
                quota[char] += 1
        return quota

    def iconise(self, score: str) -> str:
        """Iconise the plain text score to colour icons

        Args:
            score (str): _description_

        Returns:
            str: _description_
        """
        icon_score = ""
        for s in score:
            icon_score += ICONS[s]
        return icon_score

    iconize = iconise

    def compute_score(self, guess: str, ans: str) -> str:
        letters_count = self.__generate_letters_count(ans)

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

    def __validate_word_length(self, word: str) -> bool:
        if len(word) != len(self.ans):
            print(
                f"The length of {word} ({len(word)}) != the length of the answer ({len(self.ans)})")
        return len(word) == len(self.ans)

    def __validate_allowed(self, word: str) -> bool:
        if (word not in list(self.df['word'])) and (not self.allow_random):
            print("Random guessing is not allowed")

        # allow random = True -> don't care about the guess
        # allow random = False -> the guess matters
        return (word in list(self.df['word'])) or (self.allow_random)

    def __validate_exceed(self) -> bool:
        if self.num_guess >= self.max_guess:
            print(f"Max retries ({self.max_guess}) exceeded")
        return self.num_guess < self.max_guess

    def guess(self, word: str) -> Tuple[int, str | None]:
        is_correct_length = self.__validate_word_length(word)
        is_allowed = self.__validate_allowed(word)
        is_exceed = self.__validate_exceed()

        score = None

        pass_condition = is_correct_length & is_allowed
        if pass_condition:
            score = self.compute_score(word, self.ans)
            self.num_guess += 1

        score = self.iconise(score) if score and self.icon_score else score

        return self.num_guess, score
