"""Example for demonstrating base functionality of sparc-me.
"""

from sparc_me import Dataset, Sample, Subject

if __name__ == '__main__':
    save_dir = "./tmp/template/"

    dataset = Dataset()
    dataset.set_path(save_dir)
    # List metadata categories/files. 
    categories = dataset.list_metadata_files(version="2.0.0")
    print(categories)

    # List elements/fields
    elements = dataset.list_elements(metadata_file="dataset_description", version="2.0.0")

    # Creating/loading dataset. 

    # Load dataset from template. 
    # Dataset templates are stored here: https://github.com/SciCrunch/sparc-curation/releases
    dataset.create_empty_dataset(version="2.0.0")

    # Save the template dataset. 
    dataset.save(save_dir=save_dir)


    # Updating dataset. 
    dataset_description = dataset.get_metadata(metadata_file="dataset_description")

    # Update a metadata file.
    # Note: give the element in the metadata file no matter their Case, space and underscore.
    # The add value is append the values to the existing values
    dataset_description.add_values(element='type', values="experimental")
    dataset_description.add_values(element='Title', values="duke breast cancer MRI preprocessing")

    # Add multiple values via str[]
    dataset_description.add_values(element='Keywords', values=["breast cancer", "image processing"])

    # Set value to replace current values
    dataset_description.set_values(
        element='Contributor orcid',
        values=["https://orcid.org/0000-0001-8170-199X",
                "https://orcid.org/0000-0001-8171-199X",
                "https://orcid.org/0000-0001-8172-199X",
                "https://orcid.org/0000-0001-8173-199X",
                "https://orcid.org/0000-0001-8174-199X",
                "https://orcid.org/0000-0001-8176-199X"])

    # Code to move the samples and subject.
    # It will automatically update the dataset_description, manifest, samples and subjects metadata
    subjects = []
    samples = []

    sample1 = Sample()
    sample1.add_path("./test_data/bids_data/sub-01/sequence1/")

    sample1.add_path(["./test_data/sample2/raw/dummy_sam2.txt", "./test_data/sample1/raw/dummy_sam1.txt"])
    samples.append(sample1)

    # create a subject obj
    subject1 = Subject()
    # add a sample obj list to subject
    subject1.add_samples(samples)

    subjects.append(subject1)

    dataset.add_subjects(subjects)

    subject_sds_id = "sub-1"
    subject = dataset.get_subject(subject_sds_id)
    subject.set_value(
        element='age',
        value=30)

    sample_sds_id = "sam-1"
    sample = subject.get_sample(sample_sds_id)
    sample.set_value(
        element='sampleexperimental group',
        value='experimental')
    sample.set_value(
        element='sample type',
        value='DCE-MRI Contrast Image {0}'.format(sample_sds_id))
    sample.set_value(
        element='sample anatomical location',
        value='breast')


    dataset.save(save_dir)