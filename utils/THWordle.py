from jupyterlab_server import WORKSPACE_EXTENSION
import numpy as np

import pythainlp

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