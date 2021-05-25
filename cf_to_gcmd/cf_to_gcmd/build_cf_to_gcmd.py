#!/usr/bin/env python3

import requests


def build_gcmd_to_cf_mapping():
    """
    Build dictionary that maps from CF name to a list of GCMD.

    Eg, cf_to_gcmd['age_of_surface_snow'] =
        ['Earth Science > Cryosphere > Snow/Ice > Snow Stratigraphy',
        'Earth Science > Terrestrial Hydrosphere > Snow/Ice > Snow Stratigraphy'
        ]
    """

    erddap_github_cf_to_gcmd_url = "https://raw.githubusercontent.com/BobSimons/erddap/master/WEB-INF/classes/gov/noaa/pfel/erddap/util/CfToGcmd.txt"

    keyword_sections = (
        requests.get(erddap_github_cf_to_gcmd_url).content.decode().split("\n\n")
    )

    cf_to_gcmd = {}
    for keyword_section in keyword_sections:
        keyword_section_lines = keyword_section.split("\n")
        cf_name = keyword_section_lines[0]
        gcmd_keywords = []
        if len(keyword_section_lines) > 1:
            gcmd_keywords = keyword_section_lines[1:]
        cf_to_gcmd[cf_name] = gcmd_keywords
    return cf_to_gcmd


