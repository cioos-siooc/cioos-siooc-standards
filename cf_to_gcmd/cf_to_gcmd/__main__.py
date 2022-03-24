#!/usr/bin/env python3

import pandas as pd
from cf_to_gcmd.build_cf_to_gcmd import build_gcmd_to_cf_mapping

if __name__ == "__main__":
    cf_to_gcmd = build_gcmd_to_cf_mapping()
    csv_file_output = "cf_to_gcmd.csv"
    df = pd.DataFrame.from_dict(cf_to_gcmd, orient="index").reset_index()
    df=df.rename(columns = {'index':'cf_name'})
    
    print("Writing", csv_file_output)
    df.to_csv(csv_file_output,index=False)
