# https://github.com/narze/thwordle/blob/main/src/lib/Wordle.ts

import pythainlp
from typing import List

base_letters = pythainlp.thai_consonants + pythainlp.thai_lead_vowels + pythainlp.thai_follow_vowels + "ฤฦ"
below_letters = pythainlp.thai_below_vowels
above_letters = pythainlp.thai_above_vowels[:-1]
mods = pythainlp.thai_tonemarks + "์" + "็"

letter_groups = {1: below_letters, 2: above_letters, 3: mods}

allowed_letters = base_letters + below_letters + above_letters + mods


def split_word(word: str) -> List[List[str]]:
    word_by_base = []

    i = 0
    while i < len(word):
        # base, below, above, mod
        base = [''] * 4
        base[0] = word[i]

        # check next letters
        # until a base letter is found
        j = i + 1
        while j < len(word):
            if word[j] in base_letters:
                break

            # loop through all non-base types
            for k, v in letter_groups.items():
                if word[j] in v:
                    base[k] = word[j]

            j += 1

        word_by_base.append(base)

        # skip to next base character
        i = j

    return word_by_base


def pretty_print_th(word, print_split_word=True):
    print(f"word: {word}")
    print(f"length: {len(word)}")

    if print_split_word:
        word = split_word(word)
        text = ""
        for s in word:
            text += (''.join(s) + " ")
        print(f"split word: {text}")
        print(f"base length: {len(word)}")