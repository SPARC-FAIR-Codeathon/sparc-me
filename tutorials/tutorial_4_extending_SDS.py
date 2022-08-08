"""
This tutorial will walk you through the steps of
extending a field to a existing metadata
and updating the metadata schema accordingly
"""
from sparc_me import Dataset, Schema

if __name__ == '__main__':
    # Create a SDS dataset from template
    dataset = Dataset()
    dataset.load_from_template(version="1.2.3")
    dataset.save(save_dir="./tmp/template/")

    # Save the default schema
    default_schema = Schema.get_default_schema(version="1.2.3", category="dataset_description")
    schema = Schema()
    schema.set_schema(default_schema)
    schema.save(save_dir="./tmp/", category="dataset_description")
    #
    # Extend metadata - adding a new field
    category = "dataset_description"
    element = "consent_code"
    dataset.add_element(category=category, element=element)
    dataset.save(save_dir="./tmp/template/")
    # Update schema
    property = {
        "type": "string",
        "required": "N",
        "description": "Consent code",
        "Example": "test"
    }
    schema.add_property(property_name=element, property=property)
    schema.save(save_dir="./tmp/", category="dataset_description")





