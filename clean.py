# import libraries here; add more as necessary
import numpy as np
import pandas as pd
import json


from sklearn.impute import SimpleImputer


# Split "Value" column
def convert_str_float(x):
    arr = []
    if isinstance(x, list):
        try:
            for i in x:
                arr.append(int(i))
        except ValueError:
            arr.append(i)
    
    return arr if len(arr) > 0 else np.nan

def clean_metadata(DIAS_att_vals_path, DIAS_info_level_path):
    """
    Clean metadata with predefined steps.
    Args:
        - DIAS_att_vals_path: Path for DIAS Attributes and Values
        - DIAS_info_level_path: Path for DIAS for information levels.
    """
    # Load data
    att_vals = pd.read_excel(DIAS_att_vals_path, sheet_name=0, usecols="B:E", header=1)
    info_lvl = pd.read_excel(DIAS_info_level_path, sheet_name=0, usecols="B:E", header=1)

    # CLEAN att_vals

    # replace … with np.NaN
    att_vals.loc[:, "Value"].replace('…', np.nan, inplace=True)

    # forward fill na
    att_vals.loc[:, "Attribute"].fillna(method="ffill", inplace=True)
    att_vals.loc[:, "Description"].fillna(method="ffill", inplace=True)
    att_vals.loc[:, "Meaning"].fillna(method="ffill", inplace=True)

    # Prepare `Value`
    att_vals.loc[:, 'Value'] = att_vals['Value'].astype(str).replace('nan', np.nan)
    att_vals.loc[:, "Value"] = att_vals["Value"].str.split(', ').apply(convert_str_float)

    # CLEAN info_lvl
    # Forward fill NaN for Information Level
    info_lvl.loc[:, "Information level"].fillna(method="ffill", inplace=True)

    # divide `info_lvl` into 2 df to apply fixing on.
    correct_attr = info_lvl[~info_lvl['Attribute'].str.contains(' ')].copy()
    incorrect_attr = info_lvl[info_lvl['Attribute'].str.contains(' ')].copy()

    # extract false values
    pattern = '(\w+ \w+|\w+)\s+(\w+ \w+|\w+)'
    extracted_attrs = incorrect_attr["Attribute"].str.extract(pattern)

    # Combine extracted values and their associated information
    incorrect_attr.drop(columns='Attribute', inplace=True)
    incorrect_attr = pd.concat(
        [incorrect_attr, extracted_attrs], axis=1
    )

    # stack, clean, and standardlize incorrect_attr
    incorrect_attr = incorrect_attr.set_index(["Description", "Information level"]).stack().reset_index()
    incorrect_attr = incorrect_attr.rename({0: 'Attribute'}, axis=1).drop(columns='level_2')
    incorrect_attr.loc[:, 'Attribute'].replace(' ', '', regex=True, inplace=True)

    # concat incorrect_attr and correct_attr and finalize info_lvl
    info_lvl = pd.concat([correct_attr, incorrect_attr], sort=False).sort_values(by=['Information level', 'Attribute'])

    # JOIN att_vals AND info_lvl
    all_info = att_vals.merge(info_lvl.drop(columns=["Description"]), how='outer', on='Attribute')
    order = ["Information level", "Attribute", "Value", "Meaning", "Description", "Additional notes"]
    all_info = all_info.reindex(columns=order)

    return all_info


def load_metadata(all_info_path):
    """
    Function to combine all steps to read metadata.
    Args:
        - all_info_path: The path of description file.
    """
    all_info = pd.read_csv(all_info_path)
    all_info.loc[:, 'Value'] = all_info['Value'].str.replace("[\[\]]", '', regex=True).str.split(', ').apply(convert_str_float)

    return all_info


def clean_demographics(df, all_info_df, del_rows=True):
    """
    Clean demographics data with predefined steps.
    Note: for `customers`, need to remove three columns 'CUSTOMER_GROUP',
        'ONLINE_PURCHASE', 'PRODUCT_GROUP' before applying this function.
    Args:
        - df: Dataframe to clean
        - all_info_df: Dataframe which stores Attributes, its values and descriptions
        - del_rows: boolean to check if we remove row from `df` or not.
    """
    # drop index column
    df.drop(columns='LNR', inplace=True)

    # filter unknown values and get their associated attributes
    cond = all_info_df["Meaning"].str.contains("unknown", na=False)
    att_unks = all_info_df[cond][['Attribute', 'Value']]

    # Construct attribute_unknowns (att_unks) dictionary for replacing values.
    att_unks = att_unks.groupby("Attribute").sum()

    att_unks = json.loads(
        att_unks.to_json(orient="columns")
    )['Value']

    # Convert string to int and reformat the dict for correct format to be used in pd.replace function
    # refer https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.replace.html for details.
    att_unks = {
        key: {
            int(x): np.nan
            for x in att_unks[key]
        } 
        for key, val in att_unks.items()
    }

    # replace both df with `att_unks`
    df.replace(att_unks, inplace=True)

    # drop columns which are high in number of nulls
    to_drop = ['ALTER_KIND4', 'TITEL_KZ', 'ALTER_KIND3', 'ALTER_KIND2',
                'ALTER_KIND1', 'AGER_TYP', 'EXTSEL992', 'KK_KUNDENTYP',
                'KBA05_BAUMAX']
    df.drop(columns=to_drop, inplace=True)

    # Drop rows have more than 5% null.
    if del_rows:
        max_null_percent_for_row = 0.05
        null_by_row = df.isnull().mean(axis=1)
        df.drop(
            list(
                null_by_row[null_by_row > max_null_percent_for_row].index.values
            ),
            inplace=True
        )

    # handle invalid values and convert categorical column to numeric type
    df.loc[:, 'CAMEO_DEUG_2015'].replace('X', np.nan, inplace=True)
    df.loc[:, 'CAMEO_DEUG_2015'] = df.loc[:, 'CAMEO_DEUG_2015'].astype(float, copy=False)
    df.loc[:, 'CAMEO_INTL_2015'].replace('XX', np.nan, inplace=True)
    df.loc[:, 'CAMEO_INTL_2015'] = df.loc[:, 'CAMEO_INTL_2015'].astype(float, copy=False)
    df.loc[:, 'OST_WEST_KZ'] = df.loc[:, 'OST_WEST_KZ'].map({'W': 0, 'O': 1})

    # Convert datetime-like column to datetime and extract 'year' component
    df.loc[:, 'year'] = pd.DatetimeIndex(df['EINGEFUEGT_AM']).year
    df.drop(columns='EINGEFUEGT_AM', inplace=True)

    # Convert categorical column to numeric type
    df = pd.get_dummies(df, columns=['D19_LETZTER_KAUF_BRANCHE', 'CAMEO_DEU_2015'])

    # Fill NaN values in each column with their most frequent value
    imputer = SimpleImputer(strategy="most_frequent")

    df_cols = list(df.columns)
    df_imp = imputer.fit_transform(df)
    df = pd.DataFrame(df_imp, columns=df_cols)

    # drop highly correlated columns
    highly_correlated_cols = ['CAMEO_INTL_2015', 'ANZ_STATISTISCHE_HAUSHALTE', 'PLZ8_GBZ',
                              'LP_LEBENSPHASE_GROB', 'LP_FAMILIE_GROB', 'PLZ8_HHZ',
                              'KBA13_HERST_SONST', 'LP_STATUS_GROB', 'KBA13_KMH_250']
    df.drop(columns=highly_correlated_cols, inplace=True)
    
    return df