import schemes.zstd_base
import schemes.ccadb
import json
import base64
import tempfile

class DictCompress:
    def __init__(self, entries):
        self.cmap = dict()
        self.dmap = dict()
        prefix = b'\x12\x34'
        identifier = 0
        for e in entries:
            eid = prefix + identifier.to_bytes(2,'big')
            self.cmap[e] = eid
            self.dmap[eid] = e
            identifier += 1

    def name(self):
        return "Base: Dictionary Compressor"

    def compress(self, certList):
        compressed = b""
        for c in certList:
            if c in self.cmap.keys():
                compressed += self.cmap[c]
            else:
                compressed += c
        return compressed

    def decompress(self, compressed_data):
        #TODO - Needs to know to skip the first cert
        pass

class Optimised:
    def __init__(self):
        self.inner1 = DictCompress(schemes.ccadb.ccadb_certs())
        self.inner2 = schemes.zstd_base.ZstdBase(shared_dict=self.buildEEDict('data/chains.json'))

    def name(self):
        return "Method 2: Optimised"

    def compress(self, certList):
        return self.inner2.compressBytes(self.inner1.compress(certList))

    def decompress(self, compressed_data):
        return self.inner1.decompress(self.inner2.decompress(compressed_data))


    def buildEEDict(self,certJSON):
        # TODO Duplicates code in bench.py
        # TODO actually static
        with open(certJSON) as json_file:
            data = json.load(json_file)
            data = data[-2000:]
            ee = [base64.b64decode(x[0]) for x in data]
        with tempfile.TemporaryDirectory() as temp_dir:
            for index, cert in enumerate(ee):
                file_path = f"{temp_dir}/{index}.bin"
                with open(file_path, 'wb') as file:
                    file.write(cert)
            schemes.zstd_base.zstdTrain(1000,temp_dir)
            with open(f"{temp_dir}/dictionary.bin",'rb') as dFile:
                dBytes = dFile.read()
                return dBytes