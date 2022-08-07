from sparc_me import Dataset

if __name__ == '__main__':
    dataset = Dataset()

    # Load the SPARC template dataset. source from https://github.com/SciCrunch/sparc-curation
    dataset.load_from_template(version="2.0.0")
    # dataset.load_dataset(from_template=True, version="2.0.0")

    # Save the template dataset
    dataset.save(save_dir="./tmp/template/")

