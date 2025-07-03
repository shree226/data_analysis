import pandas as pd
df=pd.read_csv("/workspaces/data_analysis/data/Gujarat_Crop_SeasonWise_Leadership_Benchmarkingseasonwise.csv")
"""
print(df.head(),df.info())

print(df.columns)
print(df.isna().sum())

# Example: average benchmark value by crop
avg_by_crop = df.groupby("Crop")["Production-2024-25  (Lakh Tonnes)"].mean().sort_values(ascending=False)
print(avg_by_crop)
"""
df=df.rename(columns={'Crop':'Crops', 'State':'States'})
#print(df.head())
#print(df.isnull().any())
#print(df[df['Crops'].isna()==1])
# drop any row where 'Crops' is null


# Drop rows with NaN in 'Crops'
df.dropna(subset=["Crops"],inplace=True)

#print(df)
#df['']=df[''].fillna(0)
import numpy as np
#suppose to print all rows wrt any state: df[df['States']=='Goa']
id_cols = ['Crops', 'States', 'Season']

# Get numeric columns (to check for "real" data)
cols_to_check = [col for col in df.columns if col not in id_cols]

# Convert blanks ('', ' ') to NaN
df[cols_to_check] = df[cols_to_check].replace(r'^\s*$', np.nan, regex=True)

# Convert 0 to NaN as well (if 0 means missing in your context)
df[cols_to_check] = df[cols_to_check].replace(0, np.nan)

# Now drop rows where all non-ID columns are NaN
df = df.dropna(subset=cols_to_check, how='all')
print(df)
df.to_csv("/workspaces/data_analysis/data/Gujarat_Crop_CLEANED.csv", index=False)

