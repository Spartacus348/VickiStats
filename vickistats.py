import json
import string
from collections.abc import Generator
from enum import Flag, auto
from typing import Any


class ParserState(Flag):
    Empty = auto(),
    QuotedStr = auto(),
    UnQuotedStr = auto(),
    Num = auto()

def tokenparser(text_generator: Generator[str, Any, None]) :
    # rules:
    # key=value
    # { indicates start of list of values, ended by }
    # values space-delimited
    # not all string values are delimited
    # there are numbers
    # there are yes/no booleans
    letters = ""
    this_word: str = ""
    state = ParserState.Empty
    for char in text_generator:
        match state:
            case ParserState.Empty:
                if len(this_word) > 0: fail(char, letters, state, this_word)
                if char in string.whitespace:
                    continue
                elif char == "\"":
                    state = ParserState.QuotedStr
                    this_word += char
                elif char == "}":
                    this_word += "],"
                    letters += this_word
                    return letters
                elif char == "=":
                    letters += ":"
                elif char == "{":
                    letters += "[" + tokenparser(text_generator)
                elif char in string.digits + "-":
                    state = ParserState.Num
                    this_word += char
                elif char in string.ascii_letters:
                    state = ParserState.UnQuotedStr
                    this_word += char
                else:
                    fail(char, letters, state, this_word)
            case ParserState.UnQuotedStr:
                if char == "\"":
                    fail(char, letters, state, this_word)
                elif char in string.whitespace:
                    letters += "\""+this_word+"\","
                    this_word = ""
                    state = ParserState.Empty
                elif char == "=":
                    letters += "\"" + this_word + "\":"
                    this_word = ""
                    state=ParserState.Empty
                elif char == "}":
                    return letters + "\"" + this_word + "\"]"
                elif char in string.digits + string.punctuation + string.ascii_letters:
                    this_word += char
                else:
                    fail(char, letters, state, this_word)
            case ParserState.QuotedStr:
                if char == "\"":
                    letters += this_word + char + ","
                    this_word = ""
                    state = ParserState.Empty
                elif char in string.digits + string.punctuation + string.ascii_letters + string.whitespace + "=":
                    this_word += char
                else:
                    fail(char, letters, state, this_word)
            case ParserState.Num:
                if char in string.digits + ".":
                    this_word += char
                elif char in string.ascii_letters:
                    this_word += char
                    state = ParserState.UnQuotedStr
                elif char in string.whitespace:
                    letters += this_word + ","
                    this_word = ""
                    state = ParserState.Empty
                elif char == "}":
                    return letters + this_word + "],"
                elif char == "=":
                    letters += this_word + ":"
                    this_word = ""
                    state = ParserState.Empty
                else:
                    fail(char, letters, state, this_word)

    return letters


def fail(char, letters, state, this_word):
    raise ValueError(f"Unexpected char {char} in word {this_word} and line {letters} in state {state}")

def parse(text_generator: Generator[str, Any, None]) -> dict[dict|list]:
    # parse out the weird whitespace and un-quoted strings
    temp = tokenparser(text_generator)

    # second round of fixes to make json-compliant
    return temp

filename = "Shattered_World_1.7.7.v3"

with open(filename, "r", encoding="utf-8") as f:
    raw_text = f.read()

combined = parse((c for c in raw_text))

with open("temp.json", "w", encoding="utf-8") as f:
    f.write(combined)

# load as a map
combined_file = json.loads(combined)

# process the map
