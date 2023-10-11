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

def image_has_tags( directory : str, filename : str, tags : list ) -> bool:
    json_filename, json_filepath = get_json_filepath( directory, filename )
    if not os.path.isfile(json_filepath):
        return False
    with open(json_filepath, "r") as file:
        data = file.read()
    for tag in tags:
        if data.find(tag) != -1:
            return True
    return False

def filter_images_from_list( items : list[str] ) -> list[str]:
    filtered = []
    for item in items:
        if is_image_file(item):
            filtered.append(item)
    return filtered

def SortTagToFolder( directory : str, tags : list ) -> None:
    temp_folder = os.path.join(directory, "furry")
    if not os.path.isdir(temp_folder):
        os.makedirs(temp_folder)
    files = filter_images_from_list( os.listdir(directory) )
    total_files = len(files)
    print(total_files)
    for i, filename in enumerate(files):
        filepath = os.path.join(directory, filename)
        if image_has_tags( directory, filename, tags ):
            print(i, total_files, filename)
            json_filename, json_filepath = get_json_filepath( directory, filename )
            os.rename(filepath, os.path.join(temp_folder, filename) )
            os.rename(json_filepath, os.path.join(temp_folder, json_filename) )

print("Input the directory to sort. This sorts furry content to a separate folder. ")
directory = input("")

SortTagToFolder( directory, ["furry_female", "furry_male", "furry"] )
