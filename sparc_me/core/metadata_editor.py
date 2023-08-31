import re

class MetadataEditor:
    def __init__(self, category, metadata):
        self.category = category
        self.metadata = metadata

    def add_values(self, row_name, header, values, append=False):
        """
        Set single cell. The row is identified by the given unique name and column is identified by the header.

        :param row_name: Unique row name in Excel. (Ex: if subjects is category, a row name can be a unique subjet id)
        :type row_name: string
        :param header: column name. the header is the first row
        :type header: string
        :param values: field value
        :type values: string or list
        :return: updated dataset
        :rtype: dict
        """

        if not isinstance(row_name, str):
            msg = "row_name should be string."
            raise ValueError(msg)

        # Assumes that all excel files first column contains the unique value field
        # TODO: In version 1, the unique column is not the column 0. Hence, unique column must be specified.
        # This method need to be fixed to accomadate this

        elements = self.metadata[self.metadata.columns[0]].tolist()
        row_name_cleaned = self._remove_spaces_and_lower(row_name)

        matching_indices = [index for index, value in enumerate(elements) if self._remove_spaces_and_lower(value) == row_name_cleaned]

        # matching_indices = self.metadata.index[self.metadata[self.metadata.columns[0]]==row_name].tolist()

        if not matching_indices:
            msg = f"No row with given unique name, {row_name}, was found in the unique column {self.metadata.columns[0]}"
            raise ValueError(msg)
        elif len(matching_indices)>1:
            msg = f"More than one row with given unique name, {row_name}, was found in the unique column {self.metadata.columns[0]}"
            raise ValueError(msg)
        else:
            excel_row_index = matching_indices[0] + 2
            return self.set_row_fields( row_index=excel_row_index, header=header, values=values)

    def set_row_fields(self, row_index, header, values):
        """
        Set single field by row idx/name and column name (the header)

        :param category: metadata category
        :type category: string
        :param row_index: row index in Excel. Excel index starts from 1 where index 1 is the header row. so actual data index starts from 2
        :type row_index: int
        :param header: column name. the header is the first row
        :type header: string
        :param value: field value
        :type value: string
        :return: updated dataset
        :rtype: dict
        """

        if not isinstance(row_index, int):
            msg = "row_index should be 'int'."
            raise ValueError(msg)

        try:
            #find out column index
            start_column_index = self.metadata.columns.get_loc(header)
            row_index = row_index - 2
            if isinstance(values, str):
                self.metadata.loc[row_index, header] = values
            elif isinstance(values, list):
                self._edit_colume( header, 6)
                print(self.metadata.columns)
                self.metadata.iloc[row_index, start_column_index:start_column_index + len(values)] = values

            else:
                msg = f"Values type {type(values)} is not supported, only support str or str[]"
                raise ValueError(msg)
            # Convert Excel row index to dataframe index: index - 2

        except ValueError:
            msg = "Value error. row does not exists."
            raise ValueError(msg)

    def _remove_spaces_and_lower(self, s):

        return re.sub(r'\s', '', s).lower()

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
        column_index = self.metadata.columns.get_loc(insert_header)
        if self.category == 'dataset_description':
            columns_to_remove = self.metadata.columns[column_index + 1:]
            self.metadata.drop(columns_to_remove, axis=1, inplace=True)

        if operator == "+":
            for i in range(nums):
                idx = i + 1
                self.metadata.insert(column_index + idx, f"Value{idx}", None)
