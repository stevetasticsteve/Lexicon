import csv
import os

import lexicon_config
from application_code import kovol_verbs
from application_code import predict_verbs

print('Reading data...')
verbs = kovol_verbs.read_verbsheet()
roots = []
print('Predicting roots...')
for v in verbs:
    r = predict_verbs.predict_root((v.future['1p'], v.past['1s']))
    roots.append((v.future['1s'], r))

path = os.path.join(lexicon_config.settings['target_folder'], 'root_report.csv')
with open(path, 'w') as file:
    writer = csv.writer(file)
    writer.writerows(roots)
print('Done, check {file}'.format(file=path))