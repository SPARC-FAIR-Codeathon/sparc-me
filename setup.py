from setuptools import setup, find_packages

setup(
    name="sparc_me",
    version="1.0.11",
    description='The SPARC Metadata Editor (sparc-me) is a python tool to explore, enhance, and expand SPARC datasets and their descriptions in accordance with FAIR principles. Examples and tutorials are provided to demonstrate the use of the tool to programatically access curated datasets and their protocols, create new datasests, enhance dataset descriptions via schema extensions, conversion of data from other formats to the SPARC dataset structure, and demonstrates how the tool can be used with existing SPARC infrastructure such as o²S²PARC and the SciCrunch knowledgebase',
    author="Thiranja Prasad Babarenda Gamage, Chinchien Lin, Savindi Wijenayaka, Michael Hoffman, Linkun Gao, Haribalan Kumar",
    email="psam012@aucklanduni.ac.nz, clin864@aucklanduni.ac.nz",
    license="Apache-2.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['resources./*']},
    install_requires=[
        'pandas',
        'styleframe',
        'xlrd',
        'openpyxl',
        'jsonschema',
        'requests',
        'pybids'
    ]
)
