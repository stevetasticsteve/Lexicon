"""A script to read our collection of verb paradigms, manipulate and display them"""

import pyexcel_ods3
import pprint
import datetime
from jinja2 import Environment, FileSystemLoader
import os

import lexicon_config as s



id_col, actor_col, tense_col, mode_col, kovol_col, english_col = 0, 1, 2, 3, 4, 5


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
        self.future = blank_paradigm()
        self.future['1s'] = future1s
        self.past = blank_paradigm()
        self.rpast = blank_paradigm()

    def __str__(self):
        return '{kovol}, {eng}'.format(kovol=self.kov, eng=self.eng)

    def __repr__(self):
        return 'Kovol Verb: {v}'.format(v=self.kov)

    def add_row(self, row):
        """Method for inserting data from a spreadsheet row if it is applicable"""
        if row[english_col] != self.eng:
            return
        tense = row[tense_col]
        actor = row[actor_col]
        kovol = row[kovol_col]
        if tense == 'future':
            if actor == '2s':
                self.future['2s'] = kovol
            elif actor == '3s':
                self.future['3s'] = kovol
            elif actor == '1p':
                self.future['1p'] = kovol
            elif actor == '2p':
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
                self.rpast['1s'] = kovol
            elif actor == '2s':
                self.rpast['2s'] = kovol
            elif actor == '3s':
                self.rpast['3s'] = kovol
            elif actor == '1p':
                self.rpast['1p'] = kovol
            elif actor == '2p':
                self.rpast['2p'] = kovol
            elif actor == '3p':
                self.rpast['3p'] = kovol

    def future_paradigm(self):
        """Shows a future paradigm"""
        return pprint.pprint(self.future)

    def past_paradigm(self):
        """Shows a recent past paradigm"""
        return pprint.pprint(self.past)

    def rpast_paradigm(self):
        """Shows a remote past paradigm"""
        return pprint.pprint(self.rpast)

    def show_paradigms(self):
        pprint.pprint((self.rpast_paradigm(),
                      self.past_paradigm(),
                      self.future_paradigm()))

def read_verbsheet(spreadsheet='Kovol_verbs.ods'):
    assert os.path.exists(spreadsheet), 'Verb spreadsheet missing'
    raw_data = pyexcel_ods3.get_data(spreadsheet)['Paradigms']
    raw_data.pop(0)  # get rid of the first row
    raw_data = [x for x in raw_data if x != []]  # get rid of blank rows at the end
    future1s_set = set([(x[kovol_col], x[english_col]) for x in raw_data if
                        (x[actor_col] == '1s' and x[tense_col] == 'future')])
    verbs = []
    for v in future1s_set:
        k = KovolVerb(v[0], v[1])
        for i in raw_data:
            k.add_row(i)
        verbs.append(k)
    return sorted(verbs, key=lambda v: v.kov)

def paradigm_html(verbs):
    """Creates a verbs paradigms page"""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('verb_paradigm_template.html')

    date = datetime.datetime.now().strftime('%A %d %B %Y')
    context = {
        'title': 'Verbs',
        'date': date,
        'language': s.settings['language']
    }

    with open('verbs.html', 'w') as file:
        print(template.render(context=context, verbs=verbs), file=file)


if __name__ == '__main__':
    verbs = read_verbsheet()
    for v in verbs:
        v.show_paradigms()