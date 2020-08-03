#!/usr/bin/python3
import logging
import sys
import traceback

import lexicon_config
from application_code import output
from application_code import read_data


def initiate_logging():
    # Initiate error logging
    log = logging.getLogger('LexiconLog')
    log.setLevel(logging.DEBUG)

    # add a stream log, and a file log for errors
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)
    log.info('Updating Lexicon')
    if __name__ == '__main__':
        log_file = lexicon_config.settings['log_file']
        fh = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(logging.ERROR)
        log.addHandler(fh)
    return log


def excepthook(exctype, value, tb):
    if exctype == AssertionError:
        logger.error('A critical error occurred: {value} \nAdjust settings and try again'.format(value=value))
    else:
        logger.critical('''An unhandled error occured, please contact the developer:
        Error type : {type}
        Error value: {value}
        Traceback: {tb}'''.format(type=exctype, value=value, tb=traceback.format_tb(tb)))


logger = initiate_logging()
if __name__ == '__main__':
    sys.excepthook = excepthook

    data = read_data.read_lexicon()
    output.generate_html(data)
    output.create_phonemic_assistant_db(data, checked_only=False)
