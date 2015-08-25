# Run from GAE remote API:
# 	{GAE Path}\remote_api_shell.py -s {YourAPPName}.appspot.com
# 	import export_as_csv

import csv
import time

from db_model import UserFeedback

def exportToCsv(query, csvFileName, delimiter):
	with open(csvFileName, 'wb') as csvFile:
		csvWriter = csv.writer(csvFile, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
		writeHeader(csvWriter)

		rowsPerQuery = 1000
		totalRowsSaved = 0
		cursor = None
		areMoreRows = True

		while areMoreRows:
			if cursor is not None:
				query.with_cursor(cursor)
			items = query.fetch(rowsPerQuery)
			cursor = query.cursor()

			currentRows =0
			for item in items:
				saveItem(csvWriter, item)
				currentRows += 1

			totalRowsSaved += currentRows
			areMoreRows = currentRows >= rowsPerQuery
			print 'Saved ' + str(totalRowsSaved) + ' rows'

		print 'Finished saving all rows.'

def writeHeader(csvWriter):
	csvWriter.writerow([
            'datetime',
            'origin',
            'photo_id',
            'feedback',
            'user_ip',
            'cookie',
            'user_agent',
            'location',
            ]) #Output csv header

def saveItem(csvWriter, item):
	# csvWriter.writerow([item.property1, item.property2, item.property3]) # Save items in preferred format
	csvWriter.writerow([
            item.datetime,
            item.origin,
            item.photo_id,
            item.feedback.encode('utf-8'),
            item.user_ip,
            item.cookie,
            item.user_agent,
            item.location,
        ]) #Output csv header


query = UserFeedback.gql("ORDER BY datetime") #Query for items
exportToCsv(query, 'user-feedback.csv', ',')
archive_file = 'user-feedback.%s.csv' % time.strftime('%Y-%m-%dT%H-%M-%S')
open(archive_file, 'w').write(open('user-feedback.csv').read())
