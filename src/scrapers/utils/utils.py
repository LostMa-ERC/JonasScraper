import re


def parse_id(url: str) -> str:
    pattern = r"\/(\d+)$|=(\d+)$"
    match = re.search(pattern=pattern, string=url)
    try:
        m1, m2 = match.group(1, 2)
        if m1:
            return m1
        else:
            return m2
    except Exception as e:
        print(url)
        raise e


def clean(t: str | None) -> str:
    if t:
        t = re.sub(r"\s{2,}", " ", t)
        return t.strip()
