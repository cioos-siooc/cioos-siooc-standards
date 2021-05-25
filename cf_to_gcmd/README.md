# CF to GCMD Python Module

This Python module converts from CF to GCMD using ERDDAP's conversion text file which can be found at <https://raw.githubusercontent.com/BobSimons/erddap/master/WEB-INF/classes/gov/noaa/pfel/erddap/util/CfToGcmd.txt>

## Installation

Setup your Python3 virtual environment;

`python3 -m venv venv; source venv/bin/activate`

Install:

`pip install -e .`

## Build a CSV from the command line

Write cf_to_gcmd.csv in the working directory.

`python -m cf_to_gcmd`

## Usage in Python

```python
from cf_to_gcmd.build_cf_to_gcmd import build_gcmd_to_cf_mapping

cf_to_gcmd_mapping = build_gcmd_to_cf_mapping()

print(cf_to_gcmd_mapping['age_of_surface_snow'])

# ['Earth Science > Cryosphere > Snow/Ice > Snow Stratigraphy', 'Earth Science > Terrestrial Hydrosphere > Snow/Ice > Snow Stratigraphy']
```
