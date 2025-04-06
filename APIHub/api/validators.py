import re
from rest_framework.exceptions import ValidationError

class GarbageValueValidator:

    def __init__(self, field_name="Поле", min_length=2, language="any", required=False):
        self.field_name = field_name
        self.min_length = min_length
        self.language = language
        self.required = required

        self.garbage_patterns = [
            r'^[\W_]+$',
            r'^[A-Za-zА-Яа-я]{1}$',
            r'^(.)\1{2,}$',
            r'^(тест|test|example)$',
            r'^\d{5,}$',
        ]

    def __call__(self, value):
        if not value or not str(value).strip():
            if self.required:
                raise ValidationError(f"{self.field_name} обязательно для заполнения.")
            return

        value = str(value).strip()

        if len(value) < self.min_length:
            raise ValidationError(f"{self.field_name} должно содержать не менее {self.min_length} символов.")

        for pattern in self.garbage_patterns:
            if re.match(pattern, value.lower()):
                raise ValidationError(f"{self.field_name} содержит недопустимое или бессмысленное значение.")

        if self.language == "latin" and not re.search(r'[A-Za-z]', value):
            raise ValidationError(f"{self.field_name} должно содержать латинские буквы.")
        elif self.language == "cyrillic" and not re.search(r'[А-Яа-я]', value):
            raise ValidationError(f"{self.field_name} должно содержать кириллические символы.")
