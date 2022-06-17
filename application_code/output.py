# This file contains functions that output data by calling on functions in process_data. This is the
# third and final layer. HTML pages and Phonology assistant databases can be produced

import datetime
import logging
import os

from jinja2 import Environment, FileSystemLoader

try:
    import lexicon_config
except ModuleNotFoundError:
    import example_lexicon_config as lexicon_config
from application_code import process_data

logger = logging.getLogger("LexiconLog")


def assert_templates_exist(template_dir="templates"):
    templates = [
        "dictionary_template.html",
        "error_template.html",
    ]
    partial_templates = [
        "base.html",
        "entry.html",
        "header.html",
        "paradigm.html",
        "verb_entry.html",
    ]

    partial_templates = ["partial/" + t for t in partial_templates]
    templates = templates + partial_templates

    try:
        for template in templates:
            template = os.path.join(template_dir, template)
            if not os.path.exists(template):
                raise FileNotFoundError
        return True
    except FileNotFoundError:
        msg = 'Template: "{template}" not found'.format(template=template)
        logger.exception(msg)
        raise FileNotFoundError(msg)


def generate_html(processed_data, verb_data=None):
    """Generate the HTML pages"""
    assert_templates_exist()
    errors = process_data.validate_data(processed_data)

    generate_lexicon_page(processed_data, errors, verb_data=verb_data)
    logger.info("HTML pages sucessfully generated")
    if errors:
        generate_error_page(errors)
        logger.info("   - an error page has been generated")


def generate_lexicon_page(processed_data, errors, verb_data=None):
    """Create suitable headwords for a dictionary and create a dictionary HTML page"""
    process_data.check_processed_data(processed_data, "generate_HTML()")

    # Create the HTML header and navbar
    context = generate_context(
        title="{language} Lexicon".format(language=lexicon_config.settings["language"]),
        header="lexicon",
    )

    lexicon_entries = process_data.create_lexicon_entries(
        processed_data, verb_data=verb_data
    )
    initial_letters = process_data.get_word_beginnings(lexicon_entries)
    half_letters = len(initial_letters) / 2

    file_loader = FileSystemLoader("templates")
    env = Environment(loader=file_loader, autoescape=True)
    template = env.get_template("dictionary_template.html")

    html = os.path.join(lexicon_config.settings["target_folder"], "main_dict.html")
    with open(html, "w", encoding="utf-8") as file:
        print(
            template.render(
                context=context,
                entries=lexicon_entries,
                errors=errors,
                letters=initial_letters,
                half_letters=half_letters,
            ),
            file=file,
        )


def generate_error_page(errors):
    """Creates a page that shows all the validation errors discovered in the spreadsheet"""

    file_loader = FileSystemLoader("templates")
    env = Environment(loader=file_loader, autoescape=True)
    template = env.get_template("error_template.html")

    context = generate_context(title="Data errors", header="errors")
    html = os.path.join(lexicon_config.settings["target_folder"], "errors.html")

    with open(html, "w", encoding="utf-8") as file:
        print(template.render(context=context, errors=errors), file=file)


def generate_context(title, header):
    date = datetime.datetime.now().strftime("%A %d %B %Y")
    context = {
        "title": title,
        "date": date,
        "language": lexicon_config.settings["language"],
        "header": header,
        "bootstrap": lexicon_config.settings.get("bootstrap"),
        "jquery": lexicon_config.settings.get("jquery"),
        "fontawesome": lexicon_config.settings.get("fontawesome"),
    }

    return context
