import re


def clean(t: str | None) -> str:
    if t:
        t = re.sub(r"\s{2,}", " ", t)
        return t.strip()
