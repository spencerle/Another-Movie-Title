from boto.mturk.connection import MTurkConnection
from boto.mturk.question import *
import time
import thread
import imdb
ACCESS_ID = 'AKIAJFHM2HK3FZZAJLAA'
SECRET_KEY = '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'
HOST = 'mechanicalturk.sandbox.amazonaws.com'
ACTIVE_HIT = 'active_hit'
COMPLETE_HIT = 'complete_hit'
AMTResults = []
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
	assignments = mtc.get_assignments(hit_id)
	if assignments == []:
		print "There are no results at this time"
	else:
		for assignment in assignments:
			for question_form_answer in assignment.answers[0]:
				print "%s" % question_form_answer.fields[0]

def completeHIT(hit_id):
	with open(ACTIVE_HIT, 'r') as fd:
		lines = fd.readlines()
	with open(ACTIVE_HIT, 'w') as fd:
		for line in lines:
			id = line[:30]
			if id != str(hit_id):
				fd.write(line)
			else:
				with open(COMPLETE_HIT, 'a') as fd_complete:
					fd_complete.write(line)

def outputResults(AMTResults, hit_id):
	'''assignments = mtc.get_assignments(hit_id)
	if assignments == []:
		print "There are no results at this time"
	else:
		for assignment in assignments:
			for question_form_answer in assignment.answers[0]:
				AMTResults.append(str(question_form_answer.fields[0]))

	print AMTResults	
	'''
	for i in AMTResults:
		#if AMTResults[0] != 'NULL': 
			print "Results for %s:" % i[0]
			for j in i[1]:
				searchResults = ia.search_movie(j)
				if searchResults:
					mainResult = searchResults[0]
					ia.update(mainResult)
					print "%s (%s)" %(mainResult['canonical title'], mainResult['year'])
					print mainResult['plot outline']
				else: 
					print "Turkers' suggestion not found on IMDB!"
					print "Raw suggestion: " + j
		#else:
		#	print "Sorry! Turkers could not identify your request for %s." % i[0]
	

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
	while len(hit_ids) > 0:
		for hit_id in hit_ids:
			assignments = mtc.get_assignments(hit_id)
			if (len(assignments) > 0):
				for assignment in assignments:
					for question_form_answer in assignment.answers[0]:
						for value in question_form_answer.fields:
							responses+=value
				hit_ids.remove(hit_id)
		time.sleep(.005)
	correct = []
	for i in range(0, len(responses)):
		if (responses[i] == (u"Y")):
			correct.append(sTurkerResp[i])
	AMTResults = []
	AMTResults.append((sRequest, correct))
	return AMTResults

def Prescreen(sHITID):
	assignlist = mtc.get_assignments(sHITID)
	returnlist = []
	for assignment in assignlist:
		answerOne = assignment.answers[0][0].fields
		answerTwo = assignment.answers[0][1].fields
		answerTwo = answerTwo[:5]
		answerThree = assignment.answers[0][2].fields
		if (answerOne.lower() == "ariel") and (answerTwo.lower() == "friday") and (answerThree.lower() == "rosebud"):
			returnlist.append(assignment.answers[0][3])
		mtc.reject_assignment(assignment.AssignmentId, "Failed Pre-Screening")
	return returnlist

def RequestThread(sRequest, sHITID):
	#----Wait for Responses----#
	TurkResponse = []
	while (len(TurkResponse) < 1):
		TurkResponse = mtc.get_assignments(sHITID)
	TurkerResults = []
	#---Get the Responses----#
	#for assignment in TurkResponse:
	#	SingleTurkResponse = []
	#	for question_form_answer in assignment.answers[0]:
	#		for value in question_form_answer.fields:
	#			SingleTurkResponse.append(value)
	#	TurkerResults.append(SingleTurkResponse)
	#print(TurkerResults)
	VerifiableResponses = Prescreen(sHITID)
	#---Call Verification Check----#
	VerificationResults = Verification(VerifiableResponses, sRequest)
	#print(VerificationResults)
	outputResults(TupleFinalResults, sHITID)
	return
	
def AcceptRejectVerified(VerifiedResults, sHITID):
	#----Get All Assignments from this HIT
	assignlist = mtc.get_assignments(sHITID)
	for assignment in assignlist:
		value = assignment.answers[0][3]
		Found = False
		for Result in VerifiedResults:
			if Result.lower() == value.lower():
				Found = True
				mtc.approve_assignment(assignment.AssignmentId)
		if not Found:
			mtc.reject_assignment(assignment.AssignmentId, "Failed Verification")	
			
def LoadActiveHits():
	pass

def main():
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
			createHIT(movie_description)
		
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
					
					#--------------- Retrieve user input -------------------
					bad_input = True
					while bad_input:
						try:
							selection = int(input('\nEnter the number of your selection: '))
							bad_input = False
						except:
							print "The input needs to be an integer. Please try again"
						
					#--------------- REFINE THIS PART -------------------							
					completeHIT(hits[selection-1][0])
					#--------------- REFINE THIS PART -------------------
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
						print (str(counter) + '.) ' + hit[1]),
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
