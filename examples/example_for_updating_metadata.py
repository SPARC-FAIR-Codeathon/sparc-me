from sparc_me import Dataset

def add_values_dataset_description(dataset_description_editor):
    dataset_description_editor.add_values("2.0.0", row_name='metadataversion')
    dataset_description_editor.add_values("experimental", row_name='type')
    dataset_description_editor.add_values("Duke breast cancer MRI preprocessing", row_name='Title')
    dataset_description_editor.add_values("""Preprocessing the breast cancer MRI images and saving in Nifti format""",
                                          row_name='subtitle')
    dataset_description_editor.add_values("Breast cancer", "image processing", row_name='Keywords')
    dataset_description_editor.add_values("""Preprocessing the breast cancer MRI images and saving in Nifti format""",
                                          row_name="Study purpose")
    dataset_description_editor.add_values("derived from Duke Breast Cancer MRI dataset",
                                          row_name='Study data Collection')
    dataset_description_editor.add_values("NA", row_name='Study primary conclusion')
    dataset_description_editor.add_values("NA", row_name='Study primary conclusion', append=True)
    dataset_description_editor.add_values("breast", row_name='Study organ system')
    dataset_description_editor.add_values("image processing", row_name='Study approach')
    dataset_description_editor.add_values("""dicom2nifti""", row_name='Study technique')
    dataset_description_editor.add_values("Lin, Chinchien", "Gao, Linkun", row_name='contributorname')
    dataset_description_editor.add_values("Prasad", "Jiali", row_name='contributorNAME', append=True)
    dataset_description_editor.add_values(*["bob", "db"], row_name="contributor name", append=True)
    dataset_description_editor.add_values(
        "https://orcid.org/0000-0001-8170-199X",
        "https://orcid.org/0000-0001-8171-199X",
        "https://orcid.org/0000-0001-8172-199X",
        "https://orcid.org/0000-0001-8173-199X",
        "https://orcid.org/0000-0001-8174-199X",
        "https://orcid.org/0000-0001-8176-199X",
        row_name='Contributor orcid')

    dataset_description_editor.add_values(*["University of Auckland"] * 6, row_name='Contributor affiliation')
    dataset_description_editor.add_values(*["developer", "developer", "Researcher", "Researcher", "tester", "tester"],
                                          row_name="contributor role")
    dataset_description_editor.add_values("source", row_name='Identifier description')
    dataset_description_editor.add_values("WasDerivedFrom", row_name='Relation type')
    dataset_description_editor.add_values("DTP-UUID", row_name='Identifier')
    dataset_description_editor.add_values("12L digital twin UUID", row_name='Identifier type')
    dataset_description_editor.add_values("1", row_name='Number of subjects')
    dataset_description_editor.add_values("1", row_name='Number of samples')
if __name__ == '__main__':
    save_dir = "./tmp/template/"

    dataset = Dataset()

    # Step:1 list categories and dataset_description elements
    categories = dataset.list_categories(version="2.0.0")
    elements = dataset.list_elements(category="dataset_description", version="2.0.0")
    # list code_parameters elements
    # elements = dataset.list_elements(category="code_parameters", version="2.0.0")

    # Step2, way1: load dataset from template
    dataset.load_from_template(version="2.0.0")
    #
    # Save the template dataset.
    # dataset.save(save_dir=save_dir)

    # Step2, way2： load dataset from existing dataset
    # dataset.load_dataset(dataset_path=save_dir)

    # Step3, get dataset_description, code_description, code_parameters metadataEditor
    dataset_description_editor = dataset.get_metadata(category="dataset_description")
    code_parameters_editor = dataset.get_metadata(category="code_parameters")
    code_description_editor = dataset.get_metadata(category="code_description")

    # Step4, add values for dataset_description_editor need to specify field_name
    add_values_dataset_description(dataset_description_editor)

    # Step4, add values for code_description_editor need to specify field_name
    # code_description_editor.add_values(*["test..1", "test2", "test3", "test4", "test5...", ],
    #                                    row_name="TSR1: Define Context Clearly Rating (0-4)", append=False)
    #
    # # Step4, add values for code_parameters_editor to add values in a row, append = False
    # code_parameters_editor.add_values(
    #     *["breast ...", "test..1", "test2", "test3", "test4", "test5...", "test3", "test4", "test5..."], append=False)
    # # Step4, add values for code_parameters_editor to add values in a row, append = True
    # code_parameters_editor.add_values(
    #     *["breast_append", "test1_append", "test2_append", "test3_append", "test4_append", "test5..._append",
    #       "test3_append", "test4_append", "test5_append"], append=True)
    # # Step4, add values for code_parameters_editor to add values in a column need to specify field_name, append = True
    # code_parameters_editor.add_values(*["test1_name", "test2_name", "test3_name", "test4_name"], header='name',
    #                                   append=True)

    # Step5, get values for code_parameters_editor
    print(code_parameters_editor.get_values(field_name="name"))
    # Step5, get values for dataset_description_editor
    print(dataset_description_editor.get_values(field_name="contributorrole"))
    # Step5, get values for code_parameters_editor
    print(code_description_editor.get_values(field_name="TSR1: Define Context Clearly Rating (0-4)"))

    # Step6, remove values in specific header/field_name, code_parameters_editor
    # code_parameters_editor.remove_values("test1_name", field_name="name")

    # Step6, remove entire values in code_parameters_editor
    # code_parameters_editor.clear_values()
    # Step6, remove entire values in dataset_description_editor
    # dataset_description_editor.clear_values()
    # Step6, remove entire values in code_description_editor
    # code_description_editor.clear_values()

    # Step6, remove all values in one specific row/col
    # code_parameters_editor.clear_values(field_name="name")
    # dataset_description_editor.clear_values(field_name="Contributor role")
    # code_description_editor.clear_values(field_name="TSR1: Define Context Clearly Rating (0-4)")

    # Step7, save current dataset
    dataset.save(save_dir=save_dir)

    # Step8, move files to dataset primary and derivative folder
    # Copy data from "source_data_raw" to a "sds_dataset" parent directory adhering to SDS framework.
    dataset.add_data(source_path="./test_data/sample1/raw", subject="subject-xyz", sample="sample-1",
                     data_type="primary", sds_parent_dir=save_dir, overwrite=True)
    # If you want to move the data to destination directory, set copy to 'False'.
    dataset.add_data(source_path="./test_data/sample2/raw", subject="subject-xyz", sample="sample-2",
                     data_type="primary", sds_parent_dir=save_dir, overwrite=True)

    # Copy data from "source_data_derived" to a "sds_dataset" parent directory adhering to SDS framework.
    dataset.add_data(source_path="./test_data/sample1/derived", subject="subject-xyz", sample="sample-abc",
                     data_type="derivative", sds_parent_dir=save_dir, overwrite=True)
