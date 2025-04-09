"""Example for access protocol through SPARC dataset and download protocol data as json format.

This example shows how users can call the sparc-me API to get the protocol DOI from
a curated SPARC dataset stored on Pennsieve, and then store the data as `JSON` format locally.

Dataset 273 described on the SPARC Portal
(https://sparc.science/datasets/273?type=dataset) is used as an example.
"""

from sparc_me import Dataset_Api
from pathlib import Path

api_tools = Dataset_Api()

def get_access_to_protocols():
    # you can replace your own protocol token
    save_dir = Path(__file__).parent / "dataset"
    api_tools.get_protocolsio_text(273,save_dir, token="d57e959c789395fccae1146de189304222c15859283cc5c2d2dac97b9f69e7c3595da8f5c54ebd0de52b23ffe7af0d11e9f2b0eb226c818bcc295a7c807fce1f")


if __name__ == '__main__':
    get_access_to_protocols()
