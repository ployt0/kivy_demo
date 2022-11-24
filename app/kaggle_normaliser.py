#!/usr/bin/env python3
"""
The quotes are on trend, but hideously malformed.

https://www.gutenberg.org/files/48105/ should be considered, it's probably more inspiring.

cd C:/Users/demo/PycharmProjects/kivy_demo
python app/kaggle_normaliser.py C:/Users/demo/PycharmProjects/kivy_demo/quotes.json
"""
import csv
import json
import re
import sys
from functools import partial
from random import random
from typing import Callable

from console_io import Getch


Decider = Callable[[str, int, int, list[str]], int]


class UserEscape(Exception):
    pass


def get_output_name(src_name: str) -> str:
    pre_prefix = ".".join(src_name.split(".")[:-1])
    return pre_prefix + "_slimmed.json"


def main(method: str, file_nm: str):
    uniq_quotes = load_json(file_nm)
    print("Ctrl-C will update your progress and quit.")
    accepted_methods = ["all", "random", "csv"]
    if method == "all":
        iterate_through_quotes(uniq_quotes, file_nm, key_decider)
    elif method.startswith("random"):
        count = int(method[6:])
        sample_quotes(uniq_quotes, file_nm, count)
    elif method.startswith("csv"):
        csv_all_quotes(uniq_quotes, file_nm)
    else:
        print(f"{method} was not recognised. Please use one of: {accepted_methods}")


def save_json(out_name: str, quote_dict: [str, str]):
    with open(out_name, "w", encoding="utf8") as f:
        json.dump(quote_dict, f, ensure_ascii=False)
    print(f"Saved {len(quote_dict)} quotes.")


def get_case_bump(unfiltered):
    matches = re.findall("[a-z][A-Z]", unfiltered)
    return matches


def word_normaliser(bumpy_match: re.Match, decider: Decider, whole_quote: str) -> str:
    """
    Takes a match for a word with a central capital and normalises it.

    Maintains a list of allowable cases.

    Prompts user, no prompts *decider*, to choose replacement.

    :param bumpy_match: regex match for word harbouring the capital.
    :param decider: selects one of our (five) solutions via callback.
    :param whole_quote: used to describe the changes proposed.
    :return: fixed word.
    """
    bumpy_word = bumpy_match.group()
    if bumpy_word in {"eBay", "iPhone", "iPhones"}:  # , "WorldFest"}:
        return bumpy_word
    matches = [{"match": x} for x in re.finditer("[a-z][A-Z]", bumpy_word)]
    # Need to insert a space, or comma or stop. To automate we might choose a comma.
    for match_dct in matches:
        regs = match_dct["match"].regs[0]
        cap_char = bumpy_word[regs[1] - 1]
        options = get_options(cap_char)
        match_dct["x"] = decider(
            whole_quote, regs[0] + bumpy_match.regs[0][0],
            regs[1] + bumpy_match.regs[0][0], options)
    # Now apply the choices in the reverse order to maintain the match indexes.
    for match_dct in matches[::-1]:
        regs = match_dct["match"].regs[0]
        cap_char = bumpy_word[regs[1] - 1]
        options = get_options(cap_char)
        lhs = bumpy_word[:regs[0] + 1]
        rhs = bumpy_word[regs[1]:]
        bumpy_word = lhs + options[match_dct["x"]] + rhs
    return bumpy_word


def get_options(cap_char):
    options = [
        f", {cap_char.lower()}",
        f". {cap_char}",
        f" {cap_char.lower()}",
        f" {cap_char}",
        f"{cap_char}"
    ]
    return options


def load_json(file_nm: str) -> dict[str, str]:
    with open(file_nm, encoding="utf8") as f:
        uniq_quotes = {x["Quote"]:x["Author"] for x in json.load(f)}
    return uniq_quotes


def iterate_through_quotes(uniq_quotes: dict[str, str], src_name: str, decider: Decider):
    pre_prefix = ".".join(src_name.split(".")[:-1])
    out_name = pre_prefix + "_slimmed.json"
    try:
        with open(out_name, encoding="utf8") as f:
            quote_list = json.load(f)
    except FileNotFoundError:
        quote_list = []
    quote_cnt = len(uniq_quotes)
    bar_len = 60
    try:
        for i, item in enumerate(uniq_quotes.items()):
            prcnt_done = i / float(quote_cnt)
            steps_done = int(prcnt_done * bar_len)
            steps_left = bar_len - steps_done
            sys.stdout.write(
                f'\r{int(prcnt_done * 100.0):>3}% [' + '█' * steps_done + ' ' * steps_left + '] ' + str(i))
            # Skip if we have already persisted this:
            if i < len(quote_list):
                continue
            add_quote(item[0], item[1], quote_list, decider)
    finally:
        save_json(out_name, quote_list)


def sample_quotes(uniq_quotes: dict[str, str], src_name: str, count: int):
    pre_prefix = ".".join(src_name.split(".")[:-1])
    out_name = pre_prefix + "_selection.json"
    quote_list = []
    quote_cnt = len(uniq_quotes)
    src_list = [(x[0], x[1]) for x in uniq_quotes.items()]
    done_indices = set()
    while len(quote_list) < count:
        i = int(random() * quote_cnt)
        # Skip if we have already persisted this:
        if i in done_indices:
            continue
        done_indices.add(i)
        quote_list.append((src_list[i][0], src_list[i][1]))
    save_json(out_name, quote_list)


def csv_all_quotes(uniq_quotes: dict[str, str], src_name: str):
    pre_prefix = ".".join(src_name.split(".")[:-1])
    out_name = pre_prefix + "_all.csv"
    with open(out_name, 'w') as f:
        employee_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for item in uniq_quotes.items():
            employee_writer.writerow(item)


def add_quote(quote: str, auth: str, quote_list: list, decider: Decider):
    camel_effect = get_case_bump(quote)
    normaliser = partial(word_normaliser, decider=decider, whole_quote=quote)
    if camel_effect:
        print()
        quote = re.sub("\\b\\w*[a-z]+[A-Z]+\\w*\\b", normaliser, quote)
        print(f"Reformed: {quote}")
    quote_list.append((quote, auth))


def key_decider(whole_quote: str, l_pos: int, r_pos: int, choices: list) -> int:
    print('"' + whole_quote + '"')
    print('  ' + ' ' * l_pos + '^')
    for i, ch in enumerate(choices):
        print(f" {i+1}. {whole_quote[max(0, l_pos-15):l_pos + 1]}{ch}{whole_quote[r_pos:r_pos + 15]}")
    ans = get_int_input(len(choices))
    return ans


def get_int_input(max_int):
    """
    Get's an int in the range [0-max_int]
    The user sees choices from 1, but we use computer array addressing with the return value.
    """
    getch = Getch()
    while True:
        gotch = getch()
        if gotch in [b"\x03", b"\x04", b"\x1a"]:
            # Ctrl-C,D,Z
            raise UserEscape
        try:
            gotch = gotch.decode()
        except UnicodeDecodeError as ex:
            continue
        print(gotch)
        try:
            goti = int(gotch)
            if goti in range(1, max_int + 1):
                return goti - 1
            print(f"Please enter 1..{max_int}")
        except ValueError as ex:
            pass


if __name__ == "__main__":
    main(*sys.argv[1:])


