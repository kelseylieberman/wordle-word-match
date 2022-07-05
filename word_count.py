"""
word_count.py

Description: Counts the number of valid wordle guesses complying to the filters provided
Author:      Kelsey Lieberman
Created:     05 July 2022

Example Usage: python -m word_count -l d -p 4
"""

import argparse
from typing import (
    List,
    Optional,
)

import requests


def cli() -> argparse.Namespace:
    """Parses CLI arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--letters",
        "-l",
        type=str,
        default=None,
        nargs="+",
        help="space-separated list of letters that must be included in wordle guess",
    )
    parser.add_argument(
        "--positions",
        "-p",
        nargs="+",
        type=int,
        default=None,
        help=(
            "space-separated list of respective positions of provided letters the must be in worlde guess. "
            + "If provided, each letter provided must have a corresponding position. Positions range 0-4 inclusive"
        ),
    )
    parser.add_argument(
        "--substrings",
        "-s",
        nargs="+",
        default=None,
        help="space-separated lits of substrings that the wordle guess must contain",
    )

    args = parser.parse_args()

    if args.letters is not None:
        if any(len(l) > 1 for l in args.letters):
            raise ValueError(
                "Each letter must be a single character. Letters must be separated by spaces"
            )

    if args.letters is not None and args.positions is not None:
        if len(args.letters) != len(args.positions):
            raise ValueError("A position must be provided for each letter")
        if len(set(args.positions)) != len(args.positions):
            raise ValueError("The same position cannot be provided twice")
        if any(p < 0 or p > 4 for p in args.positions):
            raise ValueError("Valid positions are 0, 1, 2, 3, or 4")

    elif args.positions is not None and args.letters is None:
        raise ValueError("A list of letters is required when using the --positions argument")

    if args.substrings is not None:
        if len(args.substrings) > 5:
            raise ValueError("A substring annot be longer than a valid wordle guess")

    return args


def match_letters(word: str, letters: Optional[List[str]], positions: Optional[List[int]]) -> bool:
    """Checks word for matching letters and positions if provided"""
    if letters is None:
        return True
    if positions is not None:
        return all(word[p] == l for l, p in zip(letters, positions))
    return all(l in word for l in letters)


def match_substrings(word, substrings: Optional[List[str]]) -> bool:
    if substrings is None:
        return True
    return all(substring in word for substring in substrings)


def main(args: argparse.Namespace) -> None:
    """Filter list of wordle guesses based on provided arguments"""
    letters: Optional[List[str]] = args.letters
    positions: Optional[List[int]] = args.positions
    substrings: Optional[List[str]] = args.substrings

    res = requests.get(
        "https://gist.githubusercontent.com/cfreshman/cdcdf777450c5b5301e439061d29694c/raw/b8375870720504ecf89c1970ea4532454f12de94/wordle-allowed-guesses.txt"
    )
    res.raise_for_status()
    words = res.text.split("\n")

    valid_words: List[str] = [
        word
        for word in words
        if match_letters(word, letters, positions) and match_substrings(word, substrings)
    ]

    matching_word_count = len(valid_words)
    print(f"MATCHING WORD COUNT: {matching_word_count}")


if __name__ == "__main__":
    main(cli())
