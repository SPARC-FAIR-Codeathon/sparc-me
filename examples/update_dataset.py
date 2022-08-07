from pathlib import Path

from sparc_me import Dataset

if __name__ == '__main__':
    dataset = Dataset()

    # Set dataset path.
    # If the template dataset is already saved in "./tmp/template". you can then do:
    dataset_dir = Path(__file__).parent.resolve() / "./tmp/template"

    dataset.load_dataset(dataset_dir)

    # Update metadata. Excel index starts from 1 where index 1 is the header row. so actual data index starts from 2
    dataset.set_field(category="dataset_description", row_index=2, header="Value", value="testValue")

    # # Append a row to the "subjects" metadata file. "subject id" will be set to "test_id"
    dataset.append(category="subjects", row={"subject id": "test_id"})

    dataset.save(dataset_dir)
