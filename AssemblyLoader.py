import base64

def load_assembly_from_file(file_path):
    in_file = open(file_path, "rb")
    data = in_file.read()
    in_file.close()
    return base64.b64encode(data).decode("utf-8")