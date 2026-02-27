import re

VOICE_COMMANDS = [
    ("exclamation point", "!"),
    ("exclamation mark", "!"),
    ("question mark", "?"),
    ("open parenthesis", "("),
    ("open parentheses", "("),
    ("close parenthesis", ")"),
    ("close parentheses", ")"),
    ("open quote", '"'),
    ("open quotes", '"'),
    ("open quotation", '"'),
    ("open quotations", '"'),
    ("close quote", '"'),
    ("close quotes", '"'),
    ("close quotation", '"'),
    ("close quotations", '"'),
    ("period", "."),
    ("comma", ","),
    ("colon", ":"),
    ("semicolon", ";"),
    ("hyphen", "-"),
    ("dash", " -- "),
    ("ellipsis", "..."),
]


def process_voice_commands(text: str) -> str:
    """Replace spoken punctuation commands with actual characters."""
    result = text
    for phrase, replacement in VOICE_COMMANDS:
        # Consume any punctuation Whisper added around the voice command
        # e.g. "Carlos, period." → "Carlos." not "Carlos,.. "
        pattern = re.compile(
            r"[.,!?;:]*\s*" + re.escape(phrase) + r"\s*[.,!?;:]*",
            re.IGNORECASE,
        )
        result = pattern.sub(replacement, result)

    # Clean up whitespace before punctuation
    result = re.sub(r"\s+([.,!?;:])", r"\1", result)
    # Ensure space after punctuation when followed directly by a word
    result = re.sub(r"([.,!?;:])(\w)", r"\1 \2", result)
    # Capitalize after sentence-ending punctuation
    result = re.sub(
        r"([.!?])\s+(\w)", lambda m: m.group(1) + " " + m.group(2).upper(), result
    )
    # Capitalize first character
    if result:
        result = result[0].upper() + result[1:]

    return result.strip()
