from django.core.exceptions import ValidationError


def validate_person_name(value):
    """Only letters, spaces, dots, apostrophes and hyphens are allowed in a name."""
    for character in value:
        if not character.isalpha() and character not in " .'-":
            raise ValidationError(
                "Use letters only. Spaces, dots and hyphens are allowed between words."
            )


def validate_phone_number(value):
    """A phone number is 7 to 15 digits and may start with a plus sign."""
    digits = value
    if value.startswith("+"):
        digits = value[1:]
    if not digits.isdigit() or len(digits) < 7 or len(digits) > 15:
        raise ValidationError("Enter 7 to 15 digits without spaces, optionally starting with +.")
