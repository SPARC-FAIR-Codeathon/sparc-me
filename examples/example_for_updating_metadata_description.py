from sparc_me import Dataset


if __name__ == '__main__':

    save_dir = "./tmp/template/"

    dataset = Dataset()

    #Step:1 list categories and dataset_description elements
    categories = dataset.list_categories(version="2.0.0")
    elements = dataset.list_elements(category="dataset_description", version="2.0.0")
    # list code_parameters elements
    # elements = dataset.list_elements(category="code_parameters", version="2.0.0")

    #Step2, way1: load dataset from template
    dataset.load_from_template(version="2.0.0")
    #
    # Save the template dataset.
    # dataset.save(save_dir=save_dir)

    #Step2, way2： load dataset from existing dataset
    # dataset.load_dataset(dataset_path=save_dir)

    # Step3, get dataset_description metadataEditor
    dataset_description_editor = dataset.get_metadata_editor(category="dataset_description")

    # Step3, get code_parameters metadataEditor
    code_parameters_editor = dataset.get_metadata_editor(category="code_parameters")

    # Step3, get code_parameters metadataEditor
    code_description_editor = dataset.get_metadata_editor(category="code_description")

    # Step4, add values for dataset_description_editor need to specify field_name
    dataset_description_editor.add_values(*["developer", "tester"], field_name="contributor role", append=True)
    dataset_description_editor.add_values(*["bob", "db"], field_name="contributor name", append=True)

    # Step4, add values for code_description_editor need to specify field_name
    code_description_editor.add_values( *["test..1","test2","test3","test4", "test5...",], field_name="TSR1: Define Context Clearly Rating (0-4)", append=False)

    # Step4, add values for code_parameters_editor to add values in a row, append = False
    code_parameters_editor.add_values( *["breast ...","test..1","test2","test3","test4", "test5...","test3","test4", "test5..."], append=False)
    # Step4, add values for code_parameters_editor to add values in a row, append = True
    code_parameters_editor.add_values( *["breast_append","test1_append","test2_append","test3_append","test4_append", "test5..._append","test3_append","test4_append", "test5_append"], append=True)
    # Step4, add values for code_parameters_editor to add values in a column need to specify field_name, append = True
    code_parameters_editor.add_values(*["test1_name","test2_name","test3_name","test4_name"], header='name', append=True)

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
    dataset.save(save_dir=save_dir)









