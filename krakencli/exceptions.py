
class InvalidKeyFile(Exception):

    def __init__(self, file_path):
        self.file_path = file_path
        super().__init__(f"Key file {self.file_path} is not formatted properly")