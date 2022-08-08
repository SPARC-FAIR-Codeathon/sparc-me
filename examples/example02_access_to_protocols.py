from sparc_me import Dataset_Api

api_tools = Dataset_Api()

def get_access_to_protocols():
    api_tools.get_protocolsio_text(273,"./datasets")

if __name__ == '__main__':
    get_access_to_protocols()