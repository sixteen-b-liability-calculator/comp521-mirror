from ftplib import FTP
import tempfile

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