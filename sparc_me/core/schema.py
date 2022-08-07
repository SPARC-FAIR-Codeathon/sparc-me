import json
import pandas as pd
from pathlib import Path
import openpyxl
import os
import math

from pathlib import Path
from genson import SchemaBuilder
from xlrd import XLRDError


current_dir = Path(__file__).parent.resolve()
resources_dir = Path.joinpath(current_dir, "../resources")


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

