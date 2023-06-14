import json
import base64
import schemes.simple
import schemes.baseline
import schemes.optimised
import scipy
import numpy
from tqdm import tqdm
import csv
from tabulate import tabulate
import logging
import schemes.util
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

compressors = []
compressors.append(schemes.simple.NullCompressor())
compressors.append(schemes.simple.TLSCertCompression())
compressors.append(schemes.simple.IntermediateSuppression())
compressors.append(schemes.simple.ICAAndTLS())

compressors.append(schemes.baseline.Baseline())
# compressors.append(schemes.optimised.PrefixAndTrained(dictSize=1000,redact=True))
# compressors.append(schemes.optimised.PrefixAndTrained(dictSize=10000,redact=True))
# compressors.append(schemes.optimised.PrefixAndTrained(dictSize=100000,redact=True))
# compressors.append(schemes.optimised.PrefixAndTrained(dictSize=1000,redact=False))
compressors.append(schemes.optimised.PrefixAndTrained(dictSize=10000,redact=False)) # Faster, redact=True shows little diff.
# compressors.append(schemes.optimised.PrefixAndTrained(dictSize=100000,redact=False))
compressors.append(schemes.optimised.PrefixAndSystematic(threshold=100))

data = schemes.util.load_certificates()
data = random.sample(data,1000)
logging.info(f"Selected sample of {len(data)} certificate chains for benchmark")
results = dict();
for s in compressors:
    results[s.name()] = list()

for entry in tqdm(data,desc="Benchmarking Compression Schemes"):
    entry = [base64.b64decode(x) for x in entry]
    for scheme in compressors:
        size = len(scheme.compress(entry))
        #print(f"{scheme.name()}= {size}")
        results[scheme.name()].append(size)

stats = [(f"p{y}", lambda x, y=y: numpy.percentile(x, y)) for y in [5,50,95]]

with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Scheme'] + [name for name, _ in stats])  # Write header row

    for scheme, sizes in tqdm(results.items(),desc='Computing Confidence Intervals'):
        row = [scheme]
        for statName, stat in stats:
            lower,upper = scipy.stats.bootstrap([sizes], stat, method='percentile').confidence_interval
            if upper - lower > 100:
                logging.warning(f"Large Confidence Interval for {scheme} {statName} of [{lower:.1f},{upper:.1f}] bytes")
            row.append(upper)
        writer.writerow(row)

print()
with open('output.csv', 'r') as file:
    csv_reader = csv.reader(file)
    table_data = list(csv_reader)
table = tabulate(table_data, headers="firstrow", tablefmt="github",floatfmt=".0f")
print(table)