from setuptools import setup, find_packages

setup(
    name="sparc_me",
    version="2.2.0",
    description='A python tool to explore, enhance, and expand SPARC datasets and their descriptions in accordance with FAIR principles.',
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
