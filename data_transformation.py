import pandas as pd
import re


def mapper(mapping: dict, to_discard: list, df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns in a DataFrame and optionally drop specified columns.

    This function renames columns in the input DataFrame according to the provided mapping
    and drops columns specified in the to_discard list.

    Parameters:
    mapping (dict): A dictionary where keys are original column names and values are new column names.
    to_discard (list): A list of column names to be dropped from the DataFrame.
    df (pd.DataFrame): The input DataFrame to be modified.

    Returns:
    pd.DataFrame: A new DataFrame with renamed columns and specified columns dropped.
    """
    try:
        df = df.rename(columns=mapping)
        for col in to_discard:
            try:
                df = df.drop(columns=[col])
            except KeyError:
                print(f"Column '{col}' not found in the DataFrame and will be skipped.")
    except KeyError as e:
        print(f"Error: {e}")
        print(
            "Please check the column names in the mapping dictionary and to_discard list."
        )
    return df


def create_mapping(source_columns: list, destination_columns: list) -> dict:
    """
    Create a mapping dictionary from source columns to destination columns.

    This function creates a dictionary that maps source column names to destination column names,
    removing any duplicates in both lists.

    Parameters:
    source_columns (list): A list of source column names.
    destination_columns (list): A list of destination column names.

    Returns:
    dict: A dictionary where keys are unique source column names and values are unique destination column names.
    """
    source = list(dict.fromkeys(source_columns))
    destination = list(dict.fromkeys(destination_columns))
    mapping = dict(zip(source, destination))
    return mapping


def extract_substrings(big_string, substring_list) -> list:
    """
    Extract specified substrings from a larger string.

    This function searches for whole word occurrences of substrings from the provided list
    within the big_string and returns a list of all found substrings.

    Parameters:
    big_string (str): The string to search within.
    substring_list (list): A list of substrings to search for.

    Returns:
    list: A list of substrings found in the big_string, in the order they appear.
    """
    substrings = []
    pattern = r"\b(" + "|".join(map(re.escape, substring_list)) + r")\b"
    for match in re.finditer(pattern, big_string):
        substrings.append(match.group())
    return substrings


def transform_nonstandard_SAP(df: pd.DataFrame, new_column_name: str) -> pd.DataFrame:
    """
    Transform a non-standard SAP-type format DataFrame by grouping rows based on a specific pattern and adding a new column.

    This function processes a DataFrame where the first column acts as a grouper.

    Rows with NaN values in the grouper column indicate the start of a new group.
    The function creates groups based on this pattern,
    assigns the non-NaN values as keys for each group, and adds a new column with these keys.

    Parameters:
    df (pd.DataFrame): Input DataFrame. The first column is used as the grouper column.
    new_column_name (str): Name of the new column to be added, which will contain the group keys.

    Returns:
    pd.DataFrame: A new DataFrame with the following modifications:
        - The grouper column is removed.
        - A new column is added with the name specified by new_column_name, containing the group keys.
        - Rows are grouped according to the pattern in the original grouper column.
    """
    grouper_column = df.columns[0]
    grouper_values = df[grouper_column]
    # Drop the "grouper_column" we don't need it anymore.
    in_df = df.drop(columns=[grouper_column])
    group_defined_list = list(grouper_values.isna())
    index_rows_for_group = []
    keys = []
    results = {}

    # For each entry in our boolean array
    for index, is_group_defined in enumerate(group_defined_list):
        if is_group_defined is True:
            # Have we identified any keys?
            if len(keys) > 0:
                results[tuple(keys)] = index_rows_for_group
                keys = []
                index_rows_for_group = []
            index_rows_for_group.append(index)
        else:
            value = grouper_values[index]
            keys.append(value)

    # Iterate through the results
    # Building the df again with the subsets
    subset_dfs = []
    for value_key, df_indices in results.items():
        subset_df = in_df.loc[df_indices].copy()
        subset_df[new_column_name] = [value_key] * len(subset_df)
        subset_dfs.append(subset_df)
    sub_df = pd.concat(subset_dfs)
    return sub_df


def remove_rows_with_nans(df: pd.DataFrame, threshold: int = 1) -> pd.DataFrame:
    """
    Remove rows from a DataFrame if they contain NaN or NaT values in more than 'threshold' columns.
    
    Parameters:
    df (pandas.DataFrame): The input DataFrame
    threshold (int): The maximum number of columns allowed to have NaN or NaT values. Default is 1.
    
    Returns:
    pandas.DataFrame: A new DataFrame with the specified rows removed
    """
    # Count the number of NaN or NaT values in each row
    nan_counts: pd.Series = df.isna().sum(axis=1)
    
    # Keep rows where the count of NaNs/NaTs is less than or equal to the threshold
    return df[nan_counts <= threshold]

def propagate_value_backwards(series):
    result = series.copy()
    last_konto = None
    for i in range(len(series) - 1, -1, -1):  # Iterate backwards
        if isinstance(series[i], str) and series[i].startswith('Konto'):
            last_konto = series[i]
        elif last_konto is not None:
            result[i] = last_konto
        if isinstance(series[i], str) and series[i].startswith('Konto') and series[i] != last_konto:
            last_konto = None  # Reset when we hit a different Konto value
    return result


# Function to check if a string matches the pattern (e.g., '@5C\Qoffen@')
def is_pattern(x):
    return isinstance(x, str) and x.startswith('@') and x.endswith('@')