# This file contains functions related to the first layer of the application: reading the spreadsheet
# and returning the data in dictionary format, including some processing tasks that fill in blank cells

import csv
import logging
import os

import pyexcel_io
import pyexcel_ods3

import lexicon_config

logger = logging.getLogger("LexiconLog")


def check_settings(config_file=lexicon_config.settings):
    """Cause various errors if user has incorrectly defined settings."""
    # sheet_name checked by read_lexicon()
    paths = (
        config_file["target_folder"],
        config_file["log_file"],
        config_file["spreadsheet_name"],
    )
    try:
        # check all the paths exist
        for p in paths:
            if not os.path.exists(p):
                raise FileNotFoundError(p)
        # check language name is a string
        if type(config_file["language"]) != str:
            raise TypeError("language")
        # check sheet name is a string
        if type(config_file["sheet_name"]) != str:
            raise TypeError("sheet name")

    except FileNotFoundError as e:
        msg = "The following file doesn't exist: {e}".format(e=e.args[0])
        logger.exception(msg)
        raise FileNotFoundError(msg)
    except TypeError as e:
        msg = "The {e} is not a string".format(e=e.args[0])
        logger.exception(msg)
        raise TypeError(msg)


def letter_to_number(letter):
    """returns an integer to use as an index for a given column letter. Can only accept up to column Z"""
    assert type(letter) == str, "Must provide a string"
    assert len(letter) == 1, "Function only designed for single letter columns"
    assert letter.isalpha(), "Must provide alphabetic input"

    return ord(letter.upper()) - 65


def read_lexicon(*args, config_file=lexicon_config, number_of_columns=18):
    """Reads the .ods and returns a list of dictionary items representing the lexicon,
    unlike create_lexicon_entries() it doesn't group senses under 1 headword - it's just a data dump."""
    if args:
        logger.info(
            "Function not designed to accept arguments. \nDefine the settings in lexicon_config.py or pass a "
            "different config via the config_file **kwarg"
        )
    check_settings(
        config_file=config_file.settings
    )  # pass this in for testing purposes

    spreadsheet = config_file.settings["spreadsheet_name"]
    # read the file with pyexcel
    try:
        raw_data = pyexcel_ods3.get_data(spreadsheet)[
            config_file.settings["sheet_name"]
        ]
        # Convert column letters to list integers
        col = {
            k: letter_to_number(v) for k, v in config_file.spreadsheet_config.items()
        }
        assert (
            len(col) == number_of_columns
        ), "{n} items expected in spreadsheet_config, {m} defined".format(
            n=number_of_columns, m=len(col)
        )
        # pop the header if it exists
        if type(raw_data[0][col["id_col"]]) == str:  # Str == 'ID'
            raw_data.pop(0)
        raw_data = [x for x in raw_data if x != []]  # get rid of blank rows
    except KeyError:
        msg = "{sheet} is not a valid sheet name.".format(sheet=spreadsheet)
        logger.exception(msg)
        raise KeyError(msg)
    except pyexcel_io.exceptions.NoSupportingPluginFound:
        _, extension = os.path.splitext(spreadsheet)
        msg = (
            "{ext} is not a valid file extension. Must be .ods, .xls or .xlsx.".format(
                ext=extension
            )
        )
        logger.exception(msg)
        raise TypeError(msg)
    except IndexError:
        msg = "The file is blank"
        logger.exception(msg)
        raise AttributeError(msg)

    # pre process
    raw_data = pre_process_raw_data(raw_data, col)
    # format as a list of dict
    dict_data = raw_data_to_dict(raw_data, col, number_of_columns)
    # post process
    processed_data = post_process_raw_data(dict_data)

    logger.info("   -%d dictionary entries read" % len(processed_data))
    return processed_data


def read_additional_sheet(sheet_name, config_file=lexicon_config):
    """Reads additional sheets with columns [Kovol, Phonetic, Dialect, Description]. Intended to separate
    out proper nouns from the main sheet."""
    spreadsheet = config_file.settings["spreadsheet_name"]
    number_of_columns = 4
    # read the file with pyexcel
    try:
        raw_data = pyexcel_ods3.get_data(spreadsheet)[sheet_name]
        raw_data.pop(0)
        raw_data = [x for x in raw_data if x != []]  # get rid of blank rows
        data = []
        for row in raw_data:
            while (
                len(row) < number_of_columns
            ):  # add blank columns to avoid index errors
                row.append("")
            d = {
                "kovol": row[letter_to_number("A")],
                "phonetic": row[letter_to_number("B")],
                "dialect": row[letter_to_number("C")],
                "description": row[letter_to_number("D")],
            }
            data.append(d)
        return data

    except KeyError:
        msg = "{sheet} is not a valid sheet name.".format(sheet=spreadsheet)
        logger.exception(msg)
        raise KeyError(msg)
    except pyexcel_io.exceptions.NoSupportingPluginFound:
        _, extension = os.path.splitext(spreadsheet)
        msg = (
            "{ext} is not a valid file extension. Must be .ods, .xls or .xlsx.".format(
                ext=extension
            )
        )
        logger.exception(msg)
        raise TypeError(msg)
    except IndexError:
        msg = "The file is blank"
        logger.exception(msg)
        raise AttributeError(msg)


def pre_process_raw_data(raw_data, col):
    """Exclude blank data and incorrect ID numbers each row from .ods dump."""
    # set the id number to 0 if it's blank - preventing sort failures later
    for row in raw_data:
        if row[col["id_col"]] == "":
            row[col["id_col"]] = 0
    # exclude rows lacking ids and language data
    raw_data = [
        r
        for r in raw_data
        if r[col["id_col"]] or r[col["orth_col"]] or r[col["phon_col"]]
    ]
    raw_data.sort(key=lambda r: r[col["id_col"]])  # sort by ID number
    return raw_data


def raw_data_to_dict(raw_data, col, number_of_columns):
    """Take the rows from pyexcel_ods and convert from list to dict for easier handling."""
    dict_data = []
    for entry in raw_data:
        while len(entry) < number_of_columns:  # add blank columns to avoid index errors
            entry.append("")
        d = {
            "id": entry[
                col["id_col"]
            ],  # int, blank = 0 Don't force int, pre processing cleans up
            "orth": str(entry[col["orth_col"]]),  # str, blank = ''
            "phon": str(entry[col["phon_col"]]),  # str, blank = ''
            "dial": str(entry[col["dial_col"]]),  # str, blank = ''
            "sense": entry[
                col["sense_col"]
            ],  # int, blank = 1 Don't force int, pre processing cleans up
            "pos": str(entry[col["pos_col"]]),  # str, blank = ''
            "eng": str(entry[col["eng_col"]]),  # str, blank = ''
            "tpi": str(entry[col["tpi_col"]]),  # str, blank = ''
            "def": str(entry[col["def_col"]]),  # str, blank = ''
            "ex": str(entry[col["ex_col"]]),  # str, blank = ''
            "trans": str(entry[col["trans_col"]]),  # str, blank = ''
            "date": entry[
                col["date_col"]
            ],  # datetime.date, blank = '', format enforced by spreadsheet
            "enter": str(entry[col["enter_col"]]),  # str, blank = ''
            "check": str(entry[col["check_col"]]),  # str, blank = ''
            "syn": str(entry[col["syn_col"]]),  # str, blank = ''
            "ant": str(entry[col["ant_col"]]),  # str, blank = ''
            "link": str(entry[col["link_col"]]),  # str, blank = ''
            "tag": str(entry[col["tag_col"]]),  # str, blank = ''
        }

        dict_data.append(d)
    return dict_data


def post_process_raw_data(dict_data):
    """Add a default sense number to blank rows."""
    # post processing tasks
    for entry in dict_data:
        if entry["sense"] == "":
            entry["sense"] = 1
    return dict_data


def verb_sheet_to_csv(
    spreadsheet=lexicon_config.settings["verb_spreadsheet"],
    csv_name="verbs.csv",
    checked=False,
):
    """Read the verb spreadsheet and return a .csv object of columns B-F for kovol-language-tools"""
    csv_path = os.path.join(lexicon_config.settings["target_folder"], csv_name)

    # Returns an alphabetically sorted list of Verb objects
    assert os.path.exists(spreadsheet), "Verb spreadsheet missing"
    raw_data = pyexcel_ods3.get_data(spreadsheet)["Paradigms"]
    # get rid rows lacking data an English translation
    raw_data = [x for x in raw_data if len(x) >= 6]
    if checked:
        # only include rows with something marked in checked column
        raw_data = [x for x in raw_data if x[6]]
    else:
        raw_data = [x for x in raw_data]

    # Create the csv and return the path
    with open(csv_path, "w", encoding="utf-8", newline="\n") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(raw_data)
    return csv_path
