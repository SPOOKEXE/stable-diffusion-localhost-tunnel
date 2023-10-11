import os

VALID_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp", ".bmp"]

def is_image_file(filepath : str) -> bool:
    filename = os.path.basename(filepath).lower()
    for ext in VALID_IMAGE_EXTENSIONS:
        if filename.endswith(ext):
            return True
    return False

def get_json_filepath( directory : str, filename : str ) -> tuple[str, str]:
    filename = os.path.basename(filename)
    name, ext = os.path.splitext(filename)
    json_filename = f"{name}.json"
    json_filepath = os.path.join( directory, json_filename )
    return json_filename, json_filepath

def image_has_tags_file( directory : str, filename : str ) -> bool:
    json_filename, json_filepath = get_json_filepath( directory, filename )
    return os.path.isfile(json_filepath)

def filter_images_from_list( items : list[str] ) -> list[str]:
    filtered = []
    for item in items:
        if is_image_file(item):
            filtered.append(item)
    return filtered

def SortNoTagsToFolder( directory : str ) -> None:
    temp_folder = os.path.join(directory, "no_tags")
    if not os.path.isdir(temp_folder):
        os.makedirs(temp_folder)
    files = filter_images_from_list( os.listdir(directory) )
    total_files = len(files)
    print(total_files)
    for i, filename in enumerate(files):
        filepath = os.path.join(directory, filename)
        if not image_has_tags_file( directory, filename ):
            print(i, total_files, filename)
            os.rename(filepath, os.path.join(temp_folder, filename) )

print("Input the directory to sort. This moves all non-tagged files to a separate folder. ")
directory = input("")

SortNoTagsToFolder( directory )
