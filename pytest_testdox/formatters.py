import os
import re
from typing import List

TRIM_SPACES_REGEX = r'(^[\s]+|[\s]+$)'


def format_title(title, patterns: List[str]):
    return _remove_patterns(title, patterns).replace('_', ' ').strip()


def format_class_name(class_name: str, patterns: List[str]):
    formatted = ''

    class_name = _remove_patterns(class_name, patterns)

    for index, letter in enumerate(class_name):
        if letter.isupper() and _has_lower_letter_besides(index, class_name):
            formatted += ' '

        formatted += letter

    return formatted.strip()


def format_module_name(module_name: str, patterns: List[str]):
    return format_title(module_name.split('/')[-1], patterns)


def format_result_str(outcome: str, node_str: str):
    lines = node_str.split(os.linesep)
    if len(lines) == 1:
        return outcome + node_str

    characters_length = len(outcome)
    result = []
    result.append(outcome + lines[0])

    for line in lines[1:]:
        if not line:
            continue

        pad = len(line) + characters_length
        result.append(line.rjust(pad))

    return os.linesep.join(result)


def trim_multi_line_text(text: str):
    return re.sub(TRIM_SPACES_REGEX, '', text, flags=re.MULTILINE)


def include_parametrized(title: str, original_title: str):
    first_bracket = original_title.find('[')
    last_bracket = original_title.rfind(']')

    has_parameters = last_bracket > first_bracket

    if not has_parameters:
        return title

    parameters = original_title[first_bracket + 1 : last_bracket]

    return '{title}[{parameters}]'.format(title=title, parameters=parameters)


def _remove_patterns(statement: str, patterns: List[str]):
    for glob_pattern in patterns:
        pattern = glob_pattern.replace('*', '')

        if glob_pattern.startswith('*'):
            pattern = '{}$'.format(pattern)
            statement = re.sub(pattern, '', statement)

        elif glob_pattern.endswith('*'):
            pattern = '^{}'.format(pattern)
            statement = re.sub(pattern, '', statement)

        elif '*' in glob_pattern:
            infix_patterns = glob_pattern.split('*', 2)
            infix_patterns[0] = '{}*'.format(infix_patterns[0])
            infix_patterns[1] = '*{}'.format(infix_patterns[1])
            statement = _remove_patterns(statement, infix_patterns)

        else:
            pattern = '^{}'.format(pattern)
            statement = re.sub(pattern, '', statement)

    return statement


def _has_lower_letter_besides(index: int, string: str):
    letter_before = string[index - 1] if index > 0 else ''
    letter_after = string[index + 1] if index < len(string) - 1 else ''

    return letter_before.islower() or letter_after.islower()
