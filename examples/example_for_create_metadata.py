from sparc_me import Dataset
from sparc_me.core.schema import Schema, Validator


def add_values_dataset_description(dataset_description):
    dataset_description.add_values(field_name='type', values="experimental")
    dataset_description.add_values(field_name='Title', values="Duke breast cancer MRI preprocessing")
    dataset_description.add_values(field_name='subtitle',
                                   values="""Preprocessing the breast cancer MRI images and saving in Nifti format""")
    dataset_description.add_values(field_name='Keywords', values=["Breast cancer", "image processing"])
    dataset_description.add_values(field_name="Study purpose",
                                   values="""Preprocessing the breast cancer MRI images and saving in Nifti format""")
    dataset_description.add_values(field_name="Study primary conclusion", values="The result is great.")
    dataset_description.add_values(field_name='Study data Collection',
                                   values="derived from Duke Breast Cancer MRI dataset")
    dataset_description.add_values(field_name='Study primary conclusion', values="Your conclusion here!")
    dataset_description.add_values(field_name='Study organ system', values="breast")
    dataset_description.add_values(field_name='Study approach', values="image processing")
    dataset_description.add_values(field_name='Study technique', values="dicom2nifti", )
    dataset_description.add_values(field_name='contributorname', values=["Lin, Chinchien", "Gao, Linkun"])
    dataset_description.add_values(field_name='contributorNAME', values=["Prasad", "Jiali"])
    dataset_description.add_values(field_name="contributor name", values=["bob", "db"])
    dataset_description.add_values(
        field_name='Contributor orcid',
        values=["https://orcid.org/0000-0001-8170-199X",
                "https://orcid.org/0000-0001-8171-199X",
                "https://orcid.org/0000-0001-8172-199X",
                "https://orcid.org/0000-0001-8173-199X",
                "https://orcid.org/0000-0001-8174-199X",
                "https://orcid.org/0000-0001-8176-199X"],
        append=False)

    dataset_description.add_values(field_name='Contributor affiliation', values=["University of Auckland"] * 6, )
    dataset_description.add_values(field_name="contributor role",
                                   values=["developer", "developer", "Researcher", "Researcher", "tester", "tester"])
    dataset_description.add_values(field_name='Identifier description', values="source")
    dataset_description.add_values(field_name='Relation type', values="WasDerivedFrom")
    dataset_description.add_values(field_name='Identifier', values="DTP-UUID")
    dataset_description.add_values(field_name='Identifier type', values="12L digital twin UUID")


def add_values_for_sample_metadata(sample_metadata):
    sample_metadata.add_values(field_name="was derived from", values=["test"] * 6, append=False)
    sample_metadata.add_values(field_name="pool id",
                               values=["pool id 1", "pool id 2", "pool id 3", "pool id 4", "pool id 5", "pool id 6"],
                               append=False)
    sample_metadata.add_values(field_name="also in dataset", values=[*["Yes"] * 5, "No"], append=False)
    sample_metadata.add_values(field_name="member of", values=["Global"] * 6, append=False)
    sample_metadata.add_values(
        field_name="laboratory internal id",
        values=["laboratory 1", "laboratory 2", "laboratory 3", "laboratory 4", "laboratory 5", "laboratory 6"],
        append=False)
    sample_metadata.add_values(field_name="date of derivation", values=[*["1991-05-25"] * 3, *["1991-06-10"] * 3],
                               append=False)

    sample_metadata.save()


def add_values_for_subject_metadata(subject_metadata):
    subject_metadata.add_values(field_name='subject experimental group', values="test-xyz", append=False)
    subject_metadata.add_values(field_name='age', values="30", append=False)
    subject_metadata.add_values(field_name='sex', values="Male", append=False)
    subject_metadata.add_values(field_name='species', values="P", append=False)
    subject_metadata.add_values(field_name='strain', values="test", append=False)
    subject_metadata.add_values(field_name="age category", values="old", append=False)
    subject_metadata.add_values(field_name="pool id", values=["pool id 1", "pool id 2", "pool id 3"],
                                append=False)
    subject_metadata.add_values(field_name="also in dataset", values=["Yes"] * 3, append=False)
    subject_metadata.add_values(field_name="RRID for strain", values=["515dsd1515", "da515daa69", "515dsa62a"],
                                append=False)
    subject_metadata.add_values(field_name="member of", values=["Global"] * 3, append=False)
    subject_metadata.add_values(
        field_name="laboratory internal id", values=["laboratory 1", "laboratory 2", "laboratory 3"],
        append=False)
    subject_metadata.add_values(field_name="date of birth", values=["1996-03-25", "1995-09-05", "1996-04-11"],
                                append=False)
    subject_metadata.save()


if __name__ == '__main__':
    save_dir = "./tmp/template/"

    dataset = Dataset()
    schema = Schema()
    validator = Validator()
    dataset.set_dataset_path(save_dir)
    # NOTE: Step:1 list categories and dataset_description elements
    categories = dataset.list_metadata_files(version="2.0.0")
    elements = dataset.list_elements(metadata_file="dataset_description", version="2.0.0")
    # list code_parameters elements
    # elements = dataset.list_elements(metadata_file="code_parameters", version="2.0.0")

    # NOTE: Step2, way1: load dataset from template
    dataset.load_from_template(version="2.0.0")
    #
    # Save the template dataset.
    # dataset.save(save_dir=save_dir)

    # NOTE: Step2, way2： load dataset from existing dataset
    # dataset.load_dataset(dataset_path=save_dir)

    # NOTE: Step3, get dataset_description, code_description, code_parameters metadataEditor
    dataset_description = dataset.get_metadata(metadata_file="dataset_description")
    # code_parameters = dataset.get_metadata(metadata_file="code_parameters")
    # code_description = dataset.get_metadata(metadata_file="code_description")

    des_schema = schema.get_schema("dataset_description")
    print(des_schema.get('Subtitle'))

    # NOTE: Step3.1(optional), remove entire values in dataset_description
    dataset_description.clear_values()

    # NOTE: Step4, add values for dataset_description need to specify row_name
    add_values_dataset_description(dataset_description)

    # Step4, add values for code_description_editor need to specify field_name
    # code_description.add_values(*["test..1", "test2", "test3", "test4", "test5...", ],
    #                                    row_name="TSR1: Define Context Clearly Rating (0-4)", append=False)
    # # Step4, add values for code_parameters_editor to add values in a row, append = False
    # code_parameters.add_values(
    #     *["breast ...", "test..1", "test2", "test3", "test4", "test5...", "test3", "test4", "test5..."], append=False)
    # # Step4, add values for code_parameters_editor to add values in a row, append = True
    # code_parameters.add_values(
    #     *["breast_append", "test1_append", "test2_append", "test3_append", "test4_append", "test5..._append",
    #       "test3_append", "test4_append", "test5_append"], append=True)
    # # Step4, add values for code_parameters_editor to add values in a column need to specify field_name, append = True
    # code_parameters.add_values(*["test1_name", "test2_name", "test3_name", "test4_name"], header='name',
    #                                   append=True)

    # NOTE: Step5: Get Values
    # get values for dataset_description_editor
    print(dataset_description.get_values(field_name="contributorrole"))
    # get values for code_parameters_editor
    # print(code_parameters.get_values(field_name="name")
    # print(code_description.get_values(field_name="TSR1: Define Context Clearly Rating (0-4)"))

    # NOTE: Step6, remove values in specific header/row_name, code_parameters
    dataset_description.remove_values( field_name="contributor role", values="tester")
    # code_parameters.remove_values(field_name="name", values="test1_name")
    # Step6, remove entire values in code_parameters_editor
    # code_parameters.clear_values()
    # Step6, remove entire values in dataset_description_editor
    # dataset_description.clear_values()
    # Step6, remove entire values in code_description_editor
    # code_description.clear_values()

    # Step6, remove all values in one specific row/col
    # code_parameters.clear_values(field_name="name")
    # dataset_description.clear_values(field_name="Contributor role")
    # code_description.clear_values(field_name="TSR1: Define Context Clearly Rating (0-4)")

    # NOTE: Step7, save current dataset
    # dataset.save(save_dir=save_dir)
    # dataset.save()

    # NOTE: Step8, move files to dataset primary and derivative folder
    # NOTE: Step8.1, Copy data from "source_data_raw" to a "sds_dataset" parent directory adhering to SDS framework.
    dataset.add_samples(source_paths=["./test_data/sample1/raw", "./test_data/sample2/raw"], subject="sub-xyz",
                        samples=["sam-1", "sam-2"],
                        data_type="primary", sds_parent_dir=save_dir)

    # Copy data from "source_data_derived" to a "sds_dataset" parent directory adhering to SDS framework.
    dataset.add_sample(source_path="./test_data/sample1/derived", subject="sub-xyz", sample="sam-abc",
                       data_type="derivative", sds_parent_dir=save_dir, sample_metadata={})

    # NOTE: Step8.2, add subject with subject and sample metadata

    # copy data from "source_data_primary" to "sds_dataset" primary(default) directory
    dataset.add_subjects(source_paths=["./test_data/bids_data/sub-01", "./test_data/bids_data/sub-02"],
                         subjects=["1", "sub-2"], subject_metadata={
            "subject experimental group": "experimental",
            "age": "041Y",
            "sex": "Female",
            "species": "human",
            "strain": "tissue",
            "age category": "middle adulthood"
        }, sample_metadata={
            "sample experimental group": "experimental",
            "sample type": "tissue",
            "sample anatomical location": "breast tissue",
        })
    # NOTE: Step8.3 Copy single sample file data to dataset
    #
    #  from "source_data_raw" to a "sds_dataset" parent directory adhering to SDS framework.
    dataset.add_sample(source_path="./test_data/sample1/raw/simple_test1.txt", subject="sub-xyz",
                       sample="sam-2",
                       data_type="primary", sds_parent_dir=save_dir)

    sample_metadata = dataset.get_metadata("samples")
    subject_metadata = dataset.get_metadata("subjects")
    add_values_for_sample_metadata(sample_metadata)
    add_values_for_subject_metadata(subject_metadata)

    dataset.add_thumbnail("./test_data/thumbnail_0.jpg")
    dataset.add_thumbnail("./test_data/thumbnail_1.jpg")
    # dataset.delete_data("./tmp/template/docs/thumbnail_0.jpg")
    # NOTE: Step9 Delete folder
    # Step9.1 Delete subject folder
    # dataset.delete_subject("./tmp/template/primary/subject-xyz")
    # Step9.2 Delete sample folder
    # dataset.delete_samples(["./tmp/template/primary/subject-1/func"])

    # dataset_description.clear_values()
    dataset.save()


    # NOTE: Step10 validate dataset via schema
    validator.validate_dataset(dataset)
    # description_meta = schema.load_data("./tmp/template/dataset_description.xlsx")
    # validator.validate(description_meta, metadata_file="dataset_description", version="2.0.0")
    # sub_meta = schema.load_data("./tmp/template/subjects.xlsx")
    # validator.validate(sub_meta, metadata_file="subjects", version="2.0.0")
