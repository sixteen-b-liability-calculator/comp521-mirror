from ftplib import FTP
import tempfile

import re
import gzip

def homepage():
	return ("Whoopsie", 400, [])

# Function in order to retrieve an index from the edgar database
def pull_index_Edgar():
    input_data = request.get_json()
	# TODO(valakuzh) Test the inputs
    try:
        year = input_data.get('year')
        quarter = input_data.get('quarter')
        indexType = input_data.get('indexType')
    except FourhundredException as e:
        return (e.msg, 400, [])

	ftp = FTP('ftp.sec.gov')
	ftp.login()
	directoryPath = 'edgar/'+year+'/QTR'+quarter+'/'+indexType+'.gz'
	ftp.cwd(directoryPath)

	pracFile = tempfile.TemporaryFile()
	ftp.retrbinary('RETR '+ indexType + '.gz', pracFile.write)
	pracFile.seek(0)
	return pracFile

parse_idx_start = re.compile(r'-+$')
parse_idx_entry = re.compile(r''' ( [0-9]  + )    # CIK
                               \|   [^|]   *      # (skip) name
                               \| ( [^|]   + )    # form type
                               \|   [0-9-] +      # (skip) date
                               \| ( edgar/data/[0-9]+/[0-9-]+\.txt ) # path
                               $ ''', re.VERBOSE)

def ungzip_tempfile(fileobj):
    fileobj.seek(0)
    return gzip.GzipFile("", fileobj=fileobj, mode='r')

def parse_idx(fileobj, target_cik, form_types):
    out = []
    found_start = False
    for line in fileobj:
        if found_start: # i.e., we're looking at real entries now
            m = parse_idx_entry.match(line.strip())
            if not m:
                # we expect to be able to parse every line after the start
                raise Exception("could not parse line from EDGAR idx:", line)
            if int(m.group(1)) == target_cik and m.group(2) in form_types:
                out.append(m.group(3))
        elif parse_idx_start.match(line.strip()):
            found_start = True
    if not found_start:
        raise Exception("could not find start line in EDGAR idx")

    return out
