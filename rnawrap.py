import csv, os, subprocess, time, argparse

# input woid
parser = argparse.ArgumentParser()
parser.add_argument('-w', help='input woid', type=str)
args = parser.parse_args()

woid = args.w

# generate collection
admin_collections = subprocess.check_output(["wo_info", "--report", "billing", "--woid", woid]).decode(
        'utf-8').splitlines()
for ap in admin_collections:
    print(ap)
    if 'Administration Project' in ap:
        collection = ap.split(':')[1].strip()




