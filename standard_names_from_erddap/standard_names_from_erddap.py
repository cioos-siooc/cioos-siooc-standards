#!/usr/bin/env python

import pandas as pd

"""

Queries a list of ERDDAP servers and returns all of the standard names used

eg. python get_standard_names.py

"""

csv_file="standard_names.csv"

# I didn't include development servers

standard_names_combined_servers = []
cioos_erddap_servers = pd.read_csv("cioos_erddap_servers.csv")

for i,row in cioos_erddap_servers.iterrows():
    cioos_erddap_server=row['erddap_server_url']
    standard_names_url = cioos_erddap_server + "/categorize/standard_name/index.csv"

    print("Querying", standard_names_url)

    standard_names = pd.read_csv(standard_names_url)[["Category"]].rename(
        columns={"Category": "standard_name"}
    )
    standard_names_combined_servers.append(standard_names)

print("Writing ", csv_file)

# Write unique standard names. Remove '_null' entry
pd.concat(standard_names_combined_servers).query('standard_name!="_null"').drop_duplicates().sort_values(by="standard_name").to_csv(
    csv_file, index=False
)
