import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from tqdm import tqdm

tqdm.pandas()


def get_nvs_variable_info(
    id=None,
    variable=None,
    vocabulary=None,
    nvs_url="http://vocab.nerc.ac.uk/collection/",
    version="current",
    format_output="?_profile=skos&_mediatype=application/ld+json",
):
    """
    Method to parse the json format from the NERC NVS servers
    """
    if id:
        url = id
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

    response = session.get(url + "/" + format_output)
    return response.json()


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
    id,
    only=None,
    vocabularies=None,
):
    """
    Method to retrieve information available within the JSON-LD NERC file format of a specific NERC id.
    """

    if vocabularies is None:
        vocabularies = ["P02", "P06", "P07"]

    # Get all the info for this id
    id_info = get_nvs_variable_info(id)[0]

    # If only one specific is request just give that.
    if only:
        return [_get_section(id_info, item, language) for item in only]

    relationships = ("broader", "related", "narrower")
    # Initialize dictionary
    output = {"@id": id}
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
            output["definition-en"] = _get_language(value, language)

        if key.endswith(relationships):
            relationship = key.rsplit("#")[1]

            for item in id_info[key]:
                for vocab in vocabularies:
                    if "/collection/" + vocab + "/" in item["@id"]:
                        output[vocab + "_" + relationship + "_id"] += [item["@id"]]
    return output
