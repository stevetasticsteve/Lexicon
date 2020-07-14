# To do

## Validation checks
- sense numbers in order? 1,2,3 not 1,6,10
- POS missing
- ID number reused by entry with differing phonetics
- Phonetics reused by entry with differing ID
- Phonetic characters within allowable range
- Synonym and Antonyms one way link only
- Date in unusual format
- Entry missing ID
- Example missing translation
- Entered by missing

## Features
- Help page - shouldn't be Jinja - should be standalone html so it can be 
viewed even if user can't launch Python (helping first time users)
- create .dic (does libre office make use of .dic files?)
- Hyperlinks to synonms, antonyms and see all
- Create Anki .apkg from the dictionary data
- Text parser to look for missing words
- Interlinerizer? Could be useful, might not be

## Spreadsheet editing
- Make any links 2 way
- Check words used in examples are in the dict

## Bug fixes
- When filtering the html dict letters with no hits shouldn't show

## Testing
- Finish thinking through and scaffolding the neccesary tests
- Write the tests

# Kovol specific features
- Predict verb endings for a given root
- Identify regular and irregular verbs
- Identify missing paradigm entries

