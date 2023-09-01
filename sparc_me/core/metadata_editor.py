import re
import pandas as pd


class MetadataEditor:
    def __init__(self, category, metadata):
        self.category = category
        self.metadata = metadata

    def add_values(self, *values, row_name='', header='', append=False):
        """
        Set single cell. The row is identified by the given unique name and column is identified by the header.
        :param values: field value
        :type values: *str
        :param row_name: Unique row name in Excel. (Ex: if subjects is category, a row name can be a unique subjet id)
        :type row_name: str
        :param header: column name. the header is the first row
        :type header: str
        :return: updated dataset
        :rtype: dict
        """
        if self.category == "dataset_description":
            if row_name == '':
                return
            else:
                if header == '':
                    header = 'Value'
            excel_row_index = self._find_row_index(row_name)
            self.set_row_fields(*values, row_index=excel_row_index, header=header, append=append)

    def remove_values(self, *values, field_name):
        """
        :param values: field value
        :type values: *str
        :param row_name: Unique row name in Excel. (Ex: if subjects is category, a row name can be a unique subjet id)
        :type row_name: str
        :return:
        """
        excel_row_index = self._find_row_index(field_name)
        self.remove_row_fields(*values, field_index=excel_row_index)

    def set_row_fields(self, *values, row_index, header, append=False):
        """
        Set single field by row idx/name and column name (the header)

        :param row_index: row index in Excel. Excel index starts from 1 where index 1 is the header row. so actual data index starts from 2
        :type row_index: int
        :param header: column name. the header is the first row
        :type header: str
        :param value: field value
        :type value: *str
        :return: updated dataset
        :rtype: dict
        """
        insert_header = header
        if not isinstance(row_index, int):
            msg = "row_index should be 'int'."
            raise ValueError(msg)

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
                        self.metadata.insert(last_value_col_index + 1, f"Value{1}", None)
                    else:
                        try:
                            self.metadata.insert(last_value_col_index + 1, f"Value{int(value_header_order) + 1}", None)
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

    def remove_row_fields(self, *values, field_index):
        # get all values from this row
        current_values = self._get_values(field_index)
        row_index = field_index-2
        for value in values:
            if value in current_values.tolist():
                self.metadata.fillna('None', inplace=True)
                column_with_value = self.metadata.loc[field_index-2].eq(value)
                self.metadata.loc[field_index-2, column_with_value] = 'None'
        self.metadata[self.metadata == 'None'] = pd.NA
    def _remove_spaces_and_lower(self, s):

        return re.sub(r'\s', '', s).lower()

    def _get_values(self, field_index):
        values = ""
        value_header_start = self.metadata.columns.get_loc('Value')
        if self.category == "dataset_description":
            values = self.metadata.iloc[field_index - 2, value_header_start:]
        return values

    def get_values(self, field_name):
        if self.category == "dataset_description":
            excel_row_index = self._find_row_index(field_name)
            return self._get_values(excel_row_index)

    def _find_row_index(self, row_name):
        if not isinstance(row_name, str):
            msg = "row_name should be string."
            raise ValueError(msg)

        # Assumes that all excel files first column contains the unique value field
        # TODO: In version 1, the unique column is not the column 0. Hence, unique column must be specified.
        # This method need to be fixed to accomadate this

        elements = self.metadata[self.metadata.columns[0]].tolist()
        row_name_cleaned = self._remove_spaces_and_lower(row_name)

        matching_indices = [index for index, value in enumerate(elements) if
                            self._remove_spaces_and_lower(value) == row_name_cleaned]
        if not matching_indices:
            msg = f"No row with given unique name, {row_name}, was found in the unique column {self.metadata.columns[0]}"
            raise ValueError(msg)
        elif len(matching_indices) > 1:
            msg = f"More than one row with given unique name, {row_name}, was found in the unique column {self.metadata.columns[0]}"
            raise ValueError(msg)
        else:
            excel_row_index = matching_indices[0] + 2
            return excel_row_index

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
                    (idx, unique_header) = self._get_unique_header(idx)
                    try:
                        self.metadata.insert(last_header_index + i + 1, unique_header, None)
                    except ValueError:
                        msg = "Please private a correct header, e.g, Value, Value 1, Value 2..."
                        raise ValueError(msg)

    def _get_unique_header(self, idx):
        while True:
            if f"Value {idx}" in self.metadata.columns:
                idx += 1
            else:
                return (idx, f"Value {idx}")
