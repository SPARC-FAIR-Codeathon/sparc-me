import pandas as pd
from pathlib import Path
from sparc_me.core.utils import remove_spaces_and_lower
from abc import ABC, abstractmethod


class Metadata:
    def __init__(self, metadata_file, metadata, version, dataset_path):
        """
        :param metadata_file: metadata file name
        :type metadata_file: str
        :param metadata: metadata dataframe content
        :type metadata: Dataframe
        :param version: dataset version
        :type version: "2.0.0" | "1.2.3"
        :param dataset_path: root dataset path
        :type dataset_path: Path
        """
        self.metadata_file = metadata_file
        self.data = metadata
        self.version = version
        self.metadata_file_path = Path(dataset_path).joinpath(f"{metadata_file}.xlsx")

    """********************************* Add values *********************************"""

    def add_values(self, element, values, append=True):
        """
        Set single cell. The row is identified by the given unique name and column is identified by the header.
        :param values: field values
        :type values: list | str | int | bool
        :param element: a col/row name in Excel
        :type element: str
        :param append: insert values into last col or row
        :type append: bool
        :return: updated dataset
        :rtype: dict
        """
        values = self._validate_input_values(values)
        if self.metadata_file == "dataset_description" or self.metadata_file == "code_description":
            if element == '':
                return
            else:
                col_name = 'Value'
            excel_row_index = self._find_row_index(element)
            self.set_row_values(row_index=excel_row_index, values=values, col_name=col_name, append=append)
        else:
            if element == '':
                # add values by rows start at (0,0)
                # get first header
                header = self.data.columns[0]
                self.set_row_values(row_index=2, values=values, col_name=header, append=append)
            else:
                # add values by header (columns)
                col_index = self._find_col_index(element)
                self.set_col_values(col_index=col_index, values=values, append=append)

    def set_row_values(self, row_index, values, col_name='Value', append=True):
        """
        Set row fields/values by row idx/name and column name (the header)

        :param row_index: row index in Excel. Excel index starts from 1 where index 1 is the header row. so actual data index starts from 2
        :type row_index: int
        :param col_name: column name. the header is the first row
        :type col_name: str
        :param values: field values
        :type values: list | str | int | bool
        :param append: insert values into last col or row
        :type append: bool
        :return: updated dataset
        :rtype: dict
        """
        values = self._validate_input_values(values)
        insert_header = col_name
        if not isinstance(row_index, int):
            msg = "row_index should be 'int'."
            raise ValueError(msg)
        if self.metadata_file == "dataset_description" or self.metadata_file == "code_description":
            try:
                row_index = row_index - 2
                # find out column index
                row_has_null = self.data.iloc[row_index].isnull().any()
                if append:
                    if row_has_null:
                        start_header = (self.data.isnull().idxmax(axis=1))[row_index]
                        insert_header = start_header
                        start_column_index = self.data.columns.get_loc(start_header)
                    else:
                        last_value_col_index = len(self.data.iloc[row_index].values) - 1
                        last_value_col_name = self.data.columns[last_value_col_index]
                        value_header_order = last_value_col_name.replace('Value', '')
                        if value_header_order == '':
                            self.data.insert(last_value_col_index + 1, f"Value {1}", None)
                        else:
                            try:
                                if value_header_order == ' n':
                                    value_header_order = 3
                                self.data.insert(last_value_col_index + 1, f"Value {int(value_header_order) + 1}",
                                                 None)
                            except ValueError:
                                msg = "Please private a correct header, e.g, Value, Value1, Value2..."
                                raise ValueError(msg)

                        insert_header = self.data.columns[-1]
                        start_column_index = last_value_col_index + 1
                else:
                    start_column_index = self.data.columns.get_loc(col_name)

                if len(values) > 0:
                    self._edit_column(insert_header, len(values))
                    self.data.iloc[row_index, start_column_index:start_column_index + len(values)] = values
                else:
                    msg = f"please provide values"
                    raise ValueError(msg)
                # Convert Excel row index to dataframe index: index - 2

            except ValueError:
                msg = "Value error. row does not exists."
                raise ValueError(msg)
        else:
            if append:
                self.data.loc[len(self.data)] = values
            else:
                self.data.loc[-1] = values
                self.data.index = self.data.index + 1
                self.data.sort_index()

    def set_col_values(self, col_index, values, append=True):
        """
        Set col fields/values by col index
        :param values: field values
        :type values: list | str | int | bool
        :param col_index: the header index
        :type col_index: int
        :param append: insert values into last col or row
        :type append: bool
        :return:
        """
        values = self._validate_input_values(values)
        if append:
            if self.data.iloc[:, col_index].isnull().any():
                nan_row_index = self.data[self.data.iloc[:, col_index].isnull()].index[0]
                self.data.iloc[nan_row_index:nan_row_index + len(values), col_index] = values
            else:
                for value in values:
                    new_row = [None] * len(self.data.columns)
                    new_row[col_index] = value
                    self.data.loc[len(self.data)] = new_row
        else:
            if len(self.data) < len(values):
                diff = len(values) - len(self.data)
                for _ in range(diff):
                    self.data.loc[len(self.data)] = None

            for i, value in enumerate(values):
                self.data.iat[i, col_index] = value

    """********************************* Clear & Remove values *********************************"""

    def clear_values(self, element=''):
        """
        :param element:  Unique row/col name in Excel. (Ex: if subjects is metadata_file, a row name can be a unique subjet id)
        :type element: str
        :return:
        """
        if self.metadata_file == "dataset_description" or self.metadata_file == "code_description":
            header_name = 'Value'
            if element == '':
                self.data.fillna('None', inplace=True)
                self.data.drop(columns=self.data.columns[self.data.columns.get_loc(header_name):],
                               inplace=True)
                self.data['Value'] = pd.NA
                if self.metadata_file == "dataset_description":
                    self.add_values(element="Metadata version", values="2.0.0", append=False)
            else:
                excel_row_index = self._find_row_index(element)
                df_row_index = excel_row_index - 2
                header_index = self.data.columns.get_loc(header_name)
                self.data.iloc[df_row_index, header_index:] = pd.NA
        else:
            if element == '':
                self.data.drop(self.data.index, inplace=True)
            else:
                col_index = self._find_col_index(element)
                self.data.iloc[:, col_index] = pd.NA

    def remove_values(self, element, values):
        """
        :param values: field value
        :type values: list | str | int | bool
        :param element: Unique row/col name in Excel.
        :type element: str
        :return:
        """
        validate_values = self._validate_input_values(values)
        if self.metadata_file == "dataset_description" or self.metadata_file == "code_description":
            excel_row_index = self._find_row_index(element)
            self._remove_values(field_index=excel_row_index, values=validate_values)
        else:
            col_index = self._find_col_index(element)
            self._remove_values(field_index=col_index, values=validate_values)

    def remove_row(self, value):
        rows_to_delete = self.data[self.data.eq(value).any(axis=1)]
        self.data.drop(rows_to_delete.index, inplace=True)

    def _remove_values(self, field_index, values):
        """
        :param values: field values
        :type values: list | int | str | bool
        :param field_index: a col/row name index in Excel
        :type field_index: int
        :return:
        """
        # get all values from this row
        excel_field_index = field_index
        current_values = self._get_values(excel_field_index)
        df_field_index = field_index - 2
        for value in values:
            if value in current_values.tolist():
                self.data.fillna('None', inplace=True)
                if self.metadata_file == "dataset_description" or self.metadata_file == "code_description":
                    column_with_value = self.data.loc[df_field_index].eq(value)
                    self.data.loc[df_field_index, column_with_value] = 'None'
                else:
                    self.data.loc[
                        self.data.iloc[:, field_index] == value, self.data.columns[field_index]] = 'None'
        self.data[self.data == 'None'] = pd.NA

    """********************************* Get values *********************************"""

    def get_values(self, element):
        """

        :param element: a col/row name in Excel
        :return:
        """
        if self.metadata_file == "dataset_description" or self.metadata_file == "code_description":
            excel_row_index = self._find_row_index(element)
            return self._get_values(excel_row_index)
        else:
            col_index = self._find_col_index(element)
            return self._get_values(col_index)

    def _get_values(self, field_index):
        """
        :param field_index: a col/row name index in Excel
        :return:
        """
        if self.metadata_file == "dataset_description" or self.metadata_file == "code_description":
            value_header_start = self.data.columns.get_loc('Value')
            values = self.data.iloc[field_index - 2, value_header_start:]
        else:
            values = self.data.iloc[:, field_index]
        return values

    """********************************* Find col/row index *********************************"""

    def _find_row_index(self, row_name):
        """

        :param row_name: a str row name in Excel
        :type row_name: str
        :return:
        """
        elements = self.data[self.data.columns[0]].tolist()
        matching_indices = self._validate_input(row_name, elements)
        if not matching_indices:
            msg = f"No row with given unique name, {row_name}, was found in the unique column {self.data.columns[0]}"
            raise ValueError(msg)
        elif len(matching_indices) > 1:
            msg = f"More than one row with given unique name, {row_name}, was found in the unique column {self.data.columns[0]}"
            raise ValueError(msg)
        else:
            excel_row_index = matching_indices[0] + 2
            return excel_row_index

    def _find_col_index(self, col_name):
        """
        :param col_name: a str col/header name in Excel
        :type col_name: str
        :return:
        """
        elements = self.data.columns.tolist()
        matching_indices = self._validate_input(col_name, elements)
        if len(matching_indices) == 1:
            return matching_indices[0]
        else:
            msg = f"No valid field name is found!"
            raise KeyError(msg)

    """********************************* Edit column *********************************"""

    def _edit_column(self, insert_header, nums, operator='+'):
        """

        :param insert_header: the start header name
        :type insert_header: str
        :param nums: expand or reduce column's numbers
        :type nums: int
        :param operator: identifier for expand(+) or reduce(-) columns
        :type operator: "+" | "-"
        :return:
        """
        start_column_idx = self.data.columns.get_loc(insert_header)
        remain_headers = self.data.columns[start_column_idx:]
        last_header_index = self.data.columns.get_loc(self.data.columns[-1])
        if operator == "+":
            if len(remain_headers) < nums:
                length = nums - len(remain_headers)
                for i in range(length):
                    idx = i + 1
                    (idx, unique_header) = self._create_unique_header(idx)

                    try:
                        self.data.insert(last_header_index + i + 1, unique_header, None)
                    except ValueError:
                        msg = "Please provide a correct header, e.g, Value, Value 1, Value 2..."
                        raise ValueError(msg)

    def _create_unique_header(self, idx):
        while True:
            if f"Value {idx}" in self.data.columns:
                idx += 1
            else:
                return (idx, f"Value {idx}")

    """********************************* Validate inputs *********************************"""

    def _validate_input(self, element, elements):
        """

        :param element: row/col name in excel
        :param elements: dataset metadata elements
        :return:
        """
        if not isinstance(element, str):
            msg = "row_name / col_name should be string."
            raise ValueError(msg)

        # Assumes that all excel files first column contains the unique value field
        # TODO: In version 1, the unique column is not the column 0. Hence, unique column must be specified.
        # This method need to be fixed to accomadate this

        row_name_cleaned = remove_spaces_and_lower(element)
        matching_indices = [index for index, value in enumerate(elements) if
                            remove_spaces_and_lower(value) == row_name_cleaned]
        return matching_indices

    def _validate_input_values(self, values):
        new_values = []
        if isinstance(values, str) or isinstance(values, int) or isinstance(values, bool):
            new_values.append(values)
        elif not isinstance(values, list):
            msg = "Please provide a correct values parameter, if is a single value, use str, int, bool, if multiple values please put values into a list."
            raise TypeError(msg)
        else:
            new_values = values
        return new_values

    """********************************* Save *********************************"""

    def save(self, path=""):
        try:
            if path == "":
                path = self.metadata_file_path

            self.data.to_excel(path, index=False)
        except:
            msg = f"Please provide a correct path for {self.Testmetadata_file}"
            raise ValueError(msg)


class Operator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def set_dataset_root_path(self, path):
        pass

    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def add_values(self):
        pass

    @abstractmethod
    def remove_values(self):
        pass

    @abstractmethod
    def save(self):
        pass


class Sample:
    count = 0
    _dataset_path = Path('./')

    def __init__(self):
        Sample.count += 1
        self.sam_id = f"sam-{Sample.count}"
        self.sub_id = ""
        self.sam_dir = ""
        self.source_sam_dir = ""

    def set_sub_id(self, sub_id):
        self.sub_id = sub_id
        self._generate_sam_path()

    def _generate_sam_path(self):
        self.sam_dir = self._dataset_path.joinpath("primary", self.sub_id, self.sam_id)

    def get_dataset_path(self):
        return self._dataset_path

    def get_sample_id(self):
        return self.sam_id

    def add(self, source_path, metadata={}):
        self.source_sam_dir = source_path
        metadata["subject id"] = self.sub_id
        metadata["sample id"] = self.sam_id


    def add_values(self):
        pass

    def remove_values(self):
        pass

    def save(self):
        pass
