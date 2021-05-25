import xml.etree.ElementTree as ET
import json
from urllib import request, parse
from erddapy import ERDDAP
import os
import pathlib
import erddapy
import pandas as pd
import argparse

# https://cfconventions.org/Data/cf-standard-names/77/src/cf-standard-name-table.xml

erddap_list = [
    {"name":"CIOOS Atlantic", "url":"https://cioosatlantic.ca/erddap"},
    {"name":"CIOOS SLGO", "url":"https://erddap.preprod.ogsl.ca/erddap"},
    {"name":"CIOOS Pacific", "url":"https://data.cioospacific.ca/erddap"},
]

cf_df = None

def build_cf_df(cf_source):
    xml_data = open(cf_source, encoding="UTF-8", mode='r').read()
    root = ET.XML(xml_data)

    cf_entires = []
    for i, child in enumerate(root.findall('entry')):
        cf_entires.append({"cf_name": child.attrib["id"], "alias_of" : ""})

    df_entires = pd.DataFrame(cf_entires)

    cf_alias = []
    for i, child in enumerate(root.findall('alias')):
        alias = child.find("entry_id")
        cf_alias.append({"cf_name": child.attrib["id"], "alias_of" : alias.text})

    df_alias = pd.DataFrame(cf_alias)

    df_complete = df_entires.append(df_alias, ignore_index=True)
    return df_complete


def get_keywords(erddap_url):
    url = erddap_url["url"] + "/categorize/keywords/index.csv"

    print("Source: %s, %s" % (erddap_url["name"], url))

    df = pd.read_csv(url)

    cf_intersection = pd.merge(cf_df, df, how='inner', left_on="cf_name", right_on="Category")
    cf_intersection["source_ra"] = erddap_url["name"]

    # print(cf_intersection.info())
    print("Intersection of CF Names found in Keywords")
    print(cf_intersection)
    print("\n\n")

    return cf_intersection



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cf_source",
        help="Path to the CF source file to use",
        action="store",
        default="sources/cf/77/cf-standard-name-table.xml"
    )

    # parser.add_argument(
    #     "-",
    #     "--",
    #     help="Optional Argument",
    #     default="default value",
    #     action="store",
    # )

    prog_args = parser.parse_args()

    cf_df = build_cf_df(prog_args.cf_source)
        
    print(cf_df.info())
    print(cf_df)

    intersections = None
    for url in erddap_list:
        result = get_keywords(url)

        try:
            intersections = intersections.append(result, ignore_index=True)
        except AttributeError:
            intersections = result

    print(intersections.info())
    print(intersections)

    intersections.to_csv("cf_names_in_keywords.csv", columns=["source_ra", "cf_name", "alias_of", "URL"], index=False)



