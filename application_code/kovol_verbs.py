"""A script to read our collection of verb paradigms, manipulate and display them"""

import datetime
import logging
import os

import pyexcel_ods3
from jinja2 import Environment, FileSystemLoader

import lexicon_config

id_col, actor_col, tense_col, mode_col, kovol_col, english_col, check_col, author_col = 0, 1, 2, 3, 4, 5, 6, 7

logger = logging.getLogger('LexiconLog')


def blank_paradigm():
    """Returns a blank paradigm dictionary"""
    d = {
        '1s': '',
        '2s': '',
        '3s': '',
        '1p': '',
        '2p': '',
        '3p': '',
    }
    return d


class KovolVerb:
    def __init__(self, future1s, english):
        self.kov = future1s
        self.eng = english
        self.short = ''
        self.author = ''
        self.future = blank_paradigm()
        self.future['1s'] = future1s
        self.past = blank_paradigm()
        self.remote_past = blank_paradigm()
        self.sng_imperative = ''
        self.pl_imperative = ''

    def __str__(self):
        return '{kovol}, {eng}'.format(kovol=self.kov, eng=self.eng)

    def __repr__(self):
        return 'Kovol Verb: {v}'.format(v=self.kov)

    def add_row(self, row):
        """Method for inserting data from a spreadsheet row if it is applicable"""
        # if it's not the verb we're interested in return
        assert row[english_col], 'Can\'t process verbs if English column is blank'
        if row[english_col] != self.eng:
            return
        tense = row[tense_col]
        actor = row[actor_col]
        kovol = row[kovol_col]
        mode = row[mode_col]
        # first row processed should grab author
        if not self.author:
            self.author = row[author_col]
        # short verbs don't need more processing, take it and return
        if mode == 'short':
            self.short = kovol
            return

        # otherwise slot row into correct place in paradigm
        if tense == 'future':
            if actor == '2s':
                if mode == 'imperative':
                    self.sng_imperative = kovol
                    # sometimes the imperative is all we have, include it if blank
                    if not self.future['2s']:
                        self.future['2s'] = kovol + '*'
                else:
                    self.future['2s'] = kovol
            elif actor == '3s':
                self.future['3s'] = kovol
            elif actor == '1p':
                self.future['1p'] = kovol
            elif actor == '2p':
                if mode == 'imperative':
                    self.pl_imperative = kovol
                    # sometimes the imperative is all we have, include it if blank
                    if not self.future['2p']:
                        self.future['2p'] = kovol + '*'
                else:
                    self.future['2p'] = kovol
            elif actor == '3p':
                self.future['3p'] = kovol
        if tense == 'recent past':
            if actor == '1s':
                self.past['1s'] = kovol
            elif actor == '2s':
                self.past['2s'] = kovol
            elif actor == '3s':
                self.past['3s'] = kovol
            elif actor == '1p':
                self.past['1p'] = kovol
            elif actor == '2p':
                self.past['2p'] = kovol
            elif actor == '3p':
                self.past['3p'] = kovol
        if tense == 'remote past':
            if actor == '1s':
                self.remote_past['1s'] = kovol
            elif actor == '2s':
                self.remote_past['2s'] = kovol
            elif actor == '3s':
                self.remote_past['3s'] = kovol
            elif actor == '1p':
                self.remote_past['1p'] = kovol
            elif actor == '2p':
                self.remote_past['2p'] = kovol
            elif actor == '3p':
                self.remote_past['3p'] = kovol

    def create_tabulate_object(self):
        """Creates a tuple object containing the data needed for tabulate to create a table"""
        future_tense = (
            self.future['1s'],
            self.future['2s'],
            self.future['3s'],
            self.future['1p'],
            self.future['2p'],
            self.future['3p'],
        )
        past_tense = (
            self.past['1s'],
            self.past['2s'],
            self.past['3s'],
            self.past['1p'],
            self.past['2p'],
            self.past['3p'],
        )
        remote_past_tense = (
            self.remote_past['1s'],
            self.remote_past['2s'],
            self.remote_past['3s'],
            self.remote_past['1p'],
            self.remote_past['2p'],
            self.remote_past['3p'],
        )
        imperative = (
            self.sng_imperative,
            self.pl_imperative
        )
        return remote_past_tense, past_tense, future_tense, imperative


def read_verbsheet(spreadsheet=lexicon_config.settings['verb_spreadsheet'], output='class'):
    # Returns an alphabetically sorted list of Verb objects
    assert os.path.exists(spreadsheet), 'Verb spreadsheet missing'
    raw_data = pyexcel_ods3.get_data(spreadsheet)['Paradigms']
    raw_data.pop(0)  # get rid of the first row
    raw_data = [x for x in raw_data if len(x) >= 5]  # get rid rows lacking data (5 is where the Kovol words are)
    future1s_set = set([(x[kovol_col], x[english_col]) for x in raw_data if
                        (x[actor_col] == '1s' and x[tense_col] == 'future')])
    verbs = []
    if output == 'class':
        for v in future1s_set:
            k = KovolVerb(v[0], v[1])
            for i in raw_data:
                # Skip rows missing too much data
                if len(i) < 6:
                    continue
                k.add_row(i)
                k.tabulate = k.create_tabulate_object()
            verbs.append(k)
        logger.info('{n} Kovol verbs processed'.format(n=len(verbs)))
        return sorted(verbs, key=lambda v: v.kov)

    # Output as a list of dictionaries for phonology assistant to use
    elif output == 'list':
        for row in raw_data:
            # Skip rows missing too much data
            if len(row) < 6:
                continue
            item = {
                'phon': row[kovol_col],
                'eng': row[english_col] + ': ' + row[tense_col] + ' ' + row[actor_col],
                'tpi': 'None',
                'pos': 'V',
            }
            try:
                item['checked'] = row[check_col]
            except IndexError:
                pass
            verbs.append(item)
        return verbs


def paradigm_html(verbs):
    """Creates a verbs paradigms page"""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('verb_paradigm_template.html')

    date = datetime.datetime.now().strftime('%A %d %B %Y')
    context = {
        'title': 'Verbs',
        'date': date,
        'language': lexicon_config.settings['language'],
        'header': 'verbs',
        'bootstrap': lexicon_config.settings.get('bootstrap'),
        'jquery': lexicon_config.settings.get('jquery'),
    }
    html = os.path.join(lexicon_config.settings['target_folder'], 'verbs.html')
    with open(html, 'w') as file:
        print(template.render(context=context, verbs=verbs), file=file)

    logger.info('Kovol verb paradigms HTML page created')


