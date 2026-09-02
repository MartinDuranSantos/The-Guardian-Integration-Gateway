import re


class PiiSanitizer:
    """
    Robust sanitizer that detects and redacts:
      • Email addresses
      • Credit card numbers (13–19 digits with optional separators)
      • SSNs (###-##-#### or exactly 9 consecutive digits)
    """

    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b'
    )

    CREDIT_CARD_PATTERN = re.compile(
        r'\b(?:\d[ -]*?){13,19}\b'
    )

    SSN_PATTERN = re.compile(
        r'\b\d{3}-\d{2}-\d{4}\b|\b(?<!\d)\d{9}(?!\d)\b'
    )

    @classmethod
    def sanitize(cls, text: str) -> tuple[str, list[str]]:
        redactions_found = []
        sanitized = text

        if cls.CREDIT_CARD_PATTERN.search(sanitized):
            sanitized = cls.CREDIT_CARD_PATTERN.sub('<REDACTED: CREDIT_CARD>', sanitized)
            redactions_found.append('CREDIT_CARD')

        if cls.SSN_PATTERN.search(sanitized):
            sanitized = cls.SSN_PATTERN.sub('<REDACTED: SSN>', sanitized)
            redactions_found.append('SSN')

        if cls.EMAIL_PATTERN.search(sanitized):
            sanitized = cls.EMAIL_PATTERN.sub('<REDACTED: EMAIL>', sanitized)
            redactions_found.append('EMAIL')

        return sanitized, list(dict.fromkeys(redactions_found))