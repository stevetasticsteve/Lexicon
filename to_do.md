# To do

## Validation checks
- Phonetic characters within allowable range
- Synonym and Antonyms one way link only
- Date in unusual format

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
- Bandit has taken issue with my assert statements. I've learned that
try/except is more pythonic than asserts so I'll use them

## Implementation questions
- Are the check_processed_data() and check_lexicon_entries() functions necessary?
They assert that the right kind of data is being given to a function, but
is it better to drop them? Functions are unlikely to be called interactively as
an API call - wouldn't it save effort to drop and not maintain these things?


# Kovol specific features
- Predict verb endings for a given root
- Identify regular and irregular verbs
- Identify missing paradigm entries

## Kovol specific bugs
- Lots of whitespace when using the JS filter

