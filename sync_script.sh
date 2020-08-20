#!/bin/bash

rsync -r /home/steve/Documents/Computing/Python_projects/Lexicon/application_code/ pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/application_code
rsync -r /home/steve/Documents/Computing/Python_projects/Lexicon/stylesheets/ pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/stylesheets/
rsync -r /home/steve/Documents/Computing/Python_projects/Lexicon/templates/ pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/templates
rsync /home/steve/Documents/Computing/Python_projects/Lexicon/lexicon.py pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/
rsync /home/steve/Documents/Computing/Python_projects/Lexicon/lexicon_config.py pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/
rsync /home/steve/Documents/Computing/Python_projects/Lexicon/kovol_verbs.py pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/


ssh pi@pi "cd /media/NAS/CLAHub/other_sites/Lexicon/ && python3 lexicon.py"

