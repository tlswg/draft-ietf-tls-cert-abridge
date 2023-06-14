import json
import base64
import schemes.simple
import schemes.baseline
import statistics
from tqdm import tqdm

compressors = []
compressors.append(schemes.simple.NullCompressor())
compressors.append(schemes.simple.IntermediateSuppression())
compressors.append(schemes.simple.TLSCertCompression())
compressors.append(schemes.simple.ICAAndTLS())

compressors.append(schemes.baseline.Baseline())

with open('data/chains.json') as json_file:
    data = json.load(json_file)
    data = data[0:1000]

results = dict();
for s in compressors:
    results[s.name()] = list()

for entry in tqdm(data):
    entry = [base64.b64decode(x) for x in entry]
    for scheme in compressors:
        size = len(scheme.compress(entry))
        #print(f"{scheme.name()}= {size}")
        results[scheme.name()].append(size)

for key, value in results.items():
    median = statistics.median(value)
    print(f"{key}: {median}")