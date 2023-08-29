"""Example for demonstrating base functionality of sparc-me.
"""

from sparc_me import Dataset

if __name__ == '__main__':
    save_dir = "./tmp/template/"

    dataset = Dataset()

    # List metadata categories/files. 
    categories = dataset.list_categories(version="2.0.0")
    print(categories)

    # List elements/fields
    elements = dataset.list_elements(category="dataset_description", version="2.0.0")
    # elements = dataset.list_elements(category="subjects", version="2.0.0")

    # Creating/loading dataset. 

    # Load dataset from template. 
    # Dataset templates are stored here: https://github.com/SciCrunch/sparc-curation/releases
    dataset.load_from_template(version="2.0.0")

    # Save the template dataset. 
    dataset.save(save_dir=save_dir)

    # Updating dataset. 

    # Update a metadata file.
    # Note: Excel index starts from 1 where index 1 is the header row. so actual data index starts from 2.
    dataset.set_field(category="dataset_description", row_index=2, header="Value", value="testValue")
    dataset.set_field(category="dataset_description", row_index=2, header="Value 2", value="testValue")

    # # Append a row to the "subjects" metadata file. "subject id" will be set to "test_id"
    # dataset.append(category="subjects", row={"subject_id": "test_id"}) # version 1.2.3
    dataset.append(category="subjects", row={"subject id": "test_id"}) # version 2.0.0
    dataset.set_field_using_row_name(category="subjects", row_name="test_id", header="sex", value="male")

    dataset.save(save_dir)

    # Copy data from "source_data_raw" to a "sds_dataset" parent directory adhering to SDS framework.
    dataset.add_primary_data(source_path="./test_data/sample1/raw", subject="subject-xyz", sample="sample-1", sds_parent_dir=save_dir)
    # If you want to move the data to destination directory, set copy to 'False'.
    dataset.add_primary_data(source_path="./test_data/sample2/raw", subject="subject-xyz", sample="sample-2", sds_parent_dir=save_dir)

    # Copy data from "source_data_derived" to a "sds_dataset" parent directory adhering to SDS framework.
    dataset.add_derivative_data(source_path="./test_data/sample1/derived", subject="subject-xyz", sample="sample-abc", sds_parent_dir=save_dir)
