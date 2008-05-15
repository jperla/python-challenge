import os
import tarfile

def extract_tarfile(filename):
    tar = tarfile.open(filename)
    tar.extractall()
    tar.close()

def create_tarfile(tar_filename, filenames_to_add):
    import tarfile
    if tar_filename.endswith('gz'):
        tar = tarfile.open(tar_filename, "w:gz")
    else:
        tar = tarfile.open(tar_filename, "w")
    for name in filenames_to_add:
        tar.add(name)
    tar.close()
