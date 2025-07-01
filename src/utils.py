import re

import ural
from pydantic import BaseModel

from src.models.manuscript import Manuscript
from src.models.work import Work


def parse_url(url: str) -> tuple[str | None, BaseModel | None]:
    url = ural.strip_protocol(url)
    id = parse_id(url)
    paths = ural.urlpathsplit(url)
    if "oeuvre" in paths:
        url_type = Work
    elif "manuscrit" in paths:
        url_type = Manuscript
    else:
        url_type = None
    return id, url_type


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
