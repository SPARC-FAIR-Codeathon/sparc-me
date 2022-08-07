import json
import pandas as pd
from pathlib import Path
import openpyxl
import os
import math

from xlrd import XLRDError

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

current_dir = Path(__file__).parent.resolve()
resources_dir = Path.joinpath(current_dir, "../resources")


def convert_version_format(version):
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


class Validator(object):
    def __init__(self):
        self._version = None
        self._category = None
        self._schema_ref = None

    def validate(self, data, category, version):
        self._category = category
        self._version = convert_version_format(version)
        self._load_reference_schema()
        if isinstance(data, dict):
            self._execute(data)
        elif isinstance(data, list):
            for idx in range(len(data)):
                self._execute(data[idx])
        else:
            print("Input data type invalid")

    def _load_reference_schema(self):
        version = "version_" + self._version
        filename = self._category + ".json"
        schema_path = resources_dir / "templates" / version / "schema" / filename
        if not schema_path.exists():
            raise ValueError("Reference schema not found!")

        with open(schema_path) as file:
            schema_details = json.load(file)

        schema = {"type": schema_details.get("type"), "properties": {}, "required": schema_details.get("required")}
        for element, value in schema_details["properties"].items():
            data_type = value.get("type")
            schema["properties"][element] = {
                "type": data_type
            }

        self._schema_ref = schema

    def _execute(self, data):
        # validate(instance=instance, schema=self._schema_ref)
        try:
            validate(instance=data, schema=self._schema_ref)
            print("Validation: Passed")
        except ValidationError:
            print(best_match(Draft202012Validator(self._schema_ref).iter_errors(data)).message)
        except Exception as e:
            print(str(e))


class Schema(object):
    def __init__(self):
        self._schemas = dict()
        self._categories = list()

        self._schema_dir = Path()

    def generate_from_template(self, file, save_dir):
        wb = openpyxl.load_workbook(file)
        sheetnames = wb.sheetnames

        for sheet in sheetnames:
            try:
                schema_pd = pd.read_excel(file, sheet_name=sheet)
            except XLRDError:
                schema_pd = pd.read_excel(file, sheet_name=sheet, engine='openpyxl')

            schema = {"type": "object", "properties": {}, "required": []}
            required_list = list()

            for index, row in schema_pd.iterrows():
                element = row.get("Element")
                required = row.get("Required")
                data_type = row.get("Type")
                description = row.get("Description")
                example = row.get("Example")

                if required == 'Y':
                    required_list.append(element)

                # data_type = type(example).__name__

                try:
                    if math.isnan(example):
                        example = None
                except:
                    pass

                schema["properties"][element] = {
                    "type": data_type,
                    "required": required,
                    "description": description,
                    "example": example
                }

            schema["required"] = required_list
            self._schemas[sheet] = schema

            self.save(save_dir, schema, sheet)

    def save(self, save_dir, schema, sheet):
        if not save_dir.exists():
            os.makedirs(save_dir)
        filename = '{sheet}.json'.format(sheet=sheet)
        save_path = Path.joinpath(save_dir, filename)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=4)


if __name__ == '__main__':
    schema_xlsm = Path.joinpath(current_dir, "../resources/templates/version_1_2_3/element_descriptions.xlsx")
    save_dir = Path.joinpath(current_dir, "../resources/templates/version_1_2_3/schema")

    schema = Schema()
    schema.generate_from_template(schema_xlsm, save_dir=save_dir)

    # instance = {"Name": "test", "Description": "test", "Keywords":"sassf"}
    # validator = Validator()
    # validator.validate(instance, category="dataset_description", version="1.2.3")
