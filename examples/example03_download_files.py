from sparc_me import Dataset_Api
import os
from decouple import config

if __name__ == '__main__':
    api_tools = Dataset_Api()
    api_tools.get_xlsx_file_pennsieve(156, "files/dataset_description.xlsx", "./datasets")
    api_tools.get_xlsx_file_pennsieve(156, "files/docs/humanWholeBody_annotations.csv", "./datasets")
    print(os.environ['SCICRUNCH_API_KEY'])