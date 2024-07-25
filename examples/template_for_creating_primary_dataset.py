"""
Template for generating a SDS primary dataset
"""
import os
from pathlib import Path

from sparc_me import Dataset, Subject, Sample


def add_dataset_description(dataset, save_dir):
    """
    the values can be filled in by 2 methods, set_field() or set_field_using_row_name().

    This example will use Dataset.set_field()
    # You can get the row_index by looking at
    #   1. the saved metadata file dataset_description.xlsx. Excel index starts from 1 where index 1 is the header row. so actual data index starts from 2.
    #   2. or the DataFrame object in the python code. dataset._dataset.dataset_description.metadata
    """

    metadata = dataset.get_metadata(metadata_file='dataset_description')
    metadata.add_values(
        element='Type',
        values='Experimental')
    metadata.add_values(
        element='Title',
        values='')
    metadata.add_values(
        element='Subtitle',
        values='')
    metadata.add_values(
        element='Keywords',
        values=[''])
    metadata.add_values(
        element='Funding',
        values='')
    metadata.add_values(
        element='Study purpose',
        values='')
    metadata.add_values(
        element='Study data Collection',
        values='')
    metadata.add_values(
        element='Study primary conclusion',
        values='')
    metadata.add_values(
        element='Study organ system',
        values='breast')
    metadata.add_values(
        element='Study approach',
        values='')
    metadata.add_values(
        element='Study technique',
        values='')
    metadata.add_values(
        element='Contributor name',
        values=[''])
    metadata.add_values(
        element='Contributor orcid',
        values=[''])
    metadata.add_values(
        element='Identifier',
        values='')
    metadata.add_values(
        element='Identifier description',
        values='')
    metadata.add_values(
        element='Relation type',
        values='')
    metadata.add_values(
        element='Identifier type',
        values='')
    metadata.add_values(
        element='Contributor affiliation',
        values=[''])
    metadata.add_values(
        element='Contributor role',
        values=[''])

    metadata.save(os.path.join(save_dir, "dataset_description.xlsx"))
    return dataset


if __name__ == '__main__':
    save_dir = Path(r"")

    # Creating an empty SDS dataset from template
    dataset = Dataset()
    dataset.load_dataset(from_template=True, version="2.0.0")
    dataset.set_path(str(save_dir))
    dataset.save()

    # Filling in the dataset descriptions
    add_dataset_description(dataset, save_dir=str(save_dir))

    # Adding subjects and samples (the manifests will be updated automatically)
    subjects = []

    # sub-001
    subject = Subject()
    subject.set_values({
        "age": "",
        "sex": "",
        "species": "",
        "age category": "",
        "age range (min)": "",
        "age range (max)": ""
    })

    samples = []
    # sub-1 sam-1
    sample = Sample()

    sample.add_path(str(Path(r"path/to/sample")))
    samples.append(sample)

    subject.add_samples(samples)
    subjects.append(subject)

    # sub-2
    subject = Subject()

    subject.set_values({
        "age": "",
        "sex": "F",
        "species": "",
        "age category": "",
        "age range (min)": "",
        "age range (max)": ""
    })

    samples = []

    # sub-2 sam-1
    sample = Sample()
    sample.add_path(str(Path(r"path/to/sample")))
    samples.append(sample)

    subject.add_samples(samples)
    subjects.append(subject)

    dataset.add_subjects(subjects)

    # Updating sample metadata
    # sub-1
    subject = dataset.get_subject("sub-1")
    sample = subject.get_sample("sam-1")
    sample.set_values({
        "sample experimental group": "",
        "sample type": "",
        "sample anatomical location": ""
    })

    subject = dataset.get_subject("sub-2")
    sample = subject.get_sample("sam-1")
    sample.set_values({
        "sample experimental group": "",
        "sample type": "",
        "sample anatomical location": ""
    })
    dataset.save()
