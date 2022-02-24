import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import warnings

import pandas as pd
import os

from tqdm.auto import tqdm
# Create new `pandas` methods which use `tqdm` progress
# (can use tqdm_gui, optional kwargs, etc.)
tqdm.pandas()

from . import erddap


def get_nvs_variable_info(
        nerc_id=None,
        variable=None,
        vocabulary=None,
        nvs_url="http://vocab.nerc.ac.uk/collection/",
        version="current",
        api_output="?_profile=skos&_mediatype=application/ld+json",
        output_format='dataframe'
):
    """
    Method to retrieve information from the NERC NVS servers through the default ld+json format.
    """
    if nerc_id:
        url = nerc_id
    else:
        # Define the base of the URL
        url = nvs_url + "/" + vocabulary + "/" + version

        # Add the optional variable
        if variable:
            url = url + "/" + variable

    # Get the response from the NERC servers
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    response = session.get(url + "/" + api_output)
    if output_format == 'json':
        return response.json()

    elif output_format == 'dataframe':
        # Convert to DataFrame
        df = pd.DataFrame(response.json())

        # Extract information from each columns
        for var in df.columns:
            if df[var].dtype != object:
                continue
            item_type = type(df[var].iloc[0])

            # Define new variable
            if '#' in var:
                new_var = var.split('#')[1]
            else:
                new_var = var

            # Generate new variables based on type
            # Create a new column for each language
            if item_type == list and '@language' in df[var][0][0]:
                df_lang = df[var].apply(lambda x: {item['@language']: item['@value'] for item in x}).apply(pd.Series)
                for lang in df_lang.columns:
                    df[new_var + '-' + lang] = df_lang[lang]
            # Group each values in a comma separated list
            elif item_type == list and '@value' in df[var][0][0]:
                df[new_var] = df[var].apply(lambda x: ','.join([y['@value'] for y in x]))
            # Group ids in a list
            elif item_type == list and '@id' in df[var][0][0]:
                df[new_var] = df[var].apply(lambda x: [y['@id'] for y in x])

        return df
    else:
        raise RuntimeError('Unknown output format: {0}'.format(output_format))


def split_nerc_id(id_url):
    """
    Small method to parse the NERC url for each variables to extract information
    """
    # Split the order ids to extract name and vocab
    id_list = id_url.split("/")
    val = [
        "http",
        "empty",
        "nerc_url",
        "type",
        "vocabulary",
        "version",
        "variable",
        "unknown",
    ]
    return dict(zip(val, id_list))


def _get_language(item_list, language="en"):
    """
    Retrieve from a NERC term json section the specified language (default= english)
    """
    if type(language) is str:
        return [item["@value"] for item in item_list if item["@language"] == language][
            0
        ]
    elif type(language) is list:
        return {
            item["@language"]: item["@value"]
            for item in item_list
            if item["@language"] in language
        }


def _get_section(vocabulary, section, language="en"):
    """
    More general tool that retrieve data from a given section of the NERC term json.
    """
    for name, item in vocabulary.items():
        if name.endswith(section):
            if "@language" in item[0]:
                return _get_language(item, language)
            elif "@value" in item[0] and len(item) == 1:
                return item[0]["@value"]
            else:
                return item


def get_nerc_id_info(
        nerc_id,
        only=None,
        vocabularies=None,
):
    """
    Method to retrieve information available within the JSON-LD NERC file format of a specific NERC nerc_id.
    """

    if vocabularies is None:
        vocabularies = ["P02", "P06", "P07"]

    # Get all the info for this nerc_id
    id_info = get_nvs_variable_info(nerc_id)[0]

    # If only one specific is request just give that.
    if only:
        return [_get_section(id_info, item) for item in only]

    relationships = ("broader", "related", "narrower")
    # Initialize dictionary
    output = {"@nerc_id": nerc_id}
    for vocab in vocabularies:
        for relationship in relationships:
            output[vocab + "_" + relationship + "_id"] = []

    for key, value in id_info.items():

        if key.endswith("prefLabel"):
            output["prefLabel"] = value[0]["@value"]

        if key.endswith("altLabel"):
            output["altLabel"] = value[0]["@value"]

        if key.endswith("definition"):
            # Get English Definition
            output["definition-en"] = _get_language(value)

        if key.endswith(relationships):
            relationship = key.rsplit("#")[1]

            for item in id_info[key]:
                for vocab in vocabularies:
                    if "/collection/" + vocab + "/" in item["@nerc_id"]:
                        output[vocab + "_" + relationship + "_id"] += [item["@nerc_id"]]
    return output


def _generate_p06_table(output_path=None):
    """
    Method to Generate the P06 Reference Table.
    """
    df = get_nvs_variable_info(vocabulary="P06")

    # Convert all P06 to udunits
    df["udunits"] = df["prefLabel"].progress_apply(erddap.get_erddap_udunits)

    # Save to csv file
    keep_columns = ["@id", "prefLabel", "udunits"]

    if output_path:
        df[keep_columns].to_csv(output_path)
    elif output_path == 'update':
        df[keep_columns].to_csv(os.path.join(os.path.dirname(__file__), "NERC_P06_to_UDUNITS.csv"), index=False)

    return df


def get_p06_units_id(unit, reference_table_path=None, output='id'):
    """
    Compare units provided to P06 list and return matching term.
    """
    if reference_table_path is None:
        reference_table_path = os.path.join(os.path.dirname(__file__), "NERC_P06_to_UDUNITS.csv")

    # Convert units to udunit format
    unit = erddap.get_erddap_udunits(unit)

    # Load P06 Table
    p06 = pd.read_csv(reference_table_path)

    # Compare terms
    matching_term = p06.loc[p06["udunits"] == unit]
    if output == 'id':
        if len(matching_term) == 0:
            return None
        if len(matching_term) == 1:
            return matching_term["@id"].values[0]
        if len(matching_term) > 1:
            warnings.warn("Multiple matches for {0}".format(unit))
            return ",".join(matching_term["@id"].values)
    else:
        return matching_term

