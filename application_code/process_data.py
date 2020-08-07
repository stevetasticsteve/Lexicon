# This file contains functions for the 2nd layer of the application - processing the data for output. This involves
# validating the raw data to identify data entry mistakes and collating the data under headwords (so for instance.
# all the different meanings of 'running' would go under a single dictionary entry rather than several.

import logging
from collections import Counter

logger = logging.getLogger('LexiconLog')


def validate_data(processed_data):
    """Check the spreadsheet for incorrectly entered data". Returns None or an error tuple. A master function
    to call all validation checks and perform an assertion that good data is provided."""
    check_processed_data(processed_data, 'validate_data()')

    errors = [validate_find_missing_senses(processed_data)]
    if not errors[0]:
        errors = None
    return errors


class DataValidationError:
    """A simple object describing and detailing validation errors"""

    def __init__(self, error_type, error_data):
        self.error_type = error_type
        self.error_data = error_data


def validate_find_missing_senses(processed_data):
    """Returns a list (or None if n/a) of phonetic entries that are the same but aren't marked as senses of
    each other. This may reveal data entry errors."""
    words = [item['phon'] for item in processed_data]
    count = Counter(words)
    count = count.items()  # convert to list of tuples (phonetics, number of times counted)
    repeated_phonetics = [item for item in count if item[1] > 1]  # filter out single occurrences

    repeated_senses = []
    for entry in repeated_phonetics:
        phonetics = entry[0]
        entries_matching_phonetics = [entry for entry in processed_data if entry['phon'] == phonetics]

        entry_sense_count = Counter([entry['sense'] for entry in entries_matching_phonetics])
        entry_sense_count = entry_sense_count.items()
        repeated_sense = [item for item in entry_sense_count if item[1] > 1]
        if repeated_sense:
            error_msg = '{phonetics} use same sense  number multiple times.'.format(phonetics=phonetics)
            repeated_senses.append(error_msg)

    if repeated_senses:
        logger.info('   -Data validation found repeated senses')
        return DataValidationError('Sense number repeated', repeated_senses)
    else:
        return None


def sort_by_id(processed_data):
    return sorted(processed_data, key=lambda data: data['id'])


def sort_by_tag(processed_data):
    return sorted(processed_data, key=lambda data: data['tag'].lower())


def sort_by_sense(processed_data):
    return sorted(processed_data, key=lambda data: data['sense'])


# Define some quick asserts to make sure functions are given the correct data model to work on (they are similar)
def check_processed_data(processed_data, function):
    """A quick assert that the right data model is given to function, a list of dictionaries produced by
    read_lexicon()"""
    try:
        assert len(processed_data) > 0, 'No data to work on!'
        assert type(processed_data) == list, \
            'wrong data type given to {function} - needs the result of read_lexicon()'.format(function=function)
        assert type(processed_data[0]) == dict, \
            'wrong data type given to {function} - needs the result of read_lexicon()'.format(function=function)
        return True
    except AssertionError:
        logger.exception('Function called incorrectly')
        raise AssertionError
    except TypeError:
        logger.exception('Function called incorrectly')
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
        logger.exception('{f} called incorrectly'.format(f=function))
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
            logger.error('Lexicon entry initialised with wrong type')
            raise TypeError

    def __str__(self):
        return 'Lexicon entry: {h}'.format(h=self.headword)

    def __repr__(self):
        return 'Lexicon entry: {h}- {n} senses'.format(h=self.headword, n=len(self.entry))


def create_lexicon_entries(processed_data):
    """Takes the data and creates actual dictionary entries that takes account of multiple senses for the same word.
    Returns a list of tuples (headword, list of sense dictionary) sorted alphabetically by headword"""
    check_processed_data(processed_data, 'create_lexicon_entries()')
    processed_data = sort_by_sense(processed_data)  # get the sense numbers in order
    processed_data = sort_by_id(processed_data)
    lexicon_entries = []
    last_id = 0  # blank variable to check if headwords are the same
    lexeme_index = -1  # counter for lexicon_entries
    # Loop through the entries and create the dictionary entries
    for entry in processed_data:
        # choose phonetics for headword if orthography not available
        if entry['orth']:
            headword = entry['orth']
        else:
            headword = entry['phon']
        sense_data = {
            'pos': entry['pos'],
            'phonetics': entry['phon'],
            'english': entry['eng'],
            'tok_pisin': entry['tpi'],
            'definition': entry['def'],
            'example': entry['ex'],
            'example_translation': entry['trans'],
            'sense': entry['sense']
        }

        if last_id == entry['id']:  # this is a sense of the previous headword
            lexicon_entries[lexeme_index].entry.append(sense_data)
        else:  # this is a new headword
            lexeme = LexiconEntry(headword, sense_data)
            lexicon_entries.append(lexeme)
            lexeme_index += 1
        last_id = entry['id']
    # sort alphabetically
    lexicon_entries = sorted(lexicon_entries, key=lambda lexeme_object: lexeme_object.headword.lower())
    return lexicon_entries


def create_reverse_lexicon_entries(processed_data):
    """Adjust the processed data so it's suitable to be displayed in an English to Lang dict"""
    check_processed_data(processed_data, 'create_reverse_lexicon_entries()')
    # sort in English alphabetical order
    processed_data = sorted(processed_data, key=lambda d: d['eng'].lower())
    lexicon_entries = []
    for item in processed_data:
        # set the headword
        if item['orth']:
            item['headword'] = item['orth']
        else:
            item['headword'] = item['phon']
            # create the LexiconEntry object
        lexicon_entries.append(LexiconEntry(item['eng'].lower(), item))
    return lexicon_entries


def get_word_beginnings(lexicon_entries):
    """Takes a list of LexiconEntry objects and returns an alphabetically sorted set of the first letters of all
     headwords"""
    check_lexicon_entries(lexicon_entries, 'get_word_beginnings()')
    letters = [x.headword[0].lower() for x in lexicon_entries]
    return sorted(set(letters))
