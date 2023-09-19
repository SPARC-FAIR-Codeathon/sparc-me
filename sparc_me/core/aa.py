"""Metadata模块的文档注释"""


class Metadata:
    """
        metadata类的注释
    """
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

    def add_values(self, element, values):
        """
        Append values to the last value

        :param element: a col/row name in Excel
        :type element: str
        :param values: element values from that metadata
        :type values: list | str | int | bool
        :return:
        """
        self._add_values(element, values, append=True)

    def set_values(self, element, values):
        """
        Override the values in that element

        :param element: a col/row name in Excel
        :type element: str
        :param values: element values from that metadata
        :type values: list | str | int | bool
        :return:
        """
        self._add_values(element, values, append=False)

    def _add_values(self, element, values, append):
        """
        Set single cell. The row is identified by the given unique name and column is identified by the header.

        :param element: a col/row name in Excel
        :type element: str
        :param values: element values from that metadata
        :type values: list | str | int | bool
        :param append: insert values into last col or row
        :type append: bool
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