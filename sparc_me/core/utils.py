import os
import json
import shutil
import openpyxl
import pandas as pd
from pathlib import Path

from xlrd import XLRDError


def check_row_exist(dataframe, unique_column, unique_value):
    """Check if a row exist with given unique value

    :param dataframe: metadata dataframe that must be checked
    :type dataframe: Pandas DataFrame
    :param unique_value: value that can be used to uniquely identifies a row
    :type unique_value: string
    :return: row index of the row identified with the unique value, or -1 if there is no row corresponding to the unique value
    :rtype: int
    :raises ValueError: if more than one row can be identified with given unique value
    """
    row_index = dataframe.index[dataframe[unique_column] == unique_value].tolist()
    if not row_index:
        row_index = -1
    elif len(row_index) > 1:
        error_msg = "More than one row can be identified with given unique value"
        raise ValueError(error_msg)
    else:
        row_index = row_index[0]
    return row_index



def get_sub_folder_paths_in_folder(folder_path):
    """
    get sub folder paths in a folder
    :param folder_path: the parent folder path
    :type folder_path: str
    :return: list
    """
    folder = Path(folder_path)
    sub_folders = []
    for item in folder.iterdir():
        if item.is_dir():
            sub_folders.append(item)

    return sub_folders


def validate_sub_sam_name(validate_str, validate_type):
    v_4 = validate_str[:4]
    if validate_type == "sub":
        v_str = "sub-"
    elif validate_type == "sam":
        v_str = "sam-"
    else:
        error_msg = f"The validate_type should be 'sub' or 'sam', you provide validate_type is {validate_type}"
        raise ValueError(error_msg)
    if v_4 == v_str:
        return validate_str
    else:
        return f"{v_str}{validate_str}"
