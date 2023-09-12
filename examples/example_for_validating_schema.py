"""Example for Validating schema.
- To validate a schema that read from raw data file.
"""

from pathlib import Path

from sparc_me.core.schema import Schema, Validator

if __name__ == '__main__':
    # dataset_dir = Path("test_data")
    dataset_dir = Path("tmp/template")

    # Validate dataset_description
    print("Validating dataset_description")
    metadata_file = dataset_dir.joinpath("dataset_description.xlsx")
    schema = Schema()
    schema.get_schema("dataset_description")
    data = schema.load_data(metadata_file)
    validator = Validator()
    # validator.validate(data, category="dataset_description", version="1.2.3")
    validator.validate(data, category="dataset_description", version="2.0.0")

    # Validate samples.
    # This one will fail because there is a required field in which its value missing
    print("Validating samples")
    metadata_file = dataset_dir.joinpath("samples.xlsx")
    schema = Schema()
    data = schema.load_data(metadata_file)
    validator = Validator()
    # validator.validate(data, category="samples", version="1.2.3")
    validator.validate(data, category="samples", version="2.0.0")
