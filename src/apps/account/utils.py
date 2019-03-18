from django.contrib.auth import password_validation
from django.utils.html import format_html, format_html_join

def password_validators_help_text_html(password_validators=None):
    """
    Return an HTML string with all help texts of all configured validators
    in an .
    """
    help_texts = password_validation.password_validators_help_texts(password_validators)
    help_items = format_html_join('', '<p class="text-danger">{}</p>', ((help_text,) for help_text in help_texts))
    return format_html('<div>{}</div>', help_items) if help_items else ''
