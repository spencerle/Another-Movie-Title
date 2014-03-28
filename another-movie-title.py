from boto.mturk.connection import MTurkConnection
from boto.mturk.question import *
import time
import thread

ACCESS_ID = 'AKIAJFHM2HK3FZZAJLAA'
SECRET_KEY = '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'
HOST = 'mechanicalturk.sandbox.amazonaws.com'
ACTIVEHITSFNAME = 'active_hit.file'
mtc = MTurkConnection(aws_access_key_id = ACCESS_ID,
	              aws_secret_access_key = SECRET_KEY,
	              host = HOST)

def createHIT(request, hit_name):

	title = 'DEVELOPING: What movie is this?'
	description = ('Read the description of the movie below'
		       ' and give an answer as to which movie it is.')
	keywords = 'movie, relation, advice'
	 
	#---------------  BUILD OVERVIEW -------------------
	 
	overview = Overview()
	overview.append_field('Title', 'DEVELOPING: What movie is this?')
	 
	#---------------  BUILD QUESTION 1 -------------------
	 
	qc1 = QuestionContent()
	qc1.append_field('Title','Who is the main character of the little mermaid?')
	 
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
	with open('amt_hit_file', 'a') as fd:
		fd.write(str(hit_id) + ' = ' + hit_name + '\n')
	return hit_id

def getHIT(hit_id):
	assignments = mtc.get_assignments(hit_id)
	if assignments == []:
		print "There are no results at this time"
		
	else:
		for assignment in assignments:
			for question_form_answer in assignment.answers[0]:
				print "%s" % question_form_answer.fields[0]

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

def RequestThread(sRequest, sHITID):
	#----Wait for Responses----#
	TurkResponse = []
	while (len(TurkResponse) < 1):
		TurkResponse = mtc.get_assignments(sHITID)
	TurkerResults = []
	#---Get the Responses----#
	for assignment in TurkResponse:
		SingleTurkResponse = []
		for question_form_answer in assignment.answers[0]:
			for value in question_form_answer.fields:
				SingleTurkResponse.append(value)
		TurkerResults.append(SingleTurkResponse)
	print(TurkerResults)
	##Validate Turker Answers and Accept/Reject
	#---Call Verification Check----#
	VerifiableResponses = []
	for response in TurkerResults:
		VerifiableResponses.append(response[3])
	VerificationResults = Verification(VerifiableResponses, sRequest)
	print(VerificationResults)
	#call IMDB with Results
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
			mtc.reject_assignment(assignment.AssignmentId, "Failed Pre-Screening")	
			
def LoadActiveHits():
	pass
def main():
	HITID = createHIT("TEST", "DUDE")
	print (HITID)
	RequestThread("TEST", HITID)
	AcceptRejectVerified("",HITID)
	#thread.start_new_thread(RequestThread, ("TEST", HITID))
main()#FUCK YOU GIT