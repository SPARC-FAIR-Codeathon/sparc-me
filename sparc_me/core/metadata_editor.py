import re
import pandas as pd
from pathlib import Path

class MetadataEditor:
    def __init__(self, category, metadata, dataset_path):
        """
        :param category: metadata file name
        :type category: str
        :param metadata: metadata dataframe content
        :type metadata: Dataframe
        :param dataset_path: root dataset path
        :type dataset_path: Path
        """
        self.category = category
        self.metadata = metadata
        self.category_path = Path(dataset_path).joinpath(f"{category}.xlsx")

    def add_values(self, *values, row_name='', header='', append=True):
        """
        Set single cell. The row is identified by the given unique name and column is identified by the header.
        :param values: field value
        :type values: *str
        :param row_name: Unique row name in Excel. (Ex: if subjects is category, a row name can be a unique subjet id)
        :type row_name: str
        :param header: column name. the header is the first row
        :type header: str
        :param append: insert values into last col or row
        :type append: bool
        :return: updated dataset
        :rtype: dict
        """
        if self.category == "dataset_description" or self.category == "code_description":
            if row_name == '':
                return
            else:
                if header == '':
                    header = 'Value'
            excel_row_index = self._find_row_index(row_name)
            self.set_row_values(*values, row_index=excel_row_index, header=header, append=append)
        else:
            if header == '':
                # add values by rows start at (0,0)
                # get first header
                header = self.metadata.columns[0]
                self.set_row_values(*values, row_index=2, header=header, append=append)
            else:
                # add values by header (columns)
                col_index = self._find_col_index(header)
                self.set_col_values(*values, col_index=col_index, append=append)

    def remove_values(self, *values, field_name):
        """
        :param values: field value
        :type values: *str
        :param field_name: Unique row/col name in Excel.
        :type field_name: str
        :return:
        """
        if self.category == "dataset_description" or self.category == "code_description":
            excel_row_index = self._find_row_index(field_name)
            self._remove_values(*values, field_index=excel_row_index)
        else:
            col_index = self._find_col_index(field_name)
            self._remove_values(*values, field_index=col_index)

    def clear_values(self, field_name=''):
        """
        :param field_name:  Unique row/col name in Excel. (Ex: if subjects is category, a row name can be a unique subjet id)
        :type field_name: str
        :return:
        """
        if self.category == "dataset_description" or self.category == "code_description":
            header_name = 'Value'
            if field_name == '':
                self.metadata.fillna('None', inplace=True)
                self.metadata.drop(columns=self.metadata.columns[self.metadata.columns.get_loc(header_name):],
                                   inplace=True)
                self.metadata['Value'] = pd.NA
            else:
                excel_row_index = self._find_row_index(field_name)
                df_row_index = excel_row_index - 2
                header_index = self.metadata.columns.get_loc(header_name)
                self.metadata.iloc[df_row_index, header_index:] = pd.NA
        else:
            if field_name == '':
                self.metadata.drop(self.metadata.index, inplace=True)
            else:
                col_index = self._find_col_index(field_name)
                self.metadata.iloc[:, col_index] = pd.NA

    def set_row_values(self, *values, row_index, header='Value', append=True):
        """
        Set row fields/values by row idx/name and column name (the header)

        :param row_index: row index in Excel. Excel index starts from 1 where index 1 is the header row. so actual data index starts from 2
        :type row_index: int
        :param header: column name. the header is the first row
        :type header: str
        :param values: field values
        :type values: *str
        :param append: insert values into last col or row
        :type append: bool
        :return: updated dataset
        :rtype: dict
        """
        insert_header = header
        if not isinstance(row_index, int):
            msg = "row_index should be 'int'."
            raise ValueError(msg)
        if self.category == "dataset_description" or self.category == "code_description":
            try:
                row_index = row_index - 2
                # find out column index
                row_has_null = self.metadata.iloc[row_index].isnull().any()
                if append:
                    if row_has_null:
                        start_header = (self.metadata.isnull().idxmax(axis=1))[row_index]
                        insert_header = start_header
                        start_column_index = self.metadata.columns.get_loc(start_header)
                    else:
                        last_value_col_index = len(self.metadata.iloc[row_index].values) - 1
                        last_value_col_name = self.metadata.columns[last_value_col_index]
                        value_header_order = last_value_col_name.replace('Value', '')
                        if value_header_order == '':
                            self.metadata.insert(last_value_col_index + 1, f"Value {1}", None)
                        else:
                            try:
                                if value_header_order == ' n':
                                    value_header_order = 3
                                self.metadata.insert(last_value_col_index + 1, f"Value {int(value_header_order) + 1}",
                                                     None)
                            except ValueError:
                                msg = "Please private a correct header, e.g, Value, Value1, Value2..."
                                raise ValueError(msg)

                        insert_header = self.metadata.columns[-1]
                        start_column_index = last_value_col_index + 1
                else:
                    start_column_index = self.metadata.columns.get_loc(header)

                if len(values) > 0:
                    self._edit_colume(insert_header, len(values))
                    self.metadata.iloc[row_index, start_column_index:start_column_index + len(values)] = values
                else:
                    msg = f"please provide values"
                    raise ValueError(msg)
                # Convert Excel row index to dataframe index: index - 2

            except ValueError:
                msg = "Value error. row does not exists."
                raise ValueError(msg)
        else:
            if append:
                self.metadata.loc[len(self.metadata)] = values
            else:
                self.metadata.loc[-1] = values
                self.metadata.index = self.metadata.index + 1
                self.metadata.sort_index()

    def set_col_values(self, *values, col_index, append=True):
        """
        Set col fields/values by col index
        :param values: field values
        :type values: *str
        :param col_index: the header index
        :type col_index: int
        :param append: insert values into last col or row
        :type append: bool
        :return:
        """
        if append:
            if self.metadata.iloc[:, col_index].isnull().any():
                nan_row_index = self.metadata[self.metadata.iloc[:, col_index].isnull()].index[0]
                self.metadata.iloc[nan_row_index:nan_row_index + len(values), col_index] = values
            else:
                for value in values:
                    new_row = [None] * len(self.metadata.columns)
                    new_row[col_index] = value
                    self.metadata.loc[len(self.metadata)] = new_row
        else:
            if len(self.metadata) < len(values):
                diff = len(values) - len(self.metadata)
                for _ in range(diff):
                    self.metadata.loc[len(self.metadata)] = None

            for i, value in enumerate(values):
                self.metadata.iat[i, col_index] = value
    def remove_row(self, value):
        rows_to_delete = self.metadata[self.metadata.eq(value).any(axis=1)]
        self.metadata.drop(rows_to_delete.index, inplace=True)

    def _remove_values(self, *values, field_index):
        """
        :param values: field values
        :type values: *str
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
                self.metadata.fillna('None', inplace=True)
                if self.category == "dataset_description" or self.category == "code_description":
                    column_with_value = self.metadata.loc[df_field_index].eq(value)
                    self.metadata.loc[df_field_index, column_with_value] = 'None'
                else:
                    self.metadata.loc[
                        self.metadata.iloc[:, field_index] == value, self.metadata.columns[field_index]] = 'None'
        self.metadata[self.metadata == 'None'] = pd.NA

    def _remove_spaces_and_lower(self, s):
        """
        :param s: the str need to deal with
        :type s: str
        :return: a str with lower case and without space
        """

        return re.sub(r'\s', '', s).lower()

    def _get_values(self, field_index):
        """
        :param field_index: a col/row name index in Excel
        :return:
        """
        if self.category == "dataset_description" or self.category == "code_description":
            value_header_start = self.metadata.columns.get_loc('Value')
            values = self.metadata.iloc[field_index - 2, value_header_start:]
        else:
            values = self.metadata.iloc[:, field_index]
        return values

    def get_values(self, field_name):
        """

        :param field_name: a col/row name in Excel
        :return:
        """
        if self.category == "dataset_description" or self.category == "code_description":
            excel_row_index = self._find_row_index(field_name)
            return self._get_values(excel_row_index)
        else:
            col_index = self._find_col_index(field_name)
            return self._get_values(col_index)

    def _validate_input(self, field_name, elements):
        """

        :param field_name: row/col name in excel
        :param elements: dataset metadata elements
        :return:
        """
        if not isinstance(field_name, str):
            msg = "row_name / col_name should be string."
            raise ValueError(msg)

        # Assumes that all excel files first column contains the unique value field
        # TODO: In version 1, the unique column is not the column 0. Hence, unique column must be specified.
        # This method need to be fixed to accomadate this

        row_name_cleaned = self._remove_spaces_and_lower(field_name)
        matching_indices = [index for index, value in enumerate(elements) if
                            self._remove_spaces_and_lower(value) == row_name_cleaned]
        return matching_indices

    def _find_row_index(self, row_name):
        """

        :param row_name: a str row name in Excel
        :type row_name: str
        :return:
        """
        elements = self.metadata[self.metadata.columns[0]].tolist()
        matching_indices = self._validate_input(row_name, elements)
        if not matching_indices:
            msg = f"No row with given unique name, {row_name}, was found in the unique column {self.metadata.columns[0]}"
            raise ValueError(msg)
        elif len(matching_indices) > 1:
            msg = f"More than one row with given unique name, {row_name}, was found in the unique column {self.metadata.columns[0]}"
            raise ValueError(msg)
        else:
            excel_row_index = matching_indices[0] + 2
            return excel_row_index

    def _find_col_index(self, header):
        """
        :param header: a str col/header name in Excel
        :type header: str
        :return:
        """
        elements = self.metadata.columns.tolist()
        matching_indices = self._validate_input(header, elements)
        if len(matching_indices) == 1:
            return matching_indices[0]
        else:
            msg = f"No valid field name is found!"
            raise ValueError(msg)

    def _edit_colume(self, insert_header, nums, operator='+'):
        """

        :param insert_header: the start header name
        :type insert_header: str
        :param nums: expand or reduce column's numbers
        :type nums: int
        :param operator: identifier for expand(+) or reduce(-) columns
        :type operator: "+" | "-"
        :return:
        """
        start_column_idx = self.metadata.columns.get_loc(insert_header)
        remain_headers = self.metadata.columns[start_column_idx:]
        last_header_index = self.metadata.columns.get_loc(self.metadata.columns[-1])
        if operator == "+":
            if len(remain_headers) < nums:
                length = nums - len(remain_headers)
                for i in range(length):
                    idx = i + 1
                    (idx, unique_header) = self._create_unique_header(idx)

                    try:
                        self.metadata.insert(last_header_index + i + 1, unique_header, None)
                    except ValueError:
                        msg = "Please provide a correct header, e.g, Value, Value 1, Value 2..."
                        raise ValueError(msg)

    def _create_unique_header(self, idx):
        while True:
            if f"Value {idx}" in self.metadata.columns:
                idx += 1
            else:
                return (idx, f"Value {idx}")

    def save(self, path=""):
        try:
            if path == "":
                path = self.category_path

            self.metadata.to_excel(path, index=False)
        except:
            msg = f"Please provide a correct path for {self.category}"
            raise ValueError(msg)
