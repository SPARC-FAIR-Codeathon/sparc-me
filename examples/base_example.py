from sparc_me import Dataset

if __name__ == '__main__':
    dataset = Dataset()

    # List metadata categories/files
    categories = dataset.list_categories(version="2.0.0")
    print(categories)

    # List elements/fields
    elements = dataset.list_elements(category="dataset_description", version="2.0.0")
    # elements = dataset.list_elements(category="subjects", version="2.0.0")

    # Creating/loading dataset

    # Load dataset from template. SPARC template datasets: https://github.com/SciCrunch/sparc-curation/releases
    dataset.load_from_template(version="2.0.0")
    # dataset.load_dataset(from_template=True, version="2.0.0")

    # Save the template dataset
    dataset.save(save_dir="./tmp/template/")

    # Updating dataset

    # Update a metadata file.
    # Note: Excel index starts from 1 where index 1 is the header row. so actual data index starts from 2
    dataset.set_field(category="dataset_description", row_index=2, header="Value", value="testValue")

    # # Append a row to the "subjects" metadata file. "subject id" will be set to "test_id"
    dataset.append(category="subjects", row={"subject id": "test_id"})

    dataset.save("./tmp/template/")

    # Copy data from "source_data_raw" to a "sds_dataset" parent directory adhering to SDS framework
    dataset.add_primary_data("source_data_raw", "subject-xyz", "sample-abc", sds_parent_dir="sds_dataset")
    dataset.add_primary_data("source_data_raw", "subject-xyz", "sample-pqr", sds_parent_dir="sds_dataset")

    # Copy data from "source_data_derived" to a "sds_dataset" parent directory adhering to SDS framework
    dataset.add_derivative_data("source_data_derived", "subject-xyz", "sample-abc", "sds_dataset")

    # Move data from "source_data_raw" to a temporary sds_dataset directory
    dataset.add_primary_data("source_data_raw", "subject-xyz", "sample-pqr", copy=False)
