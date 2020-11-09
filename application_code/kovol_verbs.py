"""A script to read our collection of verb paradigms, manipulate and display them"""

import datetime
import logging
import os
import pprint

import pyexcel_ods3
from jinja2 import Environment, FileSystemLoader

import lexicon_config

id_col, actor_col, tense_col, mode_col, kovol_col, english_col, author_col = 0, 1, 2, 3, 4, 5, 6

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
    vowels = ['i', 'e', 'ɛ', 'a', 'ə', 'u', 'o', 'ɔ']

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

    # def future_paradigm(self):
    #     """Shows a future paradigm"""
    #     return pprint.pprint(self.future)
    #
    # def past_paradigm(self):
    #     """Shows a recent past paradigm"""
    #     return pprint.pprint(self.past)
    #
    # def rpast_paradigm(self):
    #     """Shows a remote past paradigm"""
    #     return pprint.pprint(self.remote_past)
    #
    # def show_paradigms(self):
    #     pprint.pprint((self.rpast_paradigm(),
    #                    self.past_paradigm(),
    #                    self.future_paradigm()))

    def predict_root(self):
        # Take the future 1st plural and recent past 1st singular and strip the suffix. The word should be the root,
        # root reduction operates to remove either a C or V in all declensions.
        possible_root1 = self.future['1s'][0:-4]  # strip -inim
        possible_root2 = self.past['1s'][0:-3]  # strip -gom

        if len(possible_root1) > len(possible_root2):
            return possible_root1
        else:
            return possible_root2

    def predict_paradigm(self):
        root = self.predict_root()
        # is the last letter of the root a vowel?
        if root[-1] in self.vowels:
            v_reduction_root = root[0:-1]
            c_reduction_root = root
            last_v = root[-1]
        else:
            v_reduction_root = root
            c_reduction_root = root[0:-1]
            last_v = root[-2]
        if last_v == 'u':
            sfx_v = 'u'
        elif last_v == 'a':
            sfx_v = 'a'
        else:
            sfx_v = 'o'
        remote_past = {
            '1s': v_reduction_root + sfx_v + 'm',
            '2s': v_reduction_root + 'oŋ',
            '3s': v_reduction_root + 'ot',
            '1p': v_reduction_root + 'omuŋg',
            '2p': v_reduction_root + 'omwa',
            '3p': v_reduction_root + 'ɛmind',
        }
        past = {
            '1s': c_reduction_root + 'g' + sfx_v + 'm',
            '2s': c_reduction_root + 'goŋ',
            '3s': c_reduction_root + 'ge',
            '1p': v_reduction_root + sfx_v + 'ŋg',
            '2p': c_reduction_root + 'g' + sfx_v + 'ma',
            '3p': c_reduction_root + 'g' + sfx_v + 'nd',
        }
        future = {
            '1s': v_reduction_root + 'inim',
            '2s': v_reduction_root + 'iniŋ',
            '3s': v_reduction_root + 'iŋ',
            '1p': v_reduction_root + 'ug',
            '2p': v_reduction_root + 'a',
            '3p': v_reduction_root + 'is',
        }
        return remote_past, past, future


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
                k.add_row(i)
            k.pred_remote_past, k.pred_past, k.pred_future = k.predict_paradigm()
            verbs.append(k)
        logger.info('{n} Kovol verbs processed'.format(n=len(verbs)))
        return sorted(verbs, key=lambda v: v.kov)

    # Output as a list of dictionaries for phonology assistant to use
    elif output == 'list':
        for row in raw_data:
            item = {
                'phon': row[kovol_col],
                'eng': row[english_col] + ': ' + row[tense_col] + ' ' + row[actor_col],
                'tpi': 'None',
                'pos': 'V'
            }
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


def evaluate_prediction(Verbs):
    errors = 0
    number_of_paradigms = len(Verbs) * 3 * 6
    for v in Verbs:
        if v.future == v.pred_future and v.past == v.pred_past and v.remote_past == v.pred_remote_past:
            print(str(v) + ' predicted correctly')
        else:
            future_diff = list(v.future.items() ^ v.pred_future.items())
            errors += len(future_diff) / 2
            print(sorted(future_diff))
            past_diff = list(v.past.items() ^ v.pred_past.items())
            errors += len(past_diff) / 2
            print(sorted(past_diff))
            remote_past_diff = list(v.remote_past.items() ^ v.pred_remote_past.items())
            errors += len(remote_past_diff) / 2
            print(sorted(remote_past_diff))
    print('Accuracy = {x:.2f}%'.format(x=errors / number_of_paradigms * 100))


def predict_verb():
    fut1s = input('What is the first person singular future?   ')
    past1s = input('What is the first person singular recent past?   ')
    eng = input('What is the English translation?   ')
    verb = KovolVerb(fut1s, eng)
    verb.past['1s'] = past1s
    remote_past, past, future = verb.predict_paradigm()
    for tense in (remote_past, past, future):
        pprint.pprint(tense)