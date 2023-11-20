import re
from datetime import datetime


def parse_mass_hunter_dt(dt_str: str) -> str:
    """Parses out utc and extraneous millisecond places from
    Mass Hunter datetime strings due to non-standard formatting
    in their datetime strings.  Too many millisecond decimal places
    and a colon in the utc field.  E.g.
    2023-03-17 14:19:50.9887083-06:00.
    """
    pattern = re.compile(r".\d+-[0-2]\d:\d\d")  # milliseconds + utc
    ms_utc_portion = pattern.findall(dt_str)
    pattern = re.compile(r".\d{6}")  # truncate to req'd ms length
    ms_portion = pattern.findall(ms_utc_portion[0])
    return dt_str.replace(ms_utc_portion[0], ms_portion[0])


def try_parsing_date(text):
    for fmt in (
        "%d-%b-%y, %H:%M:%S",  # Chemstation ch format
        "%A %B %d %Y %H:%M:%S",  # Thermo raw format
        "%Y%m%d%H%M%S%z",  # cdf format
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            try:
                text = parse_mass_hunter_dt(text)
                fmt = "%Y-%m-%d %H:%M:%S.%f"  # Mass Hunter mod format
                return datetime.strptime(text, fmt)
            except:
                pass
    raise ValueError("no valid date format found")
