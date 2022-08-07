from sparc_me import Dataset

if __name__ == '__main__':
    dataset = Dataset()

    # List categories()
    categories = dataset.list_categories(version="1.2.3")
    print(categories)

    # List SPARC elements
    elements = dataset.list_elements(category="dataset_description", version="1.2.3")
    elements = dataset.list_elements(category="subjects", version="1.2.3")


