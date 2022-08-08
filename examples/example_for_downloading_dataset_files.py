"""Example for downloading and exploring curated SPARC datasets.

Dataset 156 described on the SPARC Portal 
(https://sparc.science/datasets/156?type=dataset) is used as an example.
"""

from sparc_me import Dataset_Api
from decouple import config


if __name__ == '__main__':
    '''
    To get the API-key please see here: https://github.com/tgbugs/ontquery#scicrunch-api-key
    To config API-key to local environment variables:
    create a .env in project root folder
    pip install decouple
    from decouple import config
    SCICRUNCH_API_KEY = config('SCICRUNCH_API_KEY')
    '''
   
    SCICRUNCH_API_KEY = config('SCICRUNCH_API_KEY')

    api_tools = Dataset_Api()
    api_tools.get_xlsx_csv_file_pennsieve(156, "files/dataset_description.xlsx", "./datasets")
    api_tools.get_xlsx_csv_file_pennsieve(156, "files/docs/humanWholeBody_annotations.csv", "./datasets")
    api_tools.get_UBERONs_From_Dataset(156, "files/docs/humanWholeBody_annotations.csv")
