# This file contains classes and functions for retrieving verb data and putting it into a Verb object.
# Also handles verb prediction.

import csv


class KovolVerb:
    """A class to represent a Kovol verb defining the conjugations of it as attributes with methods for retrieving
    those conjugations and printing to screen."""

    vowels = (
        "i",
        "e",
        "ɛ",
        "a",
        "ə",
        "u",
        "o",
        "ɔ",
    )  # Vowels in Kovol language

    def __init__(self, future1s: str, english: str):
        # Meta data
        self.kovol = future1s
        self.english = english
        self.tpi = ""  # Tok pisin
        self.author = ""  # Who entered the data
        self.errors = []  # used for PredictedVerb subclass,
        # defined here to maintain template compatibility

        # Remote past tense
        self.remote_past_1s = ""
        self.remote_past_2s = ""
        self.remote_past_3s = ""
        self.remote_past_1p = ""
        self.remote_past_2p = ""
        self.remote_past_3p = ""

        # Recent past tense
        self.recent_past_1s = ""
        self.recent_past_2s = ""
        self.recent_past_3s = ""
        self.recent_past_1p = ""
        self.recent_past_2p = ""
        self.recent_past_3p = ""

        # Future tense
        self.future_1s = future1s
        self.future_2s = ""
        self.future_3s = ""
        self.future_1p = ""
        self.future_2p = ""
        self.future_3p = ""

        # Imperative forms
        self.singular_imperative = ""
        self.plural_imperative = ""

        # Other forms
        self.short = ""

    def __str__(self):
        string = self.get_string_repr()
        return f"Kovol verb: {string['future_1s']}, \"{string['english']}\""

    def __repr__(self):
        return self.__str__()


def get_data_from_csv(csv_file, format="object") -> list:
    """reads a csv file and outputs a list of KovolVerb objects.
    Can accept 'list' as format to return a list of listed dict entries instead"""
    with open(csv_file, newline="") as file:
        reader = csv.DictReader(
            file,
            delimiter=",",
            fieldnames=["actor", "tense", "mode", "kov", "eng", "checked"],
        )
        data = [r for r in reader]
        if "actor" in data[0]:
            data.pop(0)  # Remove header

    # Get a list of the unique verbs (identified by English translation)
    eng = set([v["eng"] for v in data])
    # Get list of all data where each index is a list of dict items for each translation
    verb_data = [[d for d in data if d["eng"] == e] for e in eng]

    if format == "list":
        return verb_data
    elif format == "object":
        return csv_data_to_verb_object(verb_data)


def csv_data_to_verb_object(verb_data: list) -> list:
    """Take a list of dicts representing a verb and return a list of Verb objects instead."""
    verbs = []
    for d in verb_data:
        eng = d[0]["eng"]  # every row item contains this info
        v = KovolVerb("", eng)  # init obj with temp 1s_future

        future_tense = [v for v in d if v["tense"].lower() == "future"]
        for t in future_tense:
            if t["actor"].lower() == "1s":
                v.future_1s = t["kov"]
            elif t["actor"].lower() == "2s":
                if not t["mode"] == "imperative":
                    v.future_2s = t["kov"]
            elif t["actor"].lower() == "3s":
                v.future_3s = t["kov"]
            elif t["actor"].lower() == "1p":
                v.future_1p = t["kov"]
            elif t["actor"].lower() == "2p":
                if not t["mode"] == "imperative":
                    v.future_2p = t["kov"]
            elif t["actor"].lower() == "3p":
                v.future_3p = t["kov"]

        recent_past_tense = [v for v in d if v["tense"].lower() == "recent past"]
        for t in recent_past_tense:
            if t["actor"].lower() == "1s":
                v.recent_past_1s = t["kov"]
            elif t["actor"].lower() == "2s":
                v.recent_past_2s = t["kov"]
            elif t["actor"].lower() == "3s":
                v.recent_past_3s = t["kov"]
            elif t["actor"].lower() == "1p":
                v.recent_past_1p = t["kov"]
            elif t["actor"].lower() == "2p":
                v.recent_past_2p = t["kov"]
            elif t["actor"].lower() == "3p":
                v.recent_past_3p = t["kov"]

        remote_past_tense = [v for v in d if v["tense"].lower() == "remote past"]
        for t in remote_past_tense:
            if t["actor"].lower() == "1s":
                v.remote_past_1s = t["kov"]
            elif t["actor"].lower() == "2s":
                v.remote_past_2s = t["kov"]
            elif t["actor"].lower() == "3s":
                v.remote_past_3s = t["kov"]
            elif t["actor"].lower() == "1p":
                v.remote_past_1p = t["kov"]
            elif t["actor"].lower() == "2p":
                v.remote_past_2p = t["kov"]
            elif t["actor"].lower() == "3p":
                v.remote_past_3p = t["kov"]

        imperatives = [v for v in d if v["mode"]]
        for t in imperatives:
            if t["actor"].lower() == "2s":
                v.singular_imperative = t["kov"]
            elif t["actor"].lower() == "2p":
                v.plural_imperative = t["kov"]
            elif t["mode"].lower() == "short":
                v.short = t["kov"]

        verbs.append(v)
    verbs = sorted(verbs, key=lambda x: x.future_1s)
    return verbs
