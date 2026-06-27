from django.core.exceptions import ValidationError


class UppercaseValidator:
    def validate(self, password, user=None):
        if not any(c.isupper() for c in password):
            raise ValidationError(
                'Password must contain at least one uppercase letter.',
                code='password_no_upper',
            )

    def get_help_text(self):
        return 'Your password must contain at least one uppercase letter.'


class NumberValidator:
    def validate(self, password, user=None):
        if not any(c.isdigit() for c in password):
            raise ValidationError(
                'Password must contain at least one number.',
                code='password_no_number',
            )

    def get_help_text(self):
        return 'Your password must contain at least one number.'
