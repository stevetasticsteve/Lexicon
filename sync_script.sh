#!/bin/bash

rsync -v lexicon.py lexicon_config.py pi@pi:/media/NAS/CLAHub/other_sites/Lexicon/
ssh pi@pi "python3 /media/NAS/CLAHub/other_sites/Lexicon/lexicon.py"

