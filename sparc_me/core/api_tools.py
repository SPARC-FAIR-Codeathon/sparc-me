# python -m pip install requests
import requests
import json
from pathlib import Path
import re
import zipfile


class Dataset_Api:

    def __init__(self):
        pass

    def get_dataset_versions_pensieve(self, datasetId):
        '''
            get one dataset all versions
        :return: versions
        '''

        if not isinstance(datasetId, str):
            datasetId = str(datasetId)

        url = "https://api.pennsieve.io/discover/datasets/" + datasetId + "/versions"

        headers = {"Accept": "application/json"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            versions = json.loads(response.text)
            return versions

    def get_all_datasets_all_versions(self):
        '''
            Get all datasets with all versions
            It may cost a few minutes to get the whole data,
            Because some dataset have a lot of versions, e.g, 20,
            And every time when the version number getter than 1,
            it will request server for getting new data, so it waste a lot of time.

        :return: datasets
        '''
        datasets = []

        latest_datasets = self.get_all_datasets_latest_version_pensieve()
        for dataset in latest_datasets:
            if dataset["version"] > 1:
                versions = self.get_dataset_versions_pensieve(dataset["id"])
                for version in versions:
                    datasets.append(version)
            else:
                datasets.append(dataset)

        return datasets

    def get_all_datasets_latest_version_pensieve(self):
        '''
            Get all datasets with latest version
        :return: datasets | []
        '''

        url = "https://api.pennsieve.io/discover/datasets?limit=2147483647&offset=0&orderBy=relevance&orderDirection=desc"

        headers = {"Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers)
            response_json = json.loads(response.text)
            datasets = response_json["datasets"]

            return datasets
        except:
            print("bad connect! 404")

        return []

    def get_dataset_latest_version_pensieve(self, datasetId):
        '''
         :parameter: datasetId : String
         :return:
        '''
        if isinstance(datasetId, int):
            datasetId = str(datasetId)
        elif isinstance(datasetId, str):
            pass
        else:
            return
        url = "https://api.pennsieve.io/discover/datasets/" + datasetId

        headers = {"Accept": "application/json"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return json.loads(response.text)

    def get_metadata_pensieve(self, datasetId, versionId):
        '''
            Get a metadata from the specific version
        :return: metadata json format
        '''

        if not isinstance(datasetId, str):
            datasetId = str(datasetId)
            versionId = str(versionId)

        url = "https://api.pennsieve.io/discover/datasets/" + datasetId + "/versions/" + versionId + "/metadata"

        headers = {"Accept": "application/json"}

        response = requests.get(url, headers=headers)

        print(isinstance(response.text, str))
        if response.status_code == 200:
            return json.loads(response.text)

    def get_dataset_latest_version_number(self, datasetId):
        if not isinstance(datasetId, str):
            datasetId = str(datasetId)
        url = "https://api.pennsieve.io/discover/datasets/" + datasetId
        headers = {"Accept": "application/json"}
        response = requests.request("GET", url, headers=headers)
        response_json = json.loads(response.text)
        if response.status_code == 200:
            versionId = str(response_json['version'])
        else:
            versionId = ""
        return versionId

    '''
    not finish
    '''
    def download_file(self, datasetId, filepath):
        versionId = self.get_dataset_latest_version(datasetId)

        url = "https://api.pennsieve.io/zipit/discover"

        payload = {"data": {
            "paths": [filepath],
            "datasetId": datasetId,
            "version": versionId
        }}
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code == 200:
            return response
        else:
            return response.reason