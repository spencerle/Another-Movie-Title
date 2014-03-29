from boto.mturk.connection import MTurkConnection
from boto.mturk.question import *
import time
import thread
import imdb
ACCESS_ID = 'AKIAJZH2OMW6WNOX6H6Q'
SECRET_KEY = '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'
HOST = 'mechanicalturk.sandbox.amazonaws.com'
ACTIVE_HIT = 'active_hit'
COMPLETE_HIT = 'complete_hit'
mtc = MTurkConnection(aws_access_key_id = ACCESS_ID,
	              aws_secret_access_key = SECRET_KEY,
	              host = HOST)
ia = imdb.IMDb() # by default access the web.

def createHIT(request):

	title = 'DEVELOPING: What movie is this?'
	description = ('Read the description of the movie below'
		       ' and give an answer as to which movie it is.')
	keywords = 'movie, relation, advice'
	 
	#---------------  BUILD OVERVIEW -------------------
	 
	overview = Overview()
	overview.append_field('Title', 'DEVELOPING: What movie is this?')
	 
	#---------------  BUILD QUESTION 1 -------------------
	 
	qc1 = QuestionContent()
	qc1.append_field('Title','Who is the main character of The Little Mermaid?')
	 
	fta1 = FreeTextAnswer()
	 
	q1 = Question(identifier='question1',
		      content=qc1,
		      answer_spec=AnswerSpecification(fta1),
		      is_required=True)
	 
	#---------------  BUILD QUESTION 2 -------------------
	 
	qc2 = QuestionContent()
	qc2.append_field('Title','Which movie series features a killer in a hockey mask?')
	 
	fta2 = FreeTextAnswer()
	 
	q2 = Question(identifier='question2',
		      content=qc2,
		      answer_spec=AnswerSpecification(fta2),
		      is_required=True)
	 
	#---------------  BUILD QUESTION 3 -------------------
	 
	qc3 = QuestionContent()
	qc3.append_field('Title',"What is Kane's last word in 'Citizen Kane'?")
	 
	fta3 = FreeTextAnswer()
	 
	q3 = Question(identifier='question3',
		      content=qc3,
		      answer_spec=AnswerSpecification(fta3),
		      is_required=True)
	 
	#---------------  BUILD QUESTION 4 -------------------
	 
	qc4 = QuestionContent()
	qc4.append_field('Title', request)
	 
	fta4 = FreeTextAnswer()
	 
	q4 = Question(identifier="question4",
		      content=qc4,
		      answer_spec=AnswerSpecification(fta4),
		      is_required=True)
	 
	#--------------- BUILD THE QUESTION FORM -------------------
	 
	question_form = QuestionForm()
	question_form.append(overview)
	question_form.append(q1)
	question_form.append(q2)
	question_form.append(q3)
	question_form.append(q4)
	 
	#--------------- CREATE THE HIT -------------------
	
	hit_request = mtc.create_hit(questions=question_form,
					max_assignments=2,
					title=title,
					description=description,
					keywords=keywords,
					duration = 60*5,
					reward=0.05)
	
	#--------------- WRITE THE HIT FILE -------------------

	hit = hit_request[0]
	hit_id = hit.HITId
	with open(ACTIVE_HIT, 'a') as fd:
		fd.write(str(hit_id) + ' = ' + request + '\n')
	return hit_id

def getHIT(hit_id):
	with open(COMPLETE_HIT, 'r') as fd:
		for line in fd:
			if hit_id == line[:30]:
				results = line[33:].strip().split('|')
				print '\nMovie: ' + str(results[1])
				print 'Year: ' + str(results[2])
				print 'Synopsis: ' + str(results[3])

def completeHIT(hit_id, IMDBResults):
	with open(ACTIVE_HIT, 'r') as fd:
		lines = fd.readlines()
	with open(ACTIVE_HIT, 'w') as fd:
		for line in lines:
			id = line[:30]
			if id != str(hit_id):
				fd.write(line)
			else:
				with open(COMPLETE_HIT, 'a') as fd_complete:
					line = line[:-1] 
					for result in IMDBResults[0]:
						line += ' | ' + str(result)
					fd_complete.write(line)

def outputResults(AMTResults):
	movieInfo = []
	for movie in AMTResults:
		searchResults = ia.search_movie(movie)
		if searchResults:
			mainResult = searchResults[0]
			ia.update(mainResult)
			#print "%s (%s)" %(mainResult['canonical title'], mainResult['year'])
			#print mainResult['plot outline']
			movieInfo.append([mainResult['canonical title'], mainResult['year'], mainResult['plot outline']])
		else: 
			#print "Turkers' suggestion not found on IMDB!"
			#print "Raw suggestion: " + movie
			movieInfo.append([movie, "(No year)", "(No outline)"])
	return movieInfo

	

def Verification(sTurkerResp, sRequest):
	hit_ids = []
	for i in range (0,len(sTurkerResp)):
		#-----Build HITs----#
		title = "DEVELOPING: Test5"
		description = "Is the described scene from this movie?"
		keywords = 'movie, relation, advice'
		overview = Overview()
		overview.append_field("Title", title)
		questionCon = QuestionContent()
		questionCon.append_field("Title", "Is this scene: \""+sRequest+ "\" from the movie \"" + sTurkerResp[i]+"\"?")
		cBox = SelectionAnswer(1, 2, 'radiobutton', ('YY','NN'))
		q1 = Question(identifier='main',
			        content=questionCon,
			        answer_spec=AnswerSpecification(cBox),
			        is_required=True)
		question_form = QuestionForm()
		question_form.append(overview)
		question_form.append(q1)
		hit_request = mtc.create_hit(questions=question_form,
			                                max_assignments=1,
			                                title=title,
			                                description=description,
			                                keywords=keywords,
			                                duration = 60*5,
			                                reward=0.01)
							
		hit = hit_request[0]
		hit_ids.append(hit.HITId)
	#----Loop Until Get Result----#
	responses = []
	assignments = []
	while len(hit_ids) > 0: #As long as a single HIT hasn't been completed, keep waiting
		for hit_id in hit_ids:
			#----Go through each HIT ans check to see if it's been completed or not----#
			assignments = mtc.get_assignments(hit_id)
			#----If the HIT has been completed, add the response----#
			if (len(assignments) > 0):
				for assignment in assignments:
					for question_form_answer in assignment.answers[0]:
						for value in question_form_answer.fields:
							responses+=value
					mtc.approve_assignment(assignment.AssignmentId)
				hit_ids.remove(hit_id)
		time.sleep(.005) #Sleep to prevent us from monopolizing the CPU
	#Throw out any that are marked as wrong	
	correct = []
	for i in range(0, len(responses)):
		if (responses[i] == (u"Y")):
			correct.append(sTurkerResp[i])
	return correct

def Prescreen(sHITID):
	assignlist = mtc.get_assignments(sHITID)
	returnlist = []
	for assignment in assignlist:
		answerOne = assignment.answers[0][0].fields[0]
		answerTwo = assignment.answers[0][1].fields[0]
		answerTwo = answerTwo[:6]
		answerThree = assignment.answers[0][2].fields[0]
		if (answerOne.lower() == "ariel") and (answerTwo.lower() == "friday") and (answerThree.lower() == "rosebud"):
			returnlist.append(assignment.answers[0][3].fields[0])
		else:
			try:
				mtc.reject_assignment(assignment.AssignmentId, "Failed Pre-Screening")
			except:
				pass
	return returnlist

def RequestThread(sRequest, sHITID):
	#----Wait for Responses----#
	TurkResponse = []
	while (len(TurkResponse) < 1):
		TurkResponse = mtc.get_assignments(sHITID)
	#---Throw out any that fail trivia check---#
	VerifiableResponses = Prescreen(sHITID)
	#---Call Verification Check----#
	VerificationResults = Verification(VerifiableResponses, sRequest)
	#Get the Final Results list
	FinalResults = AcceptRejectVerified(VerificationResults,sHITID)
	if (len(FinalResults) == 0):
		print("No results found for HIT: "+sHITID)
		return
	#call IMDB with Results
	IMDBResults = outputResults(FinalResults)
	completeHIT(sHITID, IMDBResults)
	return
	
def AcceptRejectVerified(VerifiedResults, sHITID):
	#----Get All Assignments from this HIT
	assignlist = mtc.get_assignments(sHITID)
	returnResults = []
	for assignment in assignlist:
		value = assignment.answers[0][3].fields[0]
		Found = False
		for Result in VerifiedResults:
			if Result.lower() == value.lower():
				Found = True
				try:
					mtc.approve_assignment(assignment.AssignmentId)
				except:
					pass
				returnResults.append(value)
		if not Found:
			try:
				mtc.reject_assignment(assignment.AssignmentId, "Failed Pre-Screening")
			except:
				pass
	return returnResults

def LoadActiveHits(sHITIDS, sRequests):
	if (len(sHITIDS) != len(sRequests)):
		#THE HELL IS GOING ON, WE'RE FUBARED!!!!!!!!
		return
	for i in range(0, len(sHITIDS)):
		thread.start_new_thread(RequestThread, (sRequests[i], sHITIDS[i]))
	print("All active HITs loaded and Threads started")	
	return

def main():
	hit_ids = []
	labels = []	
	with open(ACTIVE_HIT, 'r') as fd:
		for line in fd:
			key = line[:30]
			label = line[33:]
			hit_ids.append(key)
			labels.append(label)
	LoadActiveHits(hit_ids, labels)
	
	print "\n---Welcome to Turkleton's Another Movie Title!---"
		
	while True:
		selection = 0
		bad_input = True
		print "\n\nWhat would you like to do?"
		print "\n1.) Make a request\n2.) Check request status\n3.) View results"
		while bad_input:
			try:
				selection = int(input('\nEnter the number of your selection: '))
				bad_input = False
			except:
				print "The input needs to be an integer. Please try again"
		
		#--------------- CREATE A HIT -------------------
		if selection == 1:
			print "\n\nPlease enter a description of the movie you are thinking of. The more details you can provide, the more accurate our results will be."
			movie_description = raw_input('Description: ')
			hitid = createHIT(movie_description)
			thread.start_new_thread(RequestThread,(movie_description,hitid))
		
		#--------------- CHECK STATUS -------------------
		if selection == 2:
			hits = []
			try:		
				with open(ACTIVE_HIT, 'r') as fd:
					for line in fd:
						key = line[:30]
						label = line[33:]
						hits.append((key,label))
						
					#--------------- CHECK FOR EMPTY FILE -------------------
					if hits == []:
						raise Error()
						
					#--------------- PRINT HIT OPTIONS -------------------
					counter = 1
					for hit in hits:
						print (str(counter) + '.) ' + hit[1]),
						counter+=1
			except:
					print ("No HITS found. Please create a HIT or View Results.")
					
		#--------------- VIEW RESULTS -------------------
		if selection == 3:
			hits = []
			try:
				#--------------- PULL CURRENT HITS -------------------
				with open(COMPLETE_HIT, 'r') as fd:
					for line in fd:
						key = line[:30]
						label = line[33:]
						hits.append((key,label))
						
					#--------------- CHECK FOR EMPTY FILE -------------------
					if hits == []:
						raise Error()
						
					#--------------- PRINT HIT OPTIONS -------------------
					counter = 1
					for hit in hits:
						results = hit[1].strip().split('|')
						print (str(counter) + '.) ' + results[0]),
						counter+=1
					
					#--------------- Retrieve user input -------------------
					bad_input = True
					while bad_input:
						try:
							selection = int(input('\nEnter the number of your selection: '))
							bad_input = False
						except:
							print "The input needs to be an integer. Please try again"
													
					getHIT(hits[selection-1][0])					
							
			except:
				print ("No HITS complete at this time.")
