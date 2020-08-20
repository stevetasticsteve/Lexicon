#!/bin/bash

rsync -r --delete /home/steve/Documents/Computing/Python_projects/Lexicon/application_code/ pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/
rsync -r --delete /home/steve/Documents/Computing/Python_projects/Lexicon/stylesheets/ pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/
rsync -r --delete /home/steve/Documents/Computing/Python_projects/Lexicon/templates/ pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/
rsync --delete /home/steve/Documents/Computing/Python_projects/Lexicon/lexicon.py pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/


ssh pi@pi "cd /media/NAS/CLAHub/other_sites/Lexicon/ && python3 /media/NAS/CLAHub/other_sites/Lexicon/main.py"

