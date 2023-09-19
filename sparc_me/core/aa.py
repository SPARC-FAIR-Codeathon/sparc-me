"""aa模块的文档注释"""


class Aa(object):
    """
        Aa类的注释
    """

    @staticmethod
    def aa_api(x, y):
        """
        求商
        :param x: 整数
        :param y: 不能为零的整数
        :return: 两数之商
        """
        return x / y

class Metadata(object):
    """
        metadata类的注释
    """
    def __init__(self, metadata_file, metadata, version, dataset_path):
        """
        :param metadata_file: metadata file name
        :type metadata_file: str
        :param metadata: metadata dataframe content
        :type metadata: Dataframe
        :param version: dataset version
        :type version: "2.0.0" | "1.2.3"
        :param dataset_path: root dataset path
        :type dataset_path: Path
        """
        self.metadata_file = metadata_file
        self.data = metadata
        self.version = version
        self.metadata_file_path = Path(dataset_path).joinpath(f"{metadata_file}.xlsx")