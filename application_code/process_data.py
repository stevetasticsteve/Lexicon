# This file contains functions for the 2nd layer of the application - processing the data for output. This involves
# validating the raw data to identify data entry mistakes and collating the data under headwords (so for instance.
# all the different meanings of 'running' would go under a single dictionary entry rather than several.
import csv
import logging
from collections import Counter

from application_code import verbs
from application_code import read_data

logger = logging.getLogger("LexiconLog")


def validate_data(processed_data):
    """Check the spreadsheet for incorrectly entered data". Returns None or an error tuple. A master function
    to call all validation checks and perform an assertion that good data is provided."""
    check_processed_data(processed_data, "validate_data()")

    errors = [
        validate_find_missing_senses(processed_data),
        validate_find_missing_pos(processed_data),
        validate_translation_missing(processed_data),
        validate_repeated_id(processed_data),
        validate_missing_id(processed_data),
        validate_words_unique(processed_data),
        validate_entered_by(processed_data),
        validate_sense_number_order(processed_data),
    ]
    errors = [e for e in errors if e]
    if not errors:
        errors = None
    return errors


class DataValidationError:
    """A simple object describing and detailing validation errors"""

    def __init__(self, error_type, error_data):
        self.error_type = error_type
        self.error_data = error_data

    def __repr__(self):
        return "{type} error object".format(type=self.error_type)


def get_repeated_ids(processed_data):
    ids = [
        item["id"] for item in processed_data if item["id"] > 0
    ]  # ignore id 0 as that indicates no ID entered by user
    count = Counter(ids)
    count = count.items()  # convert to list of tuples (id, number of times counted)
    repeated_ids = [
        item[0] for item in count if item[1] > 1
    ]  # filter out single occurrences
    return repeated_ids


def get_repeated_words(processed_data):
    words = [item["phon"] for item in processed_data]
    count = Counter(words)
    count = (
        count.items()
    )  # convert to list of tuples (phonetics, number of times counted)
    repeated_phonetics = [
        item[0] for item in count if item[1] > 1
    ]  # filter out single occurrences
    return repeated_phonetics


def validate_find_missing_senses(processed_data):
    """Returns a list (or None if n/a) of phonetic entries that are the same but aren't marked as senses of
    each other. This may reveal data entry errors."""
    repeated_phonetics = get_repeated_words(processed_data)
    repeated_senses = []
    for i in repeated_phonetics:
        rows = [r for r in processed_data if r["phon"] == i]

        entry_sense_count = Counter([entry["sense"] for entry in rows])
        entry_sense_count = entry_sense_count.items()
        repeated_sense = [item for item in entry_sense_count if item[1] > 1]
        if repeated_sense:
            error_msg = "{phonetics} uses same sense number multiple times.".format(
                phonetics=i
            )
            repeated_senses.append(error_msg)

    if repeated_senses:
        logger.info("   -Data validation found repeated senses")
        return DataValidationError("Sense number repeated", repeated_senses)
    else:
        return None


def validate_find_missing_pos(processed_data):
    """Checks the spreadsheet for blank POS cells"""
    blank_pos = [
        "{w} is missing pos".format(w=row["phon"])
        for row in processed_data
        if row["pos"] == ""
    ]
    if blank_pos:
        logger.info("   -Data validation found missing POS")
        return DataValidationError("Part of speech missing", blank_pos)
    else:
        return None


def validate_missing_id(processed_data):
    """Check for data assinged an ID of 0. Indicates user forgot to put ID number"""
    blank_id = [
        "{w} is missing an ID number".format(w=row["phon"])
        for row in processed_data
        if row["id"] == 0
    ]
    if blank_id:
        logger.info("   -Data validation found missing ID number")
        return DataValidationError("ID number is missing", blank_id)
    else:
        return None


def validate_repeated_id(processed_data):
    """ID numbers can be reused only if the phonetic word is the same. A repeated ID indicates a secondary sense of a
    a word. Thus repeated ID numbers with differing phonetics indicates a data entry mistake"""
    repeated_ids = get_repeated_ids(processed_data)
    error_data = []
    for i in repeated_ids:
        rows = [r for r in processed_data if r["id"] == i]
        entry = rows[0]["phon"]  # pick an word to measure all the others against
        for row in rows:
            if entry != row["phon"]:
                error_data.append(
                    "ID number {id} is used for both {entry} and {conflict}".format(
                        id=i, entry=entry, conflict=row["phon"]
                    )
                )

    if error_data:
        logger.info("   -Data validation found repeated ids with differing phonetics")
        return DataValidationError(
            "An ID number has been incorrectly repeated", error_data
        )
    else:
        return None


def validate_translation_missing(processed_data):
    missing_translations = [
        '{w} example: "{ex}", is missing a translation'.format(
            w=row["phon"], ex=row["ex"]
        )
        for row in processed_data
        if (row["ex"] != "" and row["trans"] == "")
    ]
    if missing_translations:
        logger.info("   -Data validation found missing example translations")
        return DataValidationError(
            "Example is missing a translation", missing_translations
        )
    else:
        return None


def validate_words_unique(processed_data):
    """Checks for words that are phonetically identical, but don't have identical IDs. If the word is a sense of another
    word the ID number should be the same."""
    repeated_phonetics = get_repeated_words(processed_data)
    error_data = []
    for i in repeated_phonetics:
        rows = [r for r in processed_data if r["phon"] == i]
        id_ = rows[0]["id"]  # pick an id to measure all the others against
        for row in rows:
            if id_ != row["id"]:
                error_data.append(
                    "{w} appears multiple times with differing ID number".format(
                        w=row["phon"]
                    )
                )

    if error_data:
        logger.info("   -Data validation found repeated words")
        return DataValidationError("Word is duplicated", error_data)
    else:
        return None


def validate_entered_by(processed_data):
    """Finds words that have a blank entered_by field"""
    error_data = [
        "{w} is lacking an author".format(w=r["phon"])
        for r in processed_data
        if r["enter"] == ""
    ]
    if error_data:
        logger.info("   -Data validation found repeated words")
        return DataValidationError("Author is missing", error_data)
    else:
        return None


def validate_sense_number_order(processed_data):
    """Checks to make sure sense numbers aren't missing. 1,2,3 rather than 1,3,4 for example."""
    repeated_ids = get_repeated_ids(processed_data)
    error_data = []
    for id_ in repeated_ids:
        phonetics = [r["phon"] for r in processed_data if r["id"] == id_][0]
        sense_numbers = sorted([r["sense"] for r in processed_data if r["id"] == id_])
        error_msg = "{w} has sense numbers {s}".format(w=phonetics, s=sense_numbers)

        if sense_numbers[0] != 1:  # find sense numbers that don't start with 1
            error_data.append(error_msg)
            continue

        for i, sense_number in enumerate(
            sense_numbers
        ):  # find sense numbers that don't increment by 1
            if i > 0:
                last_number = sense_numbers[i - 1]
                if sense_number != last_number + 1:
                    error_data.append(error_msg)
                    continue
    if error_data:
        logger.info("   -Data validation found misnumbered sense numbers")
        return DataValidationError("Sense numbers misnumbered", error_data)
    else:
        return None


def sort_by_id(processed_data):
    return sorted(processed_data, key=lambda data: data["id"])


def sort_by_tag(processed_data):
    return sorted(processed_data, key=lambda data: data["tag"].lower())


def sort_by_sense(processed_data):
    return sorted(processed_data, key=lambda data: data["sense"])


def phonetic_sort(character):
    if character == "ɛ":
        return "e"
    elif character == "β":
        return "b"
    elif character == "ə":
        return "e"
    elif character == "ɑ":
        return "a"
    elif character == "ʔ":
        return "k"
    elif character == "ɔ":
        return "o"
    else:
        return character


# Define some quick asserts to make sure functions are given the correct data model to work on (they are similar)
def check_processed_data(processed_data, function):
    """A quick assert that the right data model is given to function, a list of dictionaries produced by
    read_lexicon()"""
    try:
        assert len(processed_data) > 0, "No data to work on!"
        assert (
            type(processed_data) == list
        ), "wrong data type given to {function} - needs the result of read_lexicon()".format(
            function=function
        )
        assert (
            type(processed_data[0]) == dict
        ), "wrong data type given to {function} - needs the result of read_lexicon()".format(
            function=function
        )
        return True
    except AssertionError:
        logger.exception("Function called incorrectly")
        raise AssertionError
    except TypeError:
        logger.exception("Function called incorrectly")
        raise AssertionError


def check_lexicon_entries(lexicon_entries, function):
    """A quick assert that the data model comes from create_lexicon_entries, a list of tuples"""
    try:
        if type(lexicon_entries) != list:
            raise TypeError
        for o in lexicon_entries:
            if not isinstance(o, LexiconEntry):
                raise TypeError
    except TypeError:
        logger.exception("{f} called incorrectly".format(f=function))
        raise TypeError


class LexiconEntry:
    def __init__(self, headword, entry):
        self.headword = headword
        try:
            # must be either a dictionary or list of dictionaries
            if type(entry) == dict:
                self.entry = [entry]
            elif type(entry) == list:
                if entry[0] != dict:
                    raise TypeError
            else:
                raise TypeError

        except TypeError:
            logger.error("Lexicon entry initialised with wrong type")
            raise TypeError

    def __str__(self):
        return "Lexicon entry: {h}".format(h=self.headword)

    def __repr__(self):
        return "Lexicon entry: {h}- {n} senses".format(
            h=self.headword, n=len(self.entry)
        )


def create_lexicon_entries(processed_data, verb_data=None):
    """Takes the data and creates actual dictionary entries that takes account of multiple senses for the same word.
    Returns a list of tuples (headword, list of sense dictionary) sorted alphabetically by headword"""
    check_processed_data(processed_data, "create_lexicon_entries()")
    processed_data = sort_by_sense(processed_data)  # get the sense numbers in order
    processed_data = sort_by_id(processed_data)
    lexicon_entries = []
    last_id = 0  # blank variable to check if headwords are the same
    lexeme_index = -1  # counter for lexicon_entries
    # Loop through the entries and create the dictionary entries
    for entry in processed_data:
        # choose phonetics for headword if orthography not available
        if entry["orth"]:
            headword = entry["orth"]
            orth_prediction = None
        else:
            headword = entry["phon"]
            # orth_prediction = phonemics.phonetics_to_orthography(entry["phon"], hard_fail=False)

        sense_data = {
            "pos": entry["pos"],
            "phonetics": entry["phon"],
            "english": entry["eng"],
            "tok_pisin": entry["tpi"],
            "definition": entry["def"],
            "example": entry["ex"],
            "example_translation": entry["trans"],
            "sense": entry["sense"],
        }

        if (
            last_id == entry["id"] and entry["id"] != 0
        ):  # this is a sense of the previous headword
            # 0 is used to mark missing IDs
            lexicon_entries[lexeme_index].entry.append(sense_data)
        else:  # this is a new headword
            lexeme = LexiconEntry(headword, sense_data)
            # lexeme.orth_prediction = orth_prediction
            lexicon_entries.append(lexeme)
            lexeme_index += 1
        last_id = entry["id"]

    if verb_data:
        lexicon_entries += create_verb_lexicon_entries(verb_data)
    # sort alphabetically
    lexicon_entries = sorted(
        lexicon_entries,
        key=lambda lexeme_object: phonetic_sort(lexeme_object.headword.lower()),
    )
    return lexicon_entries


def create_verb_lexicon_entries(verb_data):
    """Convert a list of verb objects into Lexeme objects."""
    if "ID" in verb_data[0][0]:
        verb_data.pop(0)  # Remove header

    verb_data = [
        {"actor": v[1], "tense": v[2], "mode": v[3], "kov": v[4], "eng": v[5]}
        for v in verb_data
    ]

    # Get a list of the unique verbs (identified by English translation)
    eng = set([v["eng"] for v in verb_data])
    # Get list of all data where each index is a list of dict items for each translation
    verb_data = [[d for d in verb_data if d["eng"] == e] for e in eng]

    verb_data = verbs.csv_data_to_verb_object(verb_data)

    lexicon_entries = [LexiconEntry(v.future_1s, v.__dict__) for v in verb_data]
    # for l in lexicon_entries:
    #     l.orth_prediction = phonemics.phonetics_to_orthography(l.entry[0]["future_1s"], hard_fail=False)
    return lexicon_entries


def get_word_beginnings(lexicon_entries):
    """Takes a list of LexiconEntry objects and returns an alphabetically sorted set of the first letters of all
    headwords"""
    check_lexicon_entries(lexicon_entries, "get_word_beginnings()")
    letters = [x.headword[0].lower() for x in lexicon_entries if x.headword]
    return sorted(set(letters), key=phonetic_sort)


def get_verb_conjugations(checked=False):
    """Retrieve only the Kovol words from the verb .csv"""
    with open(
        read_data.verb_sheet_to_csv(checked=checked), "r", encoding="utf-8"
    ) as csvfile:
        data = csv.reader(csvfile)
        data = [{"phon": d[3]} for d in data]
        return data
