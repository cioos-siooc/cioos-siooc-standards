import requests
import xmltodict
import pandas as pd

"""
This Module present a set of tool useful to retrieve standard_name and related information from 
the cf convention website. https://cfconventions.org/
"""

def get_cf_names(output_format='dataframe', version=77):

    url = 'https://cfconventions.org/Data/cf-standard-names/{0}/src/cf-standard-name-table.xml'.format(version)
    response = requests.get(url,
                            stream=True)

    response.raw.decode_content = True

    # Convert to a dictionary
    cf_dict = xmltodict.parse(response.text)

    if output_format == dict:
        return cf_dict
    elif output_format == 'dataframe':
        # Convert to dataframes: Retrieve first both cf and alias and combine them together within on dataframe
        df_cf_alias = pd.DataFrame(cf_dict['standard_name_table']['alias'])
        df_cf_alias = df_cf_alias.rename({'@id': 'alias', 'entry_id': '@id'}, axis='columns').groupby('@id').agg(
            ','.join).reset_index()

        df_cf = pd.DataFrame(cf_dict['standard_name_table']['entry'])

        return df_cf.merge(df_cf_alias, on='@id')