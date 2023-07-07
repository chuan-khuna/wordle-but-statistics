from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
import pandas as pd

from .wordle_settings import *


class WordleGameLogicBase:

    def __init__(self, file: str, allow_random: bool = False, icon_score: bool = True) -> None:
        # common properties

        # game settings
        self.file = file
        self.allow_random = allow_random
        self.max_guess = 10
        self.icon_score = icon_score
        # game data
        self.df = pd.DataFrame({'word': ['wordle_base_class']})
        self.ans = self._sample_word()
        # game state
        self.num_guess = 0

        self.help = self.__help()

    def __help(self) -> str:
        help_message = f"""
        {ICONS[CORRECT]}|{CORRECT} = Correct
        {ICONS[WRONG_PLACE]}|{WRONG_PLACE} = Contain but wrong place
        {ICONS[NOT_CONTAIN]}|{NOT_CONTAIN} = Not contain
        {ICONS[DONT_CARE]}|{DONT_CARE} = Don't care
        """
        return help_message

    # To call this double underscore method in child class
    # self._ParentClass__method_name
    def __generate_letters_count(self, word: str) -> Dict[str, int]:
        quota = {}
        for char in word:
            if char not in quota:
                quota[char] = 1
            else:
                quota[char] += 1
        return quota

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

    @abstractmethod
    def _sample_word(self):
        # sampling word from df
        return list(self.df['word'].sample(1))[0]

    @abstractmethod
    def reset(self):
        self.ans = self._sample_word()
        self.num_guess = 0

    @abstractmethod
    def compute_score(self, guess: str, ans: str) -> str:
        pass

    @abstractmethod
    def guess(self, word: str) -> Tuple[int, str | None]:
        pass