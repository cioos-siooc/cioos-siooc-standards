import requests
import re

"""
This package regroup multiple tools to leverage some vocabulary related tools integrated within ERDDAP.
"""


def get_erddap_udunits(
    units,
    erddap="https://catalogue.hakai.org/erddap",
    ignore_first_capital_letter=True,
    ignore_parenthesis=True,
):
    """
    Use ERDDAP udunit implementation to convert a unit input to udunit format.
    """
    # Handle a few issues related to UDUNIT
    units = fix_udunit(
        units,
        ignore_first_capital_letter=ignore_first_capital_letter,
        ignore_parenthesis=ignore_parenthesis,
    )

    standardize_string = "/convert/units.txt?STANDARDIZE_UDUNITS="
    return requests.get("{0}{1}{2}".format(erddap, standardize_string, units)).text


def fix_udunit(label, ignore_first_capital_letter=True, ignore_parenthesis=True):
    """
    UDUNITS seems to have some limitations that we're trying to handle here.
    """

    # Lower first letter
    if ignore_first_capital_letter:
        label = label[0].lower() + label[1:]

    # UDUNITS doesn't handle well the terms "(per) cubic" and "(per) square"
    # map_list = {"per cubic": -3, "per square": -2, "cubic": 3, "square": 2}
    map_list = {"cubic": 3, "square": 2}

    # Cubic and Square aren't well handled by udunits
    if "cubic " in label or "square " in label:
        unit_items = re.search(r"(.*)(cubic|square) ([^ ]*)(.*)", label)

        label = "{0}{1}{2}{3}".format(
            unit_items.group(1),
            unit_items.group(3),
            map_list[unit_items.group(2)],
            unit_items.group(4),
        )
    # P06 uses squared for ^2
    if ' squared' in label:
        label = label.replace(' squared', '2')

    # Ignore parenthesis
    if ignore_parenthesis:
        label = re.sub(r"\(.*\)", "", label)

    return label
