from sparc_me import Dataset_Api
import time

if __name__ == '__main__':
    api_tools = Dataset_Api()
    start = time.time()
    # api_tools.download_dataset(156, 1)
    # api_tools.download_dataset(156, -1)
    # api_tools.download_dataset(156, 11)
    # api_tools.download_dataset(156, "1")
    # api_tools.download_dataset(156, "11")
    # api_tools.download_dataset("156", "11")
    # api_tools.download_dataset(156, "-11")
    # api_tools.download_dataset(156)
    api_tools.download_dataset(332)
    end = time.time()

    print("multi-threads to download dataset 156 cost:", end - start, "seconds!")
