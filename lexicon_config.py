settings = {
    'language': 'Kovol',
    'spreadsheet_name': '/media/NAS/Team Share/Kovol_lexicon.ods',  # the abs path to the spreadsheet used as a data source
    'sheet_name': 'Sheet1',  # Name of the sheet containing data
    'target_folder': '/media/NAS/CLAHub/other_sites/Lexicon/',  # the folder the web page should be created in,
    'log_file': '/media/NAS/CLAHub/other_sites/Lexicon/Lexicon_error.log',  # the abs path for the log file
    # 'sort': 'phonetics',  # order dictionary by 'phonetics' or 'orthography'
    'stylesheets': './stylesheets',
    # the path to the stylesheet folder
    'verb_spreadsheet': '/media/NAS/Team Share/Kovol_verbs.ods'
}

spreadsheet_config = {
    'id_col': 'A',  # Column containing id number
    'orth_col': 'B',  # Column containing orthographic text
    'phon_col': 'C',  # Column containing phonetics
    'dial_col': 'D',  # Column containing dialect variant phonetics
    'sense_col': 'E',  # Column containing sense number
    'pos_col': 'F',  # Column containing part of speech
    'eng_col': 'G',  # Column containing English translation
    'tpi_col': 'H',  # Column containing Tok Pisin translation
    'def_col': 'I',  # Column containing a definition
    'ex_col': 'J',  # Column containing example(s)
    'trans_col': 'K',  # Column containing example translation
    'date_col': 'L',  # Column containing entry date
    'enter_col': 'M',  # Column containing team member who entered data
    'check_col': 'N',  # Column containing team member who checked
    'syn_col': 'O',  # Column containing synonyms
    'ant_col': 'P',  # Column containing antonyms
    'link_col': 'Q',  # Column containing links,
    'tag_col': 'R',  # Column containing semantic tags
}
