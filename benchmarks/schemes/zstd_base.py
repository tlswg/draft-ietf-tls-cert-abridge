import tempfile
import subprocess


def zstdTrain(targetSize,targetDirectory):
    command = [
        "zstd",
        "--train",
        "-r",
        targetDirectory,
        #f"--maxdict={targetSize}", #TODO Fix
        "-9",
        "-o",
        f"{targetDirectory}/dictionary.bin"
    ]
    #print(" ".join(command))
    result = subprocess.run(command, capture_output=True,shell=False)
    #print(result.stderr)

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

    def compress(self,certList):
        return self.compressBytes(b"".join(certList))

    def compressBytes(self, data):
        #TODO: Change to using stdin.
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
            temp_file.write(data)
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