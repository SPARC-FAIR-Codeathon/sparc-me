
metadata_files_2_0_0 = ['code_description', 'code_parameters', 'dataset_description', 'manifest', 'performances',
                        'resources',
                        'samples', 'subjects', 'submission']


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


def validate_metadata_file(metadata_file, version="2.0.0"):
    if version == "2.0.0" or version == "2_0_0":
        for item in metadata_files_2_0_0:
            if remove_spaces_and_lower(item) == remove_spaces_and_lower(metadata_file):
                return item

        msg = f"no metadata files match {metadata_file}, please provide a correct one!"
        raise ValueError(msg)
    elif version == "1.2.3" or version == "1_2_3":
        return metadata_file


def find_col_element(element, metadata):
    elements = metadata.data.columns.tolist()
    matching_indices = metadata.validate_input(element, elements)
    if len(matching_indices) == 1:
        return elements[matching_indices[0]]
    else:
        msg = f"No '{element}' valid element is found! Please find correct element in {metadata.metadata_file}.xlsx file."
        raise KeyError(msg)


def remove_spaces_and_lower(s):
    """
    :param s: the str need to deal with
    :type s: str
    :return: a str with lower case and without space, and _
    """

    return re.sub(r'[\s_]', '', s).lower()


# Customise dict

class CaseInsensitiveDict(dict):
    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveDict, self).__init__(*args, **kwargs)
        self._key_map = {key.lower().replace(" ", ""): key for key in self.keys()}

    def __getitem__(self, key):
        original_key = self._key_map.get(key.lower().replace(" ", ""))
        if original_key is not None:
            return super(CaseInsensitiveDict, self).__getitem__(original_key)
        else:
            raise KeyError(key)

    def get(self, key, default=None, pprint=True):
        try:
            if pprint:
                print(json.dumps(self[key], indent=4))
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        self._key_map[key.lower().replace(" ", "")] = key
        super(CaseInsensitiveDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        original_key = self._key_map.get(key.lower().replace(" ", ""))
        if original_key is not None:
            super(CaseInsensitiveDict, self).__delitem__(original_key)
            del self._key_map[key.lower().replace(" ", "")]
