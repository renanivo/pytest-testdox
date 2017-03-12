# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re


def format_outcome(outcome):
    return 'x' if outcome == 'passed' else ' '


def format_title(title, patterns):
    return _remove_patterns(
        patterns=patterns,
        statement=title
    ).replace('_', ' ').strip()


def format_class_name(class_name, patterns):
    formatted = ''

    class_name = _remove_patterns(patterns, class_name)

    for letter in class_name:
        if letter.isupper():
            formatted += ' '

        formatted += letter

    return formatted.strip()


def format_module_name(module_name, patterns):
    return format_title(
        _remove_patterns(patterns, module_name),
        patterns
    ).replace('/', '.')


def _remove_patterns(patterns, statement):
    for glob_pattern in patterns:
        pattern = glob_pattern.replace('*', '')

        if glob_pattern.startswith('*'):
            pattern = '{0}$'.format(pattern)
            statement = re.sub(pattern, '', statement)

        elif glob_pattern.endswith('*'):
            pattern = '^{0}'.format(pattern)
            statement = re.sub(pattern, '', statement)

        elif '*' in glob_pattern:
            infix_patterns = glob_pattern.split('*', 2)
            infix_patterns[0] = '{}*'.format(infix_patterns[0])
            infix_patterns[1] = '*{}'.format(infix_patterns[1])
            statement = _remove_patterns(infix_patterns, statement)

        else:
            pattern = '^{0}'.format(pattern)
            statement = re.sub(pattern, '', statement)

    return statement
