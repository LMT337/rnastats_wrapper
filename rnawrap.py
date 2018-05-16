import csv, os, datetime, argparse, subprocess, glob

working_dir = '/gscmnt/gc2783/qc/RNA2018/'

# generate date month/day/year string
mm_dd_yy = datetime.datetime.now().strftime("%m/%d/%y")
mmddyy = datetime.datetime.now().strftime("%m%d%y")

# input woid
parser = argparse.ArgumentParser()
parser.add_argument('-w', help='input woid', type=str)
parser.add_argument('-f', help='input woid', type=str)
args = parser.parse_args()

# process inputs to woids list
woids = []
if args.w:
    woids = args.w.split(',')
if args.f:
    with open(args.f, 'r') as infilecsv:
        woids = infilecsv.read().splitlines()
woids = list(filter(None, woids))


def sample_file():
    with open('{}.master.samples.tsv'.format(woid), 'r') as mastercsv:
        master_reader = csv.DictReader(mastercsv, delimiter='\t')
        for line in master_reader:
            results['Tissue Prep Type'] = line['Tissue Prep Type']
            results['Sample Type'] = line['Sample Type']
            results['DNA Type'] = line['DNA Type']
    return


def create_master(workorderid):
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

    # remove first header line
    samples[:] = [x for x in samples if 'WOI' not in x]

    # write to sample master file
    with open('{}.master.samples.tsv'.format(woid), 'w') as mastercsv:
        for line in samples:
            mastercsv.write('{}\n'.format(line))
    return


directory_summary = dict()
for woid in woids:

    # set working dir
    os.chdir(working_dir)

    print('---\nRNA-Wrapping: {}'.format(woid))

    results = dict()
    results['work order'] = woid
    results["Date QC'ed"] = mm_dd_yy

    # generate collection
    admin_collections = subprocess.check_output(["wo_info", "--report", "billing", "--woid", woid]).decode('utf-8') \
        .splitlines()
    for ap in admin_collections:
        print(ap)
        if 'Administration Project' in ap:
            collection = ap.split(':')[1].strip()
    results['Admin'] = collection

    # dir check
    if os.path.exists(woid):
        os.chdir(woid)
        print('{} directory exists.\nOutput directory:\n{}'.format(woid,'{}{}/'.format(working_dir, woid)))
        response_continue = input('Continue writing to this directory? ({} file will be overwritten)\n'
                                  .format('{}.rna.summary.stats.{}.tsv'.format(woid, mmddyy)))
        if 'y' in response_continue.lower():
            if not os.path.isfile('{}.master.samples.tsv'.format(woid)):
                create_master(woid)
            if os.path.isfile('{}.master.samples.tsv'.format(woid)):
                response = input('Use existing {}?\n'.format('{}.master.samples.tsv'.format(woid)))
                if 'y' not in response.lower():
                    create_master(woid)
                if 'y' in response.lower():
                    pass
        if 'y' not in response_continue:
            directory_summary[woid] = 'woid directory exists, user skipped.'
            continue

    if not os.path.exists(woid):
        print('{} does not exist, creating {} dir.\nOutput directory:\n{}'.format(woid, woid,
                                                                                  '{}{}/'.format(working_dir, woid)))
        os.mkdir(woid)
        os.chdir(woid)
        create_master(woid)

    # add sample file info to results
    sample_file()

    # remove SpliceJunctionMetrics.tsv or rnastats.pl will error out
    splice_files = glob.glob('*SpliceJunctionMetrics.tsv')
    for file in splice_files:
        os.remove(file)

    # run rnstats script to generate rna stats
    print('---\nRunning rnastats_test.pl\n---')
    subprocess.run(['perl', '/gscuser/awollam/aw/rnastats.pl', "--id", woid])

    # add rnastats to results, output results file for each sample in rnastats.
    with open('{}.rna.stats.tsv'.format(woid), 'r') as rnastatscsv, \
            open('{}.rna.summary.stats.{}.tsv'.format(woid, mmddyy), 'w') as resultscsv:

        rna_stats_reader = csv.DictReader(rnastatscsv, delimiter='\t')
        rna_stats_header = rna_stats_reader.fieldnames

        # create outfile header
        outfile_header_prepend = ['Admin', 'work order', 'Date QC\'ed']
        outfile_header_append = ['Tissue Prep Type', 'Sample Type', 'DNA Type']
        results_header = outfile_header_prepend + rna_stats_header + outfile_header_append

        results_writer = csv.DictWriter(resultscsv, fieldnames=results_header, delimiter='\t')
        results_writer.writeheader()

        # write results
        for line in rna_stats_reader:
            for metric in line:
                results[metric] = line[metric]
            results_writer.writerow(results)

    # check results file, if only one line, rnastats failed.
    results_file_len = sum(1 for line in open('{}.rna.summary.stats.{}.tsv'.format(woid, mmddyy)))
    if results_file_len == 1:
        print('***rnastats_test.pl {} failed***'.format(woid))
        directory_summary[woid] = 'rnastats failed'
    else:
        directory_summary[woid] = '{}{}/{}.rna.summary.stats.{}.tsv'.format(working_dir, woid, woid, mmddyy)

    print('---\n{} Wrapped.\n---\n'.format(woid))
    os.chdir(working_dir)

print('rnawrap output summary:\nWork Order\tDirectory')
for directory in directory_summary:
    print('{}\t{}'.format(directory, directory_summary[directory]))
print()

