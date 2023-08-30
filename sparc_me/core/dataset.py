import os
import shutil
import json
import tempfile

from pathlib import Path
from distutils.dir_util import copy_tree

import pandas as pd
from styleframe import StyleFrame
from xlrd import XLRDError
from sparc_me.core.utils import add_data, check_row_exist

class Dataset(object):
    def __init__(self):
        DEFAULT_DATASET_VERSION = "2.0.0"
        EXTENSIONS = [".xlsx"]

        self._template_version = DEFAULT_DATASET_VERSION
        self._version = DEFAULT_DATASET_VERSION
        self._current_path = Path(__file__).parent.resolve()
        self._resources_path = Path.joinpath(self._current_path, "../resources")
        self._template_dir = Path()
        self._template = dict()

        self._dataset_path = Path()
        self._dataset = dict()
        self._metadata_extensions = EXTENSIONS
        self._column_based = ["dataset_description", "code_description"]
        self._subject_id_field = None
        self._sample_id_field = None

    def set_dataset_path(self, path):
        """
        Set the path to the dataset

        :param path: path to the dataset directory
        :type path: string
        """
        self._dataset_path = Path(path)

    def get_dataset_path(self):
        """
        Return the path to the dataset directory
        :return: path to the dataset directory
        :rtype: string
        """
        return str(self._dataset_path)

    def _get_template_dir(self, version):
        """
        Get template directory path

        :return: path to the template dataset
        :rtype: Path
        """
        version = "version_" + version
        template_dir = self._resources_path / "templates" / version / "DatasetTemplate"

        return template_dir

    def set_template_version(self, version):
        """
        Choose a template version

        :param version: template version
        :type version: string
        """
        version = self._convert_version_format(version)
        self._template_version = version
        self._set_version_specific_variables(version)

    
    def _set_version_specific_variables(self, version):
        """Set version specific variables

        :param version: SDS version to use Ex: 2_0_0
        :type version: string
        :raises ValueError: if the given version is not an acceptable SDS version
        """
        if version == "2_0_0":
            self._subject_id_field = "subject id"
            self._sample_id_field = "sample id"
        elif version == "1_2_3":
            self._subject_id_field = "subject_id"
            self._sample_id_field = "sample_id"
        else:
            error_msg = f"Unsupported version {version}"
            raise ValueError(error_msg)


    def _load(self, dir_path):
        """
        Load the input dataset into a dictionary

        :param dir_path: path to the dataset dictionary
        :type dir_path: string
        :return: loaded dataset
        :rtype: dict
        """
        dataset = dict()

        dir_path = Path(dir_path)
        for path in dir_path.iterdir():
            if path.suffix in self._metadata_extensions:
                try:
                    metadata = pd.read_excel(path)
                except XLRDError:
                    metadata = pd.read_excel(path, engine='openpyxl')

                metadata = metadata.dropna(how="all")
                metadata = metadata.loc[:, ~metadata.columns.str.contains('^Unnamed')]

                key = path.stem
                value = {
                    "path": path,
                    "metadata": metadata
                }
            else:
                key = path.name
                value = path

            dataset[key] = value

        return dataset

    def load_from_template(self, version):
        """
        Load dataset from SPARC template

        :param version: template version
        :type version: string
        :return: loaded dataset
        :rtype: dict
        """
        self.set_version(version)
        self._dataset_path = self._get_template_dir(self._version)
        self._dataset = self._load(str(self._dataset_path))

        return self._dataset

    def _convert_version_format(self, version):
        """
        Convert version format
        :param version: dataset/template version
        :type version: string
        :return: version in the converted format
        :rtype:
        """
        version = version.replace(".", "_")

        if "_" not in version:
            version = version + "_0_0"

        return version

    def set_version(self, version):
        """
        Set dataset version version

        :param version: dataset version
        :type version: string
        """
        version = self._convert_version_format(version)

        self._version = version
        self._set_version_specific_variables(version)

    def load_template(self, version):
        """
        Load template

        :param version: template version
        :type version: string
        :return: loaded template
        :rtype: dict
        """

        version = self._convert_version_format(version)
        self.set_template_version(version)
        self._template_dir = self._get_template_dir(self._template_version)
        self._template = self._load(str(self._template_dir))

        return self._template

    def save_template(self, save_dir, version=None):
        """
        Save the template directory locally

        :param save_dir: path to the output folder
        :type save_dir: string
        :param version: template version
        :type version: string
        """
        if version:
            version = self._convert_version_format(version)
            template_dir = self._get_template_dir(version)
        elif not version and self._template_version:
            template_dir = self._get_template_dir(self._template_version)
        else:
            raise ValueError("Template path not found.")

        copy_tree(str(template_dir), str(save_dir))

    def load_dataset(self, dataset_path=None, from_template=False, version=None):
        """
        Load the input dataset into a dictionary

        :param dataset_path: path to the dataset
        :type dataset_path: string
        :param from_template: whether to load the dataset from a SPARC template
        :type from_template: bool
        :param version: dataset version
        :type version: string
        :return: loaded dataset
        :rtype: dict
        """
        if version:
            self.set_version(version)

        if from_template:
            self._dataset = self.load_from_template(version=version)
        else:
            self._dataset = self._load(dataset_path)

        return self._dataset

    def save(self, save_dir, remove_empty=False):
        """
        Save dataset

        :param save_dir: path to the dest dir
        :type save_dir: string
        :param remove_empty: (optional) If True, remove rows which do not have values in the "Value" field
        :type remove_empty: bool
        """
        if not self._dataset:
            msg = "Dataset not defined. Please load the dataset or the template dataset in advance."
            raise ValueError(msg)

        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        for key, value in self._dataset.items():
            if isinstance(value, dict):
                file_path = Path(value.get("path"))
                filename = file_path.name
                data = value.get("metadata")

                if remove_empty:
                    data = self._filter(data, filename)

                if isinstance(data, pd.DataFrame):
                    self.set_version(self._version)
                    template_dir = self._get_template_dir(self._version)
                    sf = StyleFrame.read_excel_as_template(str(template_dir / filename), data)
                    writer = StyleFrame.ExcelWriter(Path.joinpath(save_dir, filename))
                    sf.to_excel(writer)
                    writer.save()

            elif Path(value).is_dir():
                dir_name = Path(value).name
                dir_path = Path.joinpath(save_dir, dir_name)
                copy_tree(str(value), str(dir_path), update=1)

            elif Path(value).is_file():
                filename = Path(value).name
                file_path = Path.joinpath(save_dir, filename)
                try:
                    shutil.copyfile(value, file_path)
                except shutil.SameFileError:
                    # overwrite file by copy, remove then rename
                    file_path_tmp = str(file_path) + "_tmp"
                    shutil.copyfile(value, file_path_tmp)
                    os.remove(file_path)
                    os.rename(file_path_tmp, file_path)

    def load_metadata(self, path):
        """
        Load & update a single metadata

        :param path: path to the metadata file
        :type path: string
        :return: metadata
        :rtype: Pandas.DataFrame
        """
        path = Path(path)
        try:
            metadata = pd.read_excel(path)
        except XLRDError:
            metadata = pd.read_excel(path, engine='openpyxl')

        filename = path.stem
        self._dataset[filename] = {
            "path": path,
            "metadata": metadata
        }

        return metadata

    def _filter(self, metadata, filename):
        """
        Remove column/row if values not set

        :param metadata: metadata
        :type metadata: Pandas.DataFrame
        :param filename: name of the metadata
        :type filename: string
        :return: updated metadata
        :rtype: Pandas.DataFrame
        """
        if "dataset_description" in filename:
            # For the dataset_description metadata, remove rows which do not have values in the "Value" fields
            metadata = metadata.dropna(subset=["Value"])

        return metadata

    def list_categories(self, version):
        """
        list all categories based on the metadata files in the template dataset

        :param version: reference template version
        :type version: string
        :return: all metadata categories
        :rtype: list
        """
        categories = list()

        self.load_template(version=version)

        for key, value in self._template.items():
            if isinstance(value, dict):
                file_path = Path(value.get("path"))
                category = file_path.stem
                categories.append(category)

        print("Categories:")
        for category in categories:
            print(category)

        return categories

    def list_elements(self, category, axis=0, version=None):
        """
        List field from a metadata file

        :param category: metadata category
        :type category: string
        :param axis: If axis=0, column-based. list all column headers. i.e. the first row.
                     If axis=1, row-based. list all row index. i.e. the first column in each row
        :type axis: int
        :param version: reference template version
        :type version: string
        :return: a list of fields
        :rtype: list
        """
        fields = None

        if category == "dataset_description":
            axis = 1

        if version:
            version = self._convert_version_format(version)
            template_dir = self._get_template_dir(version)

            element_description_file = template_dir / "../schema.xlsx"

            try:
                element_description = pd.read_excel(element_description_file, sheet_name=category)
            except XLRDError:
                element_description = pd.read_excel(element_description_file, sheet_name=category, engine='openpyxl')

            print("Category: " + str(category))
            for index, row in element_description.iterrows():
                print(str(row["Element"]))
                print("    Required: " + str(row["Required"]))
                print("    Type: " + str(row["Type"]))
                print("    Description: " + str(row["Description"]))
                print("    Example: " + str(row["Example"]))

            fields = element_description.values.tolist()
            return fields

        if not self._template:
            self.load_template(version=None)

        data = self._template.get(category)
        metadata = data.get("metadata")
        # set the first column as the index column
        metadata = metadata.set_index(list(metadata)[0])
        if axis == 0:
            fields = list(metadata.columns)
        elif axis == 1:
            fields = list(metadata.index)

        print("Fields:")
        for field in fields:
            print(field)

        return fields

    def set_field(self, category, row_index, header, value):
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
        if not self._dataset:
            msg = "Dataset not defined. Please load the dataset in advance."
            raise ValueError(msg)

        metadata = self._dataset.get(category).get("metadata")

        if not isinstance(row_index, int):
            msg = "row_index should be 'int'."
            raise ValueError(msg)

        try:
            # Convert Excel row index to dataframe index: index - 2
            row_index = row_index - 2
            metadata.loc[row_index, header] = value
        except ValueError:
            msg = "Value error. row does not exists."
            raise ValueError(msg)

        self._dataset[category]["metadata"] = metadata

        return self._dataset

    def set_field_using_row_name(self, category, row_name, header, value):
        """
        Set single cell. The row is identified by the given unique name and column is identified by the header.

        :param category: metadata category
        :type category: string
        :param row_name: Unique row name in Excel. (Ex: if subjects is category, a row name can be a unique subjet id)
        :type row_name: string
        :param header: column name. the header is the first row
        :type header: string
        :param value: field value
        :type value: string
        :return: updated dataset
        :rtype: dict
        """
        if not self._dataset:
            msg = "Dataset not defined. Please load the dataset in advance."
            raise ValueError(msg)

        metadata = self._dataset.get(category).get("metadata")

        if not isinstance(row_name, str):
            msg = "row_name should be string."
            raise ValueError(msg)

        # Assumes that all excel files first column contains the unique value field
        # TODO: In version 1, the unique column is not the column 0. Hence, unique column must be specified. 
        # This method need to be fixed to accomadate this 
        matching_indices = metadata.index[metadata[metadata.columns[0]]==row_name].tolist()

        if not matching_indices:
            msg = f"No row with given unique name, {row_name}, was found in the unique column {metadata.columns[0]}"
            raise ValueError(msg)
        elif len(matching_indices)>1:
            msg = f"More than one row with given unique name, {row_name}, was found in the unique column {metadata.columns[0]}"
            raise ValueError(msg)
        else:
            excel_row_index = matching_indices[0] + 2
            return self.set_field(category=category, row_index=excel_row_index, header=header, value=value)

        
    def append(self, category, row, check_exist=False, unique_column=None):
        """
        Append a row to a metadata file

        :param category: metadata category
        :type category: string
        :param row: a row to be appended
        :type row: dic
        :param check_exist: Check if row exist before appending, if exist, update row, defaults to False
        :type check_exist: bool, optional
        :param unique_column: if check_exist is True, provide which column in category is unique, defaults to None
        :type unique_column: string, optional
        :raises ValueError: _description_
        :return: updated dataset
        :rtype: dict
        """
        if not self._dataset:
            msg = "Dataset not defined. Please load the dataset in advance."
            raise ValueError(msg)

        metadata = self._dataset.get(category).get("metadata")

        if check_exist:
            # In version 1, the unique column is not the column 0. Hence, unique column must be specified
            if unique_column is None:
                error_msg = "Provide which column in category is unique. Ex: subject_id"
                raise ValueError(error_msg)
            
            try:
                row_index = check_row_exist(metadata, unique_column, unique_value=row[unique_column])
            except ValueError:
                error_msg = "Row values provided does not contain a unique identifier"
                raise ValueError(error_msg)
        else:
            row_index = -1

        if row_index == -1:
            # Add row
            row_df = pd.DataFrame([row])
            metadata = pd.concat([metadata, row_df], axis=0, ignore_index=True)     #If new header comes, it will be added as a new column with its value
        else:
            # Append row with additional values
            for key, value in row.items():
                metadata.loc[row_index, key] = value
            
        self._dataset[category]["metadata"] = metadata
        return self._dataset

    def update_by_json(self, category, json_file):
        """
        Given json file, update metadata file
        :param category: metadata category/filename
        :type category: string
        :param json_file: path to metadata file in json
        :type json_file: string
        :return:
        :rtype:
        """
        metadata = self._dataset.get(category).get("metadata")

        with open(json_file, "r") as f:
            data = json.load(f)

        for key, value in data.items():
            if isinstance(value, dict):
                for key_1, value_1 in value.items():
                   if isinstance(value, list):
                       field = "    " + key_1
                       value = str(value_1)
                   else:
                       field = "    " + key_1
                       value = value_1

                   index = metadata.index[metadata['Metadata element'] == field].tolist()[0]
                   metadata.loc[index, "Value"] = value

            elif isinstance(value, list):
                field = key
                value = str(value)
                index = metadata.index[metadata['Metadata element'] == field].tolist()[0]
                metadata.loc[index, "Value"] = value
            else:
                field = key
                index = metadata.index[metadata['Metadata element'] == field].tolist()[0]
                metadata.loc[index, "Value"] = value

        return metadata

    
    def generate_file_from_template(self, save_path, category, data=pd.DataFrame()):
        """Generate file from a template and populate with data if givn

        :param save_path: destination to save the generated file
        :type save_path: string
        :param category: SDS category (Ex: samples, subjects)
        :type category: string
        :param data: pandas dataframe containing data, defaults to pd.DataFrame()
        :type data: pd.DataFrame, optional
        """
        self._template_dir = self._get_template_dir(version=self._version)
        sf = StyleFrame.read_excel_as_template(os.path.join(self._template_dir, f'{category}.xlsx'), data)
        writer = StyleFrame.ExcelWriter(save_path)
        sf.to_excel(writer)
        writer.save()

    def add_data(self, source_path, subject, sample, data_type="primary", sds_parent_dir=None, copy=True, overwrite=False, sample_metadata={}, subject_metadata={}):

        if sds_parent_dir:
            self._dataset_path = Path(sds_parent_dir)

        if data_type == "primary":
            self.add_primary_data(source_path, subject, sample, copy, overwrite, sample_metadata, subject_metadata)
        elif data_type == 'derivative':
            self.add_derivative_data(source_path, subject, sample, copy, overwrite)
        else:
            msg = f"The data_type should be 'primary' or 'derivative'"
            raise ValueError(msg)
    def add_primary_data(self, source_path, subject, sample, copy=True, overwrite=False, sample_metadata={}, subject_metadata={}):
        """Add raw data of a sample to correct SDS location and update relavent metadata files

        :param source_path: original location of raw data
        :type source_path: string
        :param subject: subject id
        :type subject: string
        :param sample: sample id
        :type sample: string
        :param self._dataset_path: path to existing sds dataset or desired save location for new sds dataset, defaults to None
        :type self._dataset_path: string, optional
        :param copy: if True, source directory data will not be deleted after copying, defaults to True
        :type copy: bool, optional
        :param overwrite: if True, any data in the destination folder will be overwritten, defaults to False
        :type overwrite: bool, optional
        :param sample_metadata: metadata for the sample (Ex: sample anatomical location), defaults to {}
        :type sample_metadata: dict, optional
        :param subject_metadata: metadata for the subject (Ex: sex, age), defaults to {}
        :type subject_metadata: dict, optional
        :raises NotADirectoryError: if the primary in sds_parent_dir is not a folder, this wil be raised.
        """
        if self._dataset_path is None:
            if not os.path.exists('tmp'):
                os.mkdir('tmp')
            self._dataset_path = tempfile.mkdtemp(prefix="sds_dataset_", dir='tmp')
        
        primary_folder = os.path.join(str(self._dataset_path), 'primary')

        if os.path.exists(primary_folder):
            if os.path.isdir(primary_folder):
                self.load_dataset(dataset_path=self._dataset_path, from_template=False, version=self._version)
            else:
                raise NotADirectoryError(f'{primary_folder} is not a directory')
        else:
            self.load_dataset(dataset_path=self._dataset_path, from_template=True, version=self._version)
            self.save(save_dir=self._dataset_path)

        add_data(source_path, self._dataset_path, subject, sample, data_type="primary", copy=copy, overwrite=overwrite)

        samples_file_path = os.path.join(self._dataset_path, 'samples.xlsx')
        subjects_file_path = os.path.join(self._dataset_path, 'subjects.xlsx')

        if not os.path.exists(samples_file_path):
            self.generate_file_from_template(samples_file_path, 'samples')
        if not os.path.exists(subjects_file_path):
            self.generate_file_from_template(subjects_file_path, 'subjects')

        self.load_dataset(dataset_path=self._dataset_path, from_template=False, version=self._version)
        
        if not sample_metadata:
            self.append(
                category="samples", 
                row={self._subject_id_field: subject, self._sample_id_field: sample}, 
                check_exist=True, 
                unique_column=self._sample_id_field
                )
        else:
            self.append(
                category="samples", 
                row=sample_metadata, 
                check_exist=True, 
                unique_column=self._sample_id_field
                )
        self.generate_file_from_template(samples_file_path, 'samples', self._dataset['samples']['metadata'])

        if not subject_metadata:
            self.append(
                category="subjects", 
                row={self._subject_id_field: subject}, 
                check_exist=True, 
                unique_column=self._subject_id_field
                )
        else:
            self.append(
                category="subjects", 
                row=subject_metadata, 
                check_exist=True, 
                unique_column=self._subject_id_field
                )
        self.generate_file_from_template(subjects_file_path, 'subjects', self._dataset['subjects']['metadata'])


    def add_derivative_data(self, source_path, subject, sample, sds_parent_dir, copy=True, overwrite=False):
        """Add raw data of a sample to correct SDS location and update relavent metadata files. 
        Requires you to already have the folder structure inplace.

        :param source_path: original location of raw data
        :type source_path: string
        :param subject: subject id
        :type subject: string
        :param sample: sample id
        :type sample: string
        :param sds_parent_dir: path to existing sds dataset parent
        :type sds_parent_dir: string, optional
        :param copy: if True, source directory data will not be deleted after copying, defaults to True
        :type copy: bool, optional
        :param overwrite: if True, any data in the destination folder will be overwritten, defaults to False
        :type overwrite: bool, optional
        :raises NotADirectoryError: if the derivative in sds_parent_dir is not a folder, this wil be raised.
        """

        derivative_folder = os.path.join(str(self._dataset_path), 'derivative')
        
        # Check if sds_parent_directory contains the derivative folder. If not create it.
        if os.path.exists(derivative_folder):
            if not os.path.isdir(derivative_folder):
                raise NotADirectoryError(f'{derivative_folder} is not a directory')
        else:
            os.mkdir(derivative_folder)


        add_data(source_path, self._dataset_path, subject, sample, data_type="derivative", copy=copy, overwrite=overwrite)

    def add_element(self, category, element):
        metadata = self._dataset.get(category).get("metadata")
        if category in self._column_based:
            row_pd = pd.DataFrame([{"Metadata element": element}])
            metadata = pd.concat([metadata, row_pd], axis=0, ignore_index=True)
        else:
            metadata[element] = None

        self._dataset[category]["metadata"] = metadata
