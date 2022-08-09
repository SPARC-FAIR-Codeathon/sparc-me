"""Example for access protocol through SPARC dataset and download protocol data as json format.

This example shows how users can call the sparc-me API to get the protocol DOI from
a curated SPARC dataset stored on Pennsieve, and then store the data as `JSON` format locally.

Dataset 273 described on the SPARC Portal
(https://sparc.science/datasets/273?type=dataset) is used as an example.
"""

from sparc_me import Dataset_Api

api_tools = Dataset_Api()

def get_access_to_protocols():
    api_tools.get_protocolsio_text(273,"./datasets")

if __name__ == '__main__':
    get_access_to_protocols()
