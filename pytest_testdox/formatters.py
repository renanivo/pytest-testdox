# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re


def format_outcome(outcome):
    return 'x' if outcome == 'passed' else ' '


def format_title(title):
    return re.sub(r'^test_', '', title).replace('_', ' ')


def format_class_name(class_name):
    formatted = ''

    class_name = re.sub(r'^Test', '', class_name)

    for letter in class_name:
        if letter.isupper():
            formatted += ' '

        formatted += letter

    return formatted.strip()


def format_module_name(module_name):
    return format_title(re.sub(r'.py$', '', module_name)).replace('/', '.')
