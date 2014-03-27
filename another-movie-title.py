from boto.mturk.connection import MTurkConnection
from boto.mturk.question import *


ACCESS_ID = '<enter access id here>'
SECRET_KEY = '<enter secret key here>'
HOST = 'mechanicalturk.sandbox.amazonaws.com'

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
					max_assignments=5,
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

def getHIT(hit_id):
	assignments = mtc.get_assignments(hit_id)
	if assignments == []:
		print "There are no results at this time"
		
	else:
		for assignment in assignments:
			for question_form_answer in assignment.answers[0]:
				print "%s" % question_form_answer.fields[0]

def main():
	counter = 1
	print "Which HIT do you want to see?"
	hits = []
	
	#--------------- PULL CURRENT HITS -------------------
	with open('amt_hit_file', 'r') as fd:
		for line in fd:
			key = line[:30]
			label = line[33:]
			hits.append((key,label))
	
	#--------------- PRINT HIT OPTIONS -------------------
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
