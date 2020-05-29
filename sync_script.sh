#!/bin/bash

scp lexicon.py pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/
scp lexicon_config.py pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/
scp lexicon.css pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/
scp -r templates/ pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/templates

ssh pi@pi "cd /media/NAS/CLAHub/other_sites/Lexicon/ && python3 /media/NAS/CLAHub/other_sites/Lexicon/lexicon.py"

