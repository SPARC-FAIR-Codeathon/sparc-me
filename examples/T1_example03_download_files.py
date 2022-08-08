from sparc_me import Dataset_Api

from decouple import config


if __name__ == '__main__':
    SCICRUNCH_API_KEY = config('SCICRUNCH_API_KEY')

    api_tools = Dataset_Api()
    api_tools.get_xlsx_csv_file_pennsieve(156, "files/dataset_description.xlsx", "./datasets")
    api_tools.get_xlsx_csv_file_pennsieve(156, "files/docs/humanWholeBody_annotations.csv", "./datasets")
    api_tools.get_UBERONs_From_Dataset(156, "files/docs/humanWholeBody_annotations.csv")