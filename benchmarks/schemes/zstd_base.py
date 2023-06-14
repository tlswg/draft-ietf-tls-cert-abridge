import tempfile
import subprocess

class ZstdBase:

    def __init__(self,shared_dict=None):
        self.dictBytes = shared_dict
        if shared_dict:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
                temp_file.write(self.dictBytes)
            self.dictFile = temp_file.name
        else:
            self.dictFile = None

    def name(self):
        return "Zstd Base"

    def compress(self, certList):
        #TODO: Change to using stdin.
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
            temp_file.write(b"".join(certList))
            name = temp_file.name
        command =  [
            "zstd",
            "-f",
            "-9",
            "-q",
            "--single-thread",
            "--zstd=searchLog=30",
            "--zstd=hashLog=30",
            "--zstd=chainLog=30",
            "--zstd=targetLength=6000",
        ]
        if self.dictFile:
            command.append('--patch-from')
            command.append(self.dictFile)
        command.append('-c')
        command.append(name)
        completed_process = subprocess.run(command, capture_output=True,shell=False)
        return completed_process.stdout

    def decompress(self, compressed_data):
        # TODO Not Implemented
        pass