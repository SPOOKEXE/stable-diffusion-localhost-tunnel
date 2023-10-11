
import os
from PIL import Image

def MinimumDimensionInDirectory( directory : str, min_sizes=(300,300) ):
    temp_folder = os.path.join(directory, "not_minimum")
    if not os.path.isdir(temp_folder):
        os.makedirs(temp_folder)
    files = os.listdir(directory)
    total_files = len(files)
    print(total_files)
    for i, filename in enumerate(files):
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath):
            continue
        img = Image.open(filepath)
        height, width = img.size
        img.close()
        if (width < min_sizes[0]) or (height < min_sizes[1]):
            print(i, total_files)
            os.rename(filepath, os.path.join(temp_folder, filename) )

print("Input the directory to sort. This sorts non-minimum sized images to a folder. ")
directory = input("")

MinimumDimensionInDirectory(directory, min_sizes=(250,250))
