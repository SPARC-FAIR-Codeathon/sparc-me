import requests
import json
from pathlib import Path
import io
import pandas as pd
import queue
import threading
import os



class Dataset_Api:

    def __init__(self):
        pass

    def get_dataset_versions_pensieve(self, datasetId):
        """
        get one dataset all versions
        
        :param datasetId: the dataset id from SPARC
        :type datasetId: str|int
        :return: versions
        """

        if not isinstance(datasetId, str):
            datasetId = str(datasetId)

        url = "https://api.pennsieve.io/discover/datasets/" + datasetId + "/versions"

        headers = {"Accept": "application/json"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            versions = json.loads(response.text)
            return versions

    def get_all_datasets_all_versions(self):
        """
        
        Get all datasets with all versions
        It may cost a few minutes to get the whole data,
        Because some dataset have a lot of versions, e.g, 20,
        And every time when the version number getter than 1,
        it will request server for getting new data, so it waste a lot of time.

        :return: datasets
        """
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
        """
        Get all datasets with latest version
            
        :return: datasets | []
        """

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
        """
        
        :param datasetId: the dataset id from SPARC
        :type datasetId: str|int
        :return:
        """

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
        """
         Get a metadata from the specific version

         :param datasetId: 
         :type datasetId: str | int
         :param versionId:
         :type versionId: str | int
         :return: metadata json format
        """

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

    def _download_file(self, datasetId, filepath):
        """
        Download bytes files from Pennsieve
        
        :param datasetId: 
        :param filepath: file path from 
        :return: 
        """
        versionId = self.get_dataset_latest_version_number(datasetId)

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

    def get_xlsx_csv_file_pennsieve(self, datasetId, filepath, savepath):
        """
        
        store excel file locally
        :param datasetId: dataset id from SPARC
        :param filepath: dataset version from SPARC
        :param savepath: Path for save dataset
        """
            
        pathList = filepath.split('.')
        extension = pathList[1]
        fileStrList = filepath.split('/')
        i = len(fileStrList)
        filename = fileStrList[i - 1]
        relative_path = '/'
        for r in fileStrList[0:i - 1]:
            relative_path += r + "/"
        savepath = savepath + relative_path

        save_dir = Path(savepath)
        if not save_dir.is_dir():
            save_dir._mkdir(parents=True, exist_ok=False)
        response = self._download_file(datasetId, filepath)

        if extension == "xlsx":
            with io.BytesIO(response.content) as fh:
                df = pd.io.excel.read_excel(fh, engine='openpyxl')
            df.dropna(axis=0, how='all', inplace=True)
            writer = pd.ExcelWriter(savepath + filename)
            df.to_excel(writer)
            writer.save()

        elif extension == "csv":
            with io.BytesIO(response.content) as fh:
                df = pd.read_csv(fh)
            df.to_csv(savepath + filename, sep=',', header=False, index=False)

    def get_UBERONs_From_Dataset(self, datasetId, filepath):
        response = self._download_file(datasetId, filepath)
        with io.BytesIO(response.content) as fh:
            df = pd.read_csv(fh)
        df = df.dropna(axis=0, how='any')
        return df['Term ID']

    '''
    TODO: download whole dataset
    '''

    def _mkdir(self, paths):
        for path in paths:
            savepath = "dataset/"
            fileStrList = path.split('/')
            i = len(fileStrList)
            relative_path = '/'
            for r in fileStrList[0:i - 1]:
                relative_path += r + "/"
            savepath = savepath + relative_path
            folder = os.path.exists(savepath)
            if not folder:
                os.makedirs(savepath)

    def get_all_files_path(self, dataset_id, version_id):
        url = f"https://api.pennsieve.io/discover/datasets/{dataset_id}/versions/{version_id}/metadata"

        headers = {"Accept": "application/json"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            files = json.loads(response.text)["files"]
            paths = []
            for idx in range(len(files)):
                paths.append(files[idx]["path"])
            return paths

    def _craw(self, datasetId, versionId, url_queue: queue.Queue, html_queue: queue.Queue):
        '''
          Download bytes files from Pennsieve
        '''
        while True:
            if url_queue.qsize() == 0:
                break
            filepath = url_queue.get()
            if filepath is None:
                html_queue.put(None)
                continue

            url = "https://api.pennsieve.io/zipit/discover"

            payload = {"data": {
                "paths": [filepath],
                "datasetId": datasetId,
                "version": versionId
            }}
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.request("POST", url, json=payload, headers=headers, stream=True)
                if response.status_code == 200:
                    contentObj = {
                        "content": response.content,
                        "filepath": filepath,
                    }
                    html_queue.put(contentObj)
            except Exception as e:
                print(f"The file: {filepath} download failed! The error is {e}")

    def _parse(self, html_queue: queue.Queue):
        while True:
            res = html_queue.get()
            if res is None:
                print("finish downloading dataset!")
                break
            with io.BytesIO(res["content"]) as io_file:
                with open("dataset/" + res["filepath"], 'wb') as file:
                    file.write(io_file.getvalue())

    def download_dataset(self, dataset_id, version_id=None):
        latest_version_id = self.get_dataset_latest_version_number(dataset_id)
        if latest_version_id == '':
            print("No dataset from SPARC!")
            return
        if version_id is None:
            version_id = latest_version_id
        version_id = str(version_id)
        if int(version_id) > int(latest_version_id):
            version_id = latest_version_id
            print(
                "Your input version ID is greater that the one exist in SPARC dataset, Now will download the latest version in SPARC for you!")
        if int(version_id) < 1:
            version_id = "1"
            print("Invalid version id, Now will download the first version of the dataset for you!")

        paths = self.get_all_files_path(dataset_id, version_id)
        self._mkdir(paths)
        url_queue = queue.Queue()
        html_queue = queue.Queue()
        threads = []

        for url in paths:
            url_queue.put(url)

        url_queue.put(None)
        url_queue.put(None)
        url_queue.put(None)

        for idx in range(3):
            t1 = threading.Thread(target=self._craw, args=(dataset_id, version_id, url_queue, html_queue))
            threads.append(t1)
            t1.start()
        for idx in range(2):
            t2 = threading.Thread(target=self._parse, args=(html_queue,))
            t2.start()

        for t in threads:
            t.join()

    def get_dataset_protocolsio_link(self, datasetId):
        dataset = self.get_dataset_latest_version_pensieve(datasetId)
        protocol_url = ""

        if dataset:
            if (len(dataset["externalPublications"]) > 0):
                protocol_url = dataset["externalPublications"][0]["doi"]

        return protocol_url

    def get_protocolsio_text(self, datasetId, save_dir, token="d57e959c789395fccae1146de189304222c15859283cc5c2d2dac97b9f69e7c3595da8f5c54ebd0de52b23ffe7af0d11e9f2b0eb226c818bcc295a7c807fce1f"):
        if not save_dir.exists():
            save_dir.mkdir()

        protocol_url = self.get_dataset_protocolsio_link(datasetId)
        if protocol_url:
            doi = protocol_url
            url = "https://www.protocols.io/api/v4/protocols/" + doi
            headers = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            response = requests.request(
                "GET", url, headers=headers)
            if response.status_code == 200:
                protocol_json = json.loads(response.content)
                with open(save_dir / 'protocol_data.json', 'w') as f:
                    json.dump(protocol_json, f)

