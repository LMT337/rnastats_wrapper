import os, csv, glob, datetime

working_dir = '/gscmnt/gc2783/qc/RNA2018/dev'
os.chdir(working_dir)
mmddyy = datetime.datetime.now().strftime("%m%d%y")
outfile = 'rnacat.summary.{}.tsv'.format(mmddyy)
if os.path.isfile(outfile):
    os.remove(outfile)
rna_summary_files = glob.glob('285*/285*.rna.summary.stats.*')


def file_cat(file):
    if not os.path.isfile(outfile):
        with open(file, 'r') as infilecsv, open(outfile, 'w') as outfilecsv:
            infile_reader = csv.DictReader(infilecsv, delimiter='\t')
            header = infile_reader.fieldnames
            outfile_writer = csv.DictWriter(outfilecsv, fieldnames=header, delimiter='\t')
            outfile_writer.writeheader()
            for line in infile_reader:
                outfile_writer.writerow(line)

    else:
        with open(file, 'r') as infilecsv, open(outfile, 'a') as outfilecsv:
            infile_reader = csv.DictReader(infilecsv, delimiter='\t')
            header = infile_reader.fieldnames
            outfile_writer = csv.DictWriter(outfilecsv, fieldnames=header, delimiter='\t')
            for line in infile_reader:
                outfile_writer.writerow(line)
    return header


def find_duplicates():
    with open(outfile, 'r') as infilecsv, open('rnacat.duplicates.{}.tsv'.format(mmddyy), 'w') as outfilecsv:
        infile_reader = csv.DictReader(infilecsv, delimiter='\t')
        outfile_writer = csv.DictWriter(outfilecsv, fieldnames=file_header, delimiter='\t')
        outfile_writer.writeheader()

        dups = set()
        data_all = []
        data_dups = dict()

        for line in infile_reader:
            # add all lines to data_all
            data_all.append(line)

            # find duplicate lines (duplicate samples in file) with data_dups dict, add to dups set
            if line['Sample'] in data_dups:
                dups.add(line['Sample'])
            data_dups[line['Sample']] = line

        # print out all duplicate samples using data_all and dups
        for line in data_all:
            if line['Sample'] in dups:
                outfile_writer.writerow(line)
    return


for infile in rna_summary_files:
    print(infile)
    file_header = file_cat(infile)

find_duplicates()
