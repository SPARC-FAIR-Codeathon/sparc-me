import os
import json
import shutil
import openpyxl
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from xlrd import XLRDError


# def add_data(source_path, destination_path_list, copy=True, overwrite=False):
def add_data(source_path, dataset_path, subject, sample, data_type="primary", copy=True, overwrite=True):
    """Copy or move data from source folder to destination folder

    :param source_path: path to the original data
    :type source_path: string
    :param destination_path_list: folder path in a list[root, data_pype, subject, sample] to be copied into
    :type destination_path_list: list
    :param copy: if True, source directory data will not be deleted after copying, defaults to True
    :type copy: bool, optional
    :param overwrite: if True, any data in the destination folder will be overwritten, defaults to False
    :type overwrite: bool, optional
    :raises FileExistsError: if the destination folder contains data and overwritten is set to False, this wil be raised.
    """
    destination_path = os.path.join(str(dataset_path), data_type, subject, sample)
    # If overwrite is True, remove existing sample
    print(destination_path)
    if os.path.exists(destination_path):
        if overwrite:
            shutil.rmtree(destination_path)
            os.makedirs(destination_path)
        else:
            if os.path.isdir(source_path):
                raise FileExistsError(
                    "Destination file already exist. Indicate overwrite argument as 'True' to overwrite the existing")
            else:
                fname = os.path.basename(source_path)
                exsiting_files = os.listdir(destination_path)
                if fname in exsiting_files:
                    raise FileExistsError(
                        "Destination file already exist. Indicate overwrite argument as 'True' to overwrite the existing")

    else:
        # Create destination folder
        os.makedirs(destination_path)

    if os.path.isdir(source_path):
        for fname in os.listdir(source_path):
            file_path = os.path.join(source_path, fname)
            if os.path.isdir(file_path):
                # Warn user if a subdirectory exist in the input_path
                print(
                    f"Warning: Input directory consist of subdirectory {source_path}. It will be avoided during copying")
            else:
                move_single_file(file_path=file_path, destination_path=destination_path,
                                 dataset_path=dataset_path, fname=fname, copy=copy)
    else:
        fname = os.path.basename(source_path)
        move_single_file(file_path=source_path, destination_path=destination_path,
                         dataset_path=dataset_path, fname=fname, copy=copy)


def move_single_file(file_path, destination_path, dataset_path, fname, copy):
    if copy:
        # Copy data
        shutil.copy2(file_path, destination_path)
    else:
        # Move data
        shutil.move(file_path, os.path.join(destination_path, fname))
    # Modify the manifest file
    modify_manifest(fname, dataset_path, destination_path)


def modify_manifest(fname, manifest_path, destination_path):
    # Check if manifest exist
    # If can be "xlsx", "csv" or "json"
    files = os.listdir(manifest_path)
    manifest_file_path = [f for f in files if "manifest" in f]
    # Case 1: manifest file exists
    if len(manifest_file_path) != 0:
        manifest_file_path = os.path.join(manifest_path, manifest_file_path[0])
        # Check the extension and read file accordingly
        extension = os.path.splitext(manifest_file_path)[-1].lower()
        if extension == ".xlsx":
            df = pd.read_excel(manifest_file_path)
        elif extension == ".csv":
            df = pd.read_csv(manifest_file_path)
        elif extension == ".json":
            # TODO: Check what structure a manifest json is in
            # Below code assumes json structure is like
            # '{"row 1":{"col 1":"a","col 2":"b"},"row 2":{"col 1":"c","col 2":"d"}}'
            df = pd.read_json(manifest_file_path, orient="index")
        else:
            raise ValueError(f"Unauthorized manifest file extension: {extension}")
    # Case 2: create manifest file
    else:
        # Default extension to xlsx
        extension = ".xlsx"
        # Creat manifest file path
        manifest_file_path = os.path.join(manifest_path, "manifest.xlsx")
        df = pd.DataFrame(columns=['filename', 'description', 'timestamp', 'file type'])

    # Edit manifest
    sample = destination_path.split(os.path.sep)[-1]
    subject = destination_path.split(os.path.sep)[-2]

    file_path = Path(str(os.path.join(destination_path, fname)).replace(str(manifest_path), '')[1:]).as_posix()

    row = {
        'filename': file_path,
        'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        'description': f"File of subject {subject} sample {sample}",
        'file type': os.path.splitext(fname)[-1].lower()[1:]
    }
    row_pd = pd.DataFrame([row])
    df = pd.concat([df, row_pd], axis=0, ignore_index=True)

    # Save editted manifest file
    if extension == ".xlsx":
        df.to_excel(manifest_file_path, index=False)
    elif extension == ".csv":
        df = pd.to_csv(manifest_file_path, index=False)
    elif extension == ".json":
        df = pd.read_json(manifest_file_path, orient="index")
    return


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


def convert_schema_excel_to_json(source_path, dest_path):
    wb = openpyxl.load_workbook(source_path)
    sheets = wb.sheetnames

    schema = dict()
    for sheet in sheets:
        schema[sheet] = dict()
        try:
            element_description = pd.read_excel(source_path, sheet_name=sheet)
        except XLRDError:
            element_description = pd.read_excel(source_path, sheet_name=sheet, engine='openpyxl')

        element_description = element_description.where(pd.notnull(element_description), None)

        for index, row in element_description.iterrows():
            element = row["Element"]
            schema[sheet][element] = dict()
            schema[sheet][element]["Required"] = row["Required"]
            schema[sheet][element]["Type"] = row["Type"]
            schema[sheet][element]["Description"] = row["Description"]
            schema[sheet][element]["Example"] = row["Example"]

    with open(dest_path, 'w') as f:
        json.dump(schema, f, indent=4)


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
