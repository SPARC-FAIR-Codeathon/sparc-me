
"""aa模块的文档注释"""


class Aa(object):
    """
        Aa类的注释
    """

    @staticmethod
    def aa_api(x, y):
        """
        求商
        :param x: 整数
        :param y: 不能为零的整数
        :return: 两数之商
        """
        return x / y
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
                    self.set_values(element="Metadata version", values="2.0.0")
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
        matching_indices = self.validate_input(row_name, elements)
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
        matching_indices = self.validate_input(col_name, elements)
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

    def validate_input(self, element, elements):
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
        """
        Save the metadata file to dataset dir

        :param path: the dataset root path (Optional)
        :type path: str
        """
        try:
            if path == "":
                path = self.metadata_file_path
            self.data.to_excel(path, index=False)
        except:
            msg = f"Please provide a correct path for {self.metadata_file}"
            raise ValueError(msg)


class Sample:
    count = 0
    _dataset_path: Path = Path('./')
    _metadata: Metadata = None
    _manifest_metadata: Metadata = None
    _previous_sub_id = ""


    def __init__(self):
        self.sample_id = ""
        self.subject_id = ""
        self.sample_dir = Path()
        self.source_sample_paths: List[Path] = []
        self.index = -1

    def set_subject_id(self, sub_id):
        """
        set subject id to sample object
        :param sub_id: a subject id
        :type sub_id: str
        """
        self.subject_id = sub_id
        if sub_id != Sample._previous_sub_id:
            Sample._previous_sub_id = sub_id
            Sample.count = 0
        self._generate_sample_path_and_id()

    def _generate_sample_path_and_id(self):
        """
        Generate sample path and id
        """
        subject_dir = self._dataset_path.joinpath("primary", self.subject_id)
        if subject_dir.exists():
            sub_dirs = []
            for sub_dir in subject_dir.iterdir():
                if sub_dir.is_dir():
                    sub_dirs.append(sub_dir.name)
            while True:
                Sample.count += 1
                self.sample_id = f"sam-{Sample.count}"
                if self.sample_id not in sub_dirs:
                    break
        else:
            Sample.count += 1
            self.sample_id = f"sam-{Sample.count}"

        self.sample_dir = subject_dir.joinpath(self.sample_id)
        self._add_sample_row()

    def get_sample_id(self):
        """
        Get sample id
        :return: sample id
        """
        return self.sample_id

    def _add_sample_row(self):
        """
        Add row in sample metadata
        """
        df = self._metadata.data
        if self.sample_id in df['sample id'].values and self.subject_id in df['subject id']:
            self.index = df.loc[df['sample id'] == self.sample_id].index[0]
        else:
            sample = [self.sample_id, self.subject_id] + [float('nan')] * (len(df.columns) - 2)
            # Create new row
            self.index = len(df)
            df.loc[self.index] = sample

    def add_path(self, source_path):
        """
        Add sample source path to sample object

        :param source_path: sample folder source path
        :type source_path: str | list

        """
        if isinstance(source_path, list):
            for file_path in source_path:
                self.source_sample_paths.append(Path(file_path))
        else:
            self.source_sample_paths.append(Path(source_path))


    def set_path(self, source_path):
        """
        Add sample source path to sample object
        Override the Previous path

        :param source_path: sample folder source path
        :type source_path: str | list

        """
        if isinstance(source_path, list):
            self.source_sample_paths = []
            for file_path in source_path:
                self.source_sample_paths.append(Path(file_path))
        else:
            self.source_sample_paths = [Path(source_path)]


    def set_values(self, metadata={}):
        """
        :param metadata: key : value dict (element:value)
        :type metadata: dict
        """
        if not isinstance(metadata, dict):
            msg = f"You should use a dict here, you provide parameter type is {type(metadata)}"
            raise TypeError(msg)

        for element, value in metadata.items():
            if element == 'sample id' or element == 'subject id':
                continue
            else:
                self.set_value(element, value)

    def set_value(self, element, value):
        """
        Set value for one element for a sample

        :param element: element in sample metadata file
        :type element: str
        :param value: the values for that element
        :type value: str|int

        """
        df = self._metadata.data
        index = df.loc[(df['sample id'] == self.sample_id) & (df['subject id'] == self.subject_id)].index[0]
        element = find_col_element(element, self._metadata)
        if index == self.index:
            df.loc[index, element] = value

        self.save()

    def move(self):
        """
        Move sample files from source dir to dataset primary dir

        """
        if not self.sample_dir.exists():
            self.sample_dir.mkdir(parents=True, exist_ok=True)

        for source_sam in self.source_sample_paths:
            if source_sam.is_dir():
                source_sample_files = source_sam.rglob("*")
                for file in source_sample_files:
                    if file.is_file():
                        relative_path = file.relative_to(source_sam)
                        target_file = self.sample_dir / relative_path
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(str(file), str(target_file))
                        self._update_manifest(sample_path=str(target_file))
            elif source_sam.is_file():
                shutil.copy(str(source_sam), str(self.sample_dir))
                self._update_manifest(sample_path=str(self.sample_dir / source_sam.name))
    def _update_manifest(self, sample_path):
        """
        Update manifest metadata, after remove samples

        :param sample_path: sample path
        :type sample_path: str
        """
        file_path = Path(
            sample_path.replace(str(self._dataset_path), '')[1:]).as_posix()

        row = {
            'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            'description': f"File of subject {self.subject_id} sample {self.sample_id}",
            'file type': Path(sample_path).suffix
        }

        df_manifest = self._manifest_metadata.data
        # check is exist
        if file_path in df_manifest['filename'].values:
            manifest_index = df_manifest.loc[df_manifest['filename'] == file_path].index[0]
        else:
            manifest_row = [file_path] + [float('nan')] * (len(df_manifest.columns) - 1)
            # Create new row
            manifest_index = len(df_manifest)
            df_manifest.loc[manifest_index] = manifest_row

        for element, value in row.items():
            validate_element = find_col_element(element, self._manifest_metadata)
            df_manifest.loc[manifest_index, validate_element] = value

        self._manifest_metadata.save()

    def remove_values(self):
        """
        Future function
        """
        pass

    def save(self):
        """
        Save sample metadata file

        """
        self._metadata.save()

class Subject:
    count = 0
    _dataset_path = Path('./')
    _metadata = None

    def __init__(self):

        self.subject_id = ""
        self.subject_dir = Path()
        self.index = -1
        self._samples = {}
        self._generate_subject_path_and_id()

    def get_sample(self, sample_sds_id) -> Sample:
        """
        Provide the sample sds id to query a sample for edit

        :param sample_sds_id: the sample id in sds
        :return: Sample
        """
        if not isinstance(sample_sds_id, str):
            msg = f"Sample not found, please provide an string sample_sds_id!, you sample_sds_id type is {type(sample_sds_id)}"
            raise ValueError(msg)

        try:
            sample = self._samples.get(sample_sds_id)
            return sample
        except:
            msg = f"Sample not found with {sample_sds_id}! Please check your subject_sds_id in subject metadata file"
            raise ValueError(msg)

    def _generate_subject_path_and_id(self):
        """
        generate subject id and path in dataset

        """
        primary_dir = self._dataset_path.joinpath("primary")
        if primary_dir.exists():
            sub_dirs = []
            for sub_dir in primary_dir.iterdir():
                if sub_dir.is_dir():
                    sub_dirs.append(sub_dir.name)
            while True:
                Subject.count += 1
                self.subject_id = f"sub-{Subject.count}"
                if self.subject_id not in sub_dirs:
                    break
        else:
            Subject.count += 1
            self.subject_id = f"sub-{Subject.count}"
        self.subject_dir = primary_dir.joinpath(self.subject_id)
        self._add_subject_row()

    def add_samples(self, samples):
        """
        Add samples into subject object

        :param samples: a samples list
        :type samples: list
        """
        if isinstance(samples, list):
            for sample in samples:
                if isinstance(sample, Sample):
                    self._create_sample(sample)
                    self._samples[sample.sample_id] = sample
        elif isinstance(samples, Sample):
            self._create_sample(samples)
            self._samples[samples.sample_id] = samples

    def _create_sample(self, sample):
        """
        Generate sample id and subject id in sample class
        :param sample: a sample object
        :type sample: Sample
        """
        sample.set_subject_id(self.subject_id)

    def _add_subject_row(self):
        """
        Add row in subject metadata file

        """
        df = self._metadata.data
        if self.subject_id in df['subject id']:
            self.index = df.loc[df['subject id'] == self.subject_id].index[0]
        else:
            subject = [self.subject_id] + [float('nan')] * (len(df.columns) - 1)
            # Create new row
            self.index = len(df)
            df.loc[self.index] = subject

    def set_values(self, metadata={}):
        """
        :param metadata: key : value dict (element:value)
        :type metadata: dict
        """
        if not isinstance(metadata, dict):
            msg = f"You should use a dict here, you provide parameter type is {type(metadata)}"
            raise TypeError(msg)

        for element, value in metadata.items():
            if element == 'subject id':
                continue
            else:
                self.set_value(element, value)

    def set_value(self, element, value):
        """
        Set value for one element for a subject

        :param element: element in sample metadata file
        :type element: str
        :param value: the values for that element
        :type value: str|int
        """
        df = self._metadata.data
        index = df.loc[df['subject id'] == self.subject_id].index[0]
        element = find_col_element(element, self._metadata)
        if index == self.index:
            df.loc[index, element] = value

        self.save()

    def move(self):
        for sample in self._samples.values():
            sample.move()

    def remove_values(self):
        pass

    def save(self):
        self._metadata.save()

