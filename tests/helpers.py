import re


def formatted_text_rematch(value_to_test, expected_formatted_text):
    """
    ``expected_formatted_text`` can be regex.
    """
    for value, expected in zip(value_to_test, expected_formatted_text):
        assert value[0] == expected[0]
        print(expected[1], value[1])
        assert re.match(expected[1], value[1])
