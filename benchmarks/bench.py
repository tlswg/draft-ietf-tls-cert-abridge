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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

compressors = []
compressors.append(schemes.simple.NullCompressor())
compressors.append(schemes.simple.IntermediateSuppression())
compressors.append(schemes.simple.TLSCertCompression())
compressors.append(schemes.simple.ICAAndTLS())

compressors.append(schemes.baseline.Baseline())
compressors.append(schemes.optimised.Optimised())

with open('data/chains.json') as json_file:
    data = json.load(json_file)
    logging.info(f"Loaded {len(data)} certificate chains for evaluation")
    data = data[0:5000]

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