import os
import shutil

def add_data(source_path, destination_path, copy=True, overwrite=False):
    """Copy or move data from source folder to destination folder

    :param source_path: path to the original data
    :type source_path: string
    :param destination_path: folder path to be copied into
    :type destination_path: string
    :param copy: if True, source directory data will not be deleted after copying, defaults to True
    :type copy: bool, optional
    :param overwrite: if True, any data in the destination folder will be overwritten, defaults to False
    :type overwrite: bool, optional
    :raises FileExistsError: if the destination folder contains data and overwritten is set to False, this wil be raised.
    """

    # If overwrite is True, remove existing sample
    if os.path.exists(destination_path):
        if overwrite: 
            shutil.rmtree(destination_path)
        else:
            raise FileExistsError("Destination file already exist. Indicate overwrite argument as 'True' to overwrite the existing")

    # Create destination folder
    os.makedirs(destination_path)

    for fname in os.listdir(source_path):
        file_path = os.path.join(source_path, fname)
        if os.path.isdir(file_path):
            # Warn user if a subdirectory exist in the input_path
            print(f"Warning: Input directory consist of subdirectory {source_path}. It will be avoided during copying") 
        else:
            if copy:
                # Copy data
                shutil.copy2(file_path, destination_path)
            else:
                # Move data
                shutil.move(file_path, os.path.join(destination_path, fname))
