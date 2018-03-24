import nltk

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

test_imperative = [
#All records
"show timesheet",
"show records from timesheet",
"show 10 records from timesheet",

#Single Where
"tell me timesheet records for employee andy",
"find records for employee andy from timesheet",
"show me records from timesheet for date d1",
"return records from d1 from timesheet",

#Multi Where w/o dates
"show me timesheet records of project soli for employee andy",
"find records of employee andy for project soli from timesheet",
"return records of employee andy from timesheet for project soli",
"return top 10 records of employee andy from timesheet for project soli",


#Multi Where w/ dates
"show me timesheet records for project soli before d1",
"show me timesheet records for project soli for employee andy after d1",
"show me timesheet records for project soli from d1 to d2",
"show me timesheet records for project soli for employee andy from d1 to d2",
"show records from timesheet for project soli from d1",
"show records from timesheet for project soli from d1 to d2",
"show records from timesheet for project soli for employee andy from d1 to d2",
"show records for project soli from timesheet from d1",
"show records for project soli from timesheet from d1 to d2",
"show records for project soli from d1 from timesheet to d2",
"show records for project soli from d1 to d2 from timesheet",
"show records for project soli for employee andy from timesheet from d1 to d2",
"show records from d1 to d2 for project soli from timesheet",
"show records from d1 to d2 from timesheet for project soli",
"show 10 records for project soli for employee andy from timesheet from d1 to d2",


#Multiple Selection
"show employee id employee name from timesheet for project soli",
"show employee name project name company for project soli from timesheet for employee andy",

#Aggregation w/o groupby
"show min employee id for project soli from timesheet",
"show average employee id from timesheet for project soli",
"show maximum employee id for project soli from timesheet for employee andy",
"show maximum employee id minimum employee id average employee id for project soli from timesheet for employee andy from d1 to d2",
"show maximum employee id minimum employee id average employee id for project soli for employee andy from d1 from timesheet to d2",
"show total number of employee from timesheet",
"show total of work hours from timesheet for employee andy",
"show unique employee from timesheet for project soli",

#Aggregation w/ groupby
"show avg work hours for each employee from timesheet",
"show min work hours of project soli for every employee from timesheet",
"show count of employee of project soli from date d1 from timesheet for each and every company",
"show 10 entries of count of employee of project soli from date d1 from timesheet for each and every company",

#order by
"show employee id in decreasing order of work hours from timesheet",
"show top 10 records of min work hours of project soli for every employee in increasing order of work hours from timesheet",
"show min work hours of project soli for every employee in increasing order of work hours from timesheet",
"show records for project soli for employee andy in increasing order of work hours from timesheet from d1 to d2",
"show top 10 records for project soli for employee andy in increasing order of work hours from timesheet from d1 to d2"

]

grammar = nltk.grammar.FeatureGrammar.fromstring(open('grammar').read())

print bcolors.HEADER + "Number of test cases : " + str(len(test_imperative)) + bcolors.ENDC
print bcolors.HEADER + "Calculating parse trees" + bcolors.ENDC

f = open('testreults.txt' , 'w')
fol = nltk.sem.interpret_sents(test_imperative, grammar)
for idx, i in enumerate(fol):
	if not len(i):
		print bcolors.FAIL + 'FAILED : ', test_imperative[idx] + bcolors.ENDC
	if len(i):
		print bcolors.OKGREEN + 'PASSED : ', test_imperative[idx] + bcolors.ENDC
		f.writelines('PASSED : ' + test_imperative[idx] + '\n')
		f.writelines([u'\t' + unicode(parse_tree[1]) + u'\n' for parse_tree in i])
		f.writelines(u'\n')
		