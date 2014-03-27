import imdb
ia = imdb.IMDb() # by default access the web.

AMTResults = [("lions",["lion king"]),("ford",["the fugitive","air force one"])]
AMTResultsFlag = 0

while AMTResultsFlag:
	pass
	
AMTResultsFlag = 1
for i in AMTResults:
	if AMTResults[0] != 'NULL': 
			print "Results for %s:" % i[0]
			for j in i[1]:
				searchResults = ia.search_movie(j)
				mainResult = searchResults[0]
				ia.update(mainResult)
				print "%s (%s)" %(mainResult['canonical title'], mainResult['year'])
				print mainResult['plot outline']
	else:
		print "Sorry! Turkers could not identify your request for %s." % i[0]
AMTResultsFlag = 0