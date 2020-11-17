import os

from tabulate import tabulate

from lexicon import kovol_verbs

headers = ['Actor', 'Remote past', 'Recent past', 'Future', 'Imperative']
vowels = ['i', 'e', 'ɛ', 'a', 'ə', 'u', 'o', 'ɔ']
output_file = '../local_output/predicted_paradigms.rtf'
red = '\033[91m'
white = '\033[0m'


def predict_root(verb_tuple):
    # future_tns = verb_tuple[0][0:-4]  # strip -inim
    future_tns = verb_tuple[0][0:-2]  # strip -ug
    past_tns = verb_tuple[1][0:-3]  # strip -gom

    if len(past_tns) > len(future_tns):
        return past_tns
    elif len(past_tns) == len(future_tns):
        return future_tns
    else:
        return future_tns


def ending(root):
    if root[-1] in vowels:
        return 'V'
    else:
        return 'C'


def strip_consonants(root):
    """Returns a string containing just the vowels"""
    v = [c for c in root if c in vowels]
    v = ''.join(v)
    return v


def predict_future_tense(verb_tuple):
    root = predict_root(verb_tuple)
    last_character = root[-1]
    last_vowel = strip_consonants(root)[-1]
    if last_character == 'a':
        suffixes = ['anim', 'aniŋ', 'aŋ', 'ug', 'wa', 'is']
    else:
        suffixes = ['inim', 'iniŋ', 'iŋ', 'ug', 'wa', 'is']

    if ending(root) == 'V':
        future_tense = [root[0:-1] + sfx for sfx in suffixes]

        future_tense[4] = root + suffixes[4]
    else:
        future_tense = [root + sfx for sfx in suffixes]
        future_tense[4] = root + suffixes[4]

    short_o_root = False
    if last_vowel == 'o' or last_vowel == 'ɔ':
        if len(strip_consonants(root)) <= 2:
            short_o_root = True
    if short_o_root:
        for i, v in enumerate(future_tense):
            if not v.endswith('ug'):
                future_tense[i] = v.replace('ɔ', 'ɛ', 1)

    return future_tense


def predict_past_tense(verb_tuple):
    root = predict_root(verb_tuple)
    last_character = root[-1]
    last_vowel = strip_consonants(root)[-1]
    if last_character == 'u':
        suffixes = ['gum', 'gɔŋ', 'ge', 'uŋg', 'guma', 'gund']
    elif last_vowel == 'i':
        suffixes = ['gɔm', 'gɔŋ', 'ge', 'ɔŋg', 'gima', 'gɔnd']
    elif last_character == 'a':
        suffixes = ['gam', 'gaŋ', 'ga', 'aŋg', 'gama', 'gand']
    elif root.endswith('ɔl') or root.endswith('ol') or root.endswith('ul'):
        suffixes = ['gam', 'gaŋ', 'ga', 'aŋg', 'gama', 'gand']
    else:
        suffixes = ['gɔm', 'gɔŋ', 'ge', 'ɔŋg', 'gɔma', 'gɔnd']

    if ending(root) == 'C':
        if last_character == 'm':
            past_tense = [root[0:-1] + 'ŋ' + sfx for sfx in suffixes]
            past_tense[3] = root + suffixes[3]
        else:
            past_tense = [root[0:-1] + sfx for sfx in suffixes]
            past_tense[3] = root + suffixes[3]
    elif ending(root) == 'V':
        past_tense = [root + sfx for sfx in suffixes]
        past_tense[3] = root[0:-1] + suffixes[3]

    return past_tense


def predict_remote_past(verb_tuple):
    root = predict_root(verb_tuple)
    last_character = root[-1]
    last_vowel = strip_consonants(root)[-1]
    if last_character == 'u':
        suffixes = ['um', 'uŋ', 'ut', 'umuŋg', 'umwa', 'umind']
    elif last_character == 'a':
        suffixes = ['am', 'aŋ', 'at', 'amuŋg', 'amwa', 'amind']
    else:
        suffixes = ['ɔm', 'ɔŋ', 'ɔt', 'omuŋg', 'omwa', 'ɛmind']

    if ending(root) == 'V':
        remote_past = [root[0:-1] + sfx for sfx in suffixes]
    else:
        remote_past = [root + sfx for sfx in suffixes]

    return remote_past


def predict_imperative(verb_tuple):
    root = predict_root(verb_tuple)
    if ending(root) == 'V':
        return [root[0:-1] + 'e', root[0:-1] + 'as']
    else:
        return [root + 'e', root + 'as']


def predict_paradigm(verb_tuple):
    future = predict_future_tense(verb_tuple)
    past = predict_past_tense(verb_tuple)
    remote_past = predict_remote_past(verb_tuple)
    imperative = predict_imperative(verb_tuple)

    data = [['1s', remote_past[0], past[0], future[0], ''],
            ['2s', remote_past[1], past[1], future[1], imperative[0]],
            ['3s', remote_past[2], past[2], future[2], ''],
            ['1p', remote_past[3], past[3], future[3], ''],
            ['2p', remote_past[4], past[4], future[4], imperative[1]],
            ['3p', remote_past[5], past[5], future[5]], '']
    return data


def get_paradigm(verb):
    verbs = kovol_verbs.read_verbsheet()
    try:
        verb_data = [v for v in verbs if v.future['1s'] == verb][0]
    except IndexError:
        print('That verb isn\'t in the data')
        raise ValueError

    remote_past = verb_data.tabulate[0]
    past = verb_data.tabulate[1]
    future = verb_data.tabulate[2]
    imperative = verb_data.tabulate[3]
    data = [['1s', remote_past[0], past[0], future[0], ''],
            ['2s', remote_past[1], past[1], future[1].rstrip(' ig'), imperative[0]],
            ['3s', remote_past[2], past[2], future[2], ''],
            ['1p', remote_past[3], past[3], future[3], ''],
            ['2p', remote_past[4], past[4], future[4].rstrip(' ig'), imperative[1]],
            ['3p', remote_past[5], past[5], future[5], '']]
    return data


def format_paradigm(data, verb='undefined'):
    v = verb.future['1s']
    root = predict_root((verb.future['1p'], verb.past['1s']))
    header = '\n{div}\nParadigm for {verb}. Root is thought to be {root}'.format(div='=' * 80, verb=v, root=root)
    paradigm = []
    for d in data:
        paradigm += '\n{Title}:\n'.format(Title=d['title'])
        paradigm += tabulate(d['data'], headers=headers)

    return header + ''.join(paradigm)


def display_paradigms(correct_paradigms, incorrect_paradigms):
    print('{n} paradigms processed\n'.format(n=len(correct_paradigms) + len(incorrect_paradigms)))
    print('The following paradigms were accurate:')
    for p in correct_paradigms:
        print(p)

    print('\nIncorrect Paradigms:')
    for p in incorrect_paradigms:
        print(p)


def print_paradigms(data, verb='undefined', root='undefined'):
    with open(output_file, 'a') as file:
        print('\n{div}\nParadigm for {verb}. Root is thought to be {root}'.format(div='=' * 80, verb=verb, root=root)
              , file=file)
        for d in data:
            print('\n{Title}:'.format(Title=d['title']), file=file)
            print(tabulate(d['data'], headers=headers), file=file)


def compare_paradigms(predicted_data, actual_data):
    for i, row in enumerate(predicted_data):
        for j, d in enumerate(row):
            if d != actual_data[i][j]:
                predicted_data[i][j] = '{red}{d}{white}'.format(red=red, d=d, white=white)

    return predicted_data


def process_verb_list(verbs):
    paradigms = []
    for v in verbs:
        predicted_paradigm = predict_paradigm((v.future['1p'], v.past['1s']))
        actual_paradigm = get_paradigm(v.future['1s'])
        predicted_paradigm = compare_paradigms(predicted_paradigm, actual_paradigm)

        p = format_paradigm([{'title': 'Predicted paradigm', 'data': predicted_paradigm},
                             {'title': 'Actual paradigm', 'data': actual_paradigm}],
                            verb=v)
        paradigms.append(p)
    incorrect_paradigms = [p for p in paradigms if red in p]
    correct_paradigms = [p[95:p.find('.')] for p in paradigms if red not in p]

    display_paradigms(correct_paradigms, incorrect_paradigms)


if __name__ == '__main__':

    data = kovol_verbs.read_verbsheet()
    target_verbs = ['sindinim',
                    'janim',
                    'saliβinim',
                    'liβinim',
                    'aminim',
                    'aŋgiminim',
                    'wɛnim',
                    'tɛnim',
                    'piβugɛnim',
                    'lambiginim',
                    'utinim',
                    'ɛtinim',
                    'duginim',
                    'ʔanatinim',
                    'ɛliminim',
                    'sɛminim']
    verbs = [v for v in data if v.future['1s'] in target_verbs]

    if os.path.exists(output_file):
        os.remove(output_file)
    process_verb_list(verbs)
