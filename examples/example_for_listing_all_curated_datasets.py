"""Example for access SPARC dataset by Pennsieve API.
This example shows we can list all SPARC datasets from Pennsieve API

"""

from sparc_me import Dataset_Api
import time

api_tools = Dataset_Api()

def get_All_Datasets():
    '''
    time cost 110.3494348526001 s
    :return:
    '''
    time_start = time.time()
    datasets = api_tools.get_all_datasets_all_versions()
    time_end = time.time()
    print(datasets)
    print("Count: " + str(len(datasets)))
    print('time cost', time_end - time_start, 's')

def get_All_latest_DataSets_from_SPARC():
    '''
    time cost 1.9873650074005127 s
    :return:
    '''
    time_start = time.time()

    datasets = api_tools.get_all_datasets_latest_version_pensieve()
    time_end = time.time()
    print(datasets)
    print("Count: "+str(len(datasets)))
    print('time cost',time_end-time_start,'s')



if __name__ == '__main__':
    get_All_latest_DataSets_from_SPARC()
    get_All_Datasets()
