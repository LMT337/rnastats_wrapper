import csv, os, subprocess, time, argparse

results = {}

# input woid
parser = argparse.ArgumentParser()
parser.add_argument('-w', help='input woid', type=str)
args = parser.parse_args()

woid = args.w
print('RNA-Wrapping: {}'.format(woid))
results['work order'] = woid

# dir check
cwd = os.getcwd()
if os.path.exists(woid):
    print('{} exists. Files output to:\n{}'.format(woid,cwd))
if not os.path.exists(woid):
    print('{} Does not exist. Creating {} dir.\nFiles output to:\n{}'.format(woid, cwd))
    os.mkdir(woid)

# generate collection
admin_collections = subprocess.check_output(["wo_info", "--report", "billing", "--woid", woid]).decode(
        'utf-8').splitlines()
for ap in admin_collections:
    print(ap)
    if 'Administration Project' in ap:
        collection = ap.split(':')[1].strip()
print('Admin: {}'.format(collection))
results['Admin'] = collection

# input master sample sheet for Tissue, Sample Type
lims_url = 'https://imp-lims.gsc.wustl.edu/entity/setup-work-order/{}?perspective=Sample'.format(woid)
print('lims sample link:\n{}\nInput samples:'.format(lims_url))

while True:
    samples = []
    while True:
        sample_line = input()
        if sample_line:
            samples.append(sample_line)
        else:
            break
    if len(samples) <= 1:
        print('Please include samples or add header line.')
        continue
    if 'Barcode' not in samples[0]:
        print('Please include header line.')
        continue
    else:
        break

# remove first header line, change dir
samples[:] = [x for x in samples if 'WOI' not in x]
os.chdir(woid)

# write to sample master file
with open(woid+'.master.samples.tsv', 'w') as mastercsv:
    for line in samples:
        mastercsv.write('{}\n'.format(line))

# add sample file info to results
with open(woid+'.master.samples.tsv', 'r') as mastercsv:
    master_reader = csv.DictReader(mastercsv, delimiter='\t')
    for line in master_reader:
        results['Tissue Prep Type'] = line['Tissue Prep Type']
        results['Sample Type'] = line['Sample Type']
        results['DNA Type'] = line['DNA Type']

print(results)








