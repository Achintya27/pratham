import re
from django.core.exceptions import ValidationError


def validate_no_malicious_content(value):
    """
    Validator to ensure that the input does not contain malicious content.
    """
    # Check for JavaScript code
    js_pattern = re.compile(r'<[a-zA-Z]+script[^\n]*>.*<[a-zA-Z]+/script>', re.IGNORECASE | re.DOTALL)

    unwanted_bash_pattern = re.compile(
        r'`|&&|\|\||;|\$\(|\$\{|<\(|<\{|>\(|>\{|\\\(|\\\{',
        re.IGNORECASE
    )

    # Check for any HTML tags
    html_pattern = re.compile(r'<.*?>', re.DOTALL)

    #Sql Patterns
    unwanted_sql_pattern = re.compile(
        r'\b(?:SELECT|UPDATE|DELETE|INSERT|DROP|CREATE|ALTER | WHERE)\b',
        re.IGNORECASE
    )


    # Combine patterns
    combined_pattern = re.compile('|'.join([js_pattern.pattern, unwanted_bash_pattern.pattern, html_pattern.pattern, unwanted_sql_pattern.pattern]))

    # Check if the input matches any of the patterns
    if combined_pattern.search(value):
        raise ValidationError("Input contains potential malicious content.")


def Min_ValLen(value, min_length = 3):
    if len(value) < min_length:
        raise ValidationError('Input at least 3 char')

def Password_Validation(value):
    if not re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=]).{8,}$', value):
        raise ValidationError("""Password must be include -
                                 uppercase letters: A-Z
                                 lowercase letters: a-z
                                 numbers: 0-9
                                 any of the special characters: @#$%^&+=""")
