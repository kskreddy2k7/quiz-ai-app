import re

WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize whitespace and strip leading/trailing gaps."""

    return WHITESPACE_RE.sub(" ", text).strip()


def summarize_topic(text: str, max_length: int = 80) -> str:
    clean = normalize_text(text)
    if len(clean) <= max_length:
        return clean
    return clean[: max_length - 3].rstrip() + "..."
