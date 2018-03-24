import os
import re
import nltk
import dateparser

class NLP2SQL(object):

	def __init__(self, __file__='grammar'):
		self.path_to_grammar = os.path.abspath(__file__)
		

	@staticmethod
	def traverse_parsed_tree(tree, queue):
		'''
		Traverses @tree to generate the tokens which is used to 
		create @queue, which is further used to generate SQL query.

		Parameters:
		@tree  : type - nltk.tree.ParentedTree
			 	 Contains the tree representation of the FOL statement.
		@queue : type - list
				 List of the tokens extracted from the FOL parsed tree.
		'''
		try:
			tree.label()
		except AttributeError:
			return
		except Exception as e:
	   		print e
			return
		else:
			if tree.height() == 2:  
				if tree.label() == 'PREDICATENAME':
					queue.append(tree.leaves()[0])
				elif tree.label() == 'VARIABLENAME':
					queue.append(tree.leaves()[0])
				else:
					queue.append(tree.label())
				return
			for child in tree:
				NLP2SQL.traverse_parsed_tree(child, queue)

	def create_queue(self, tree):
		'''
		Creates a @queue type - list of the tokens extracted from the FOL parsed tree
		which is be used to create SQL query.
		@queue is created by recursively traversing the FOL parse tree.
		ParentedTree is used because it automatically maintains parent pointers for
    	single-parented trees(see NLTK docs, for more information).

		Parameters:
		@tree : type - str
					Contains a str representation of the FOL parsed tree.

		'''
		parented_tree = nltk.tree.ParentedTree.fromstring(tree)
		queue = []
		NLP2SQL.traverse_parsed_tree(parented_tree, queue)
		self.create_query(queue)

	def create_query(self, queue):
		'''
		Creates the SQL query from token queue extracted from tree traversing. 
		@mappers type - {} is a mapping between tokens and SQL keywords.
		@predicates type - [] contains the global predicate list. 

		Everything before '->' will be considered as a part of the SELECT
		clause, and everything after will be a part of the WHERE clause.

		Parameters:
		@queue : type - list
				 Contains the list of tokens extracted from traversing the parse tree of FOL.
		
		Returning Value(s):
		@sql_query : type - str
					 Contains the SQL query for the input.

		TODO:	1) Improve mappers.
				2) Change(and add) better way to map FOL parsed tokens to SQL keywords.

		'''
		table_column_mapper = {'timesheet' : ['company_name_column','date_column','project_name_column','employee_name_column','employee_id_column','work_hour_column']} 
		sql_keywords = ['orderby', 'groupby', 'LIMIT', 'MIN', 'MAX', 'AVG', 'COUNT', 'DISTINCT', 'SUM']
		conditional_operator_mapper = {'lesser' : '<', 'greater' : '>', 'equals' : '='}
		table_clause = []
		select_clause = []
		where_clause = []
		orderby_clause = ''
		groupby_clause = ''
		limit_clause = ''
		token = None
		
		queue.pop(0)

		# Select clause 
		while token != 'IMPLIES':
			if len(queue) != 0:
				token = queue.pop(0)
				if token in table_column_mapper.keys():
					table_clause.append(token)
				elif token in sql_keywords:
					agg_column = queue.pop(0)
					for k, v in table_column_mapper.iteritems():
						if agg_column in v:
							agg_column = k + '.' + agg_column
							break
					select_clause.append(token+'('+agg_column+')')
				else:
					agg_column = token
					for k, v in table_column_mapper.iteritems():
						if agg_column in v:
							agg_column = k + '.' + agg_column
							select_clause.append(token)	
							break
			else:
				break			

		if not len(select_clause):
			select_clause.append('*')
		
		# Where, OrderBy and GroupBy Clause
		while len(queue):
			date_flag = 0
			present_flag = 0
			token = queue.pop(0)
			if token == 'date_column':
				date_flag = 1
			if token not in sql_keywords:
				for k, v in table_column_mapper.iteritems():
					if token in v:
						token = k + '.' + token
						present_flag = 1
						break
				if not present_flag:
					continue
				if date_flag:
					queue.pop(0)
					op = conditional_operator_mapper[queue.pop(0)]
					queue.pop(0)
					value = queue.pop(0)
					where_clause.append(token + ' ' + op + ' ' + value)
				else:
					queue.pop(0)
					value = queue.pop(0)
					where_clause.append(token + ' = ' + value)
			else:
				if token == 'groupby':
					value = queue.pop(0)
					for k, v in table_column_mapper.iteritems():
						if value in v:
							value = k + '.' + value
							break
					select_clause.append(value)
					groupby_clause = ' GROUP BY ' + value
				elif token == 'orderby':
					op = queue.pop(0)
					queue.pop(0)
					value = queue.pop(0)
					for k, v in table_column_mapper.iteritems():
						if value in v:
							value = k + '.' + value
							break
					orderby_clause = ' ORDER BY ' + value + ' ' + op
				elif token == 'LIMIT':
					limit_clause = ' LIMIT ' + queue.pop(0).replace('\'','')

		if len(where_clause):
			sql_query = 'SELECT ' + ','.join(select_clause) + ' FROM ' + ','.join(table_clause) + ' WHERE ' + ' AND '.join(where_clause) + orderby_clause + groupby_clause + limit_clause + ';'
		else:
			sql_query = 'SELECT ' + ','.join(select_clause) + ' FROM ' + ','.join(table_clause) + orderby_clause + groupby_clause + limit_clause + ';'

		for k, v in self.date_mapper.iteritems():
			sql_query = sql_query.replace(k, v)
		print 'SQL - ' + sql_query

	def convert_to_fol(self, sentences, additional_rules=None, draw=False):
		'''
		Converts Natual Language input to First Order Logic according to the 
		grammar rules defined. @fol_tree contains the FOL representation as well 
		as the parsed tree.

		Parameters:
		@sentences : type - list
					Contains the list of sentences that will be parsed.
		@draw     : type - boolean
					If True, a pop-up with the Parsed tree will be opened. 
					Code will wait until the pop-up is closed! 
		
		Returning Value(s):
		@fol_representation :	type - unicode
								Contains the fol representation of the input.

		Note: This is just a toy example with very limited grammar(possibly wrong too!)

		TODO:	1) Improve grammar.

		'''
		grammar = open(self.path_to_grammar, 'r').read()
		if additional_rules:
			grammar = grammar + '\n' + '\n'.join(additional_rules)
		grammar = nltk.grammar.FeatureGrammar.fromstring(grammar)
		fol_tree = nltk.sem.interpret_sents(sentences, grammar)
		if draw:
			#pass
			# WILL ADD DRAWING FUNCTIONALITY LATER
			fol_tree[0][0][0].draw()
		return fol_tree[0]

	def get_valid_tree(self, fol_tree):
		
		for tree in fol_tree:
			if len(re.findall('([a-z_A-Z]+\([^\)]*\)(\.[^\)]*\))?)', tree[1].unicode_repr())) == 1:
				return tree[1].unicode_repr().replace('.','.(').replace('>',')>')
			elif u'\\' in tree[1].unicode_repr() or u'?' in tree[1].unicode_repr() or u'all x.(' not in tree[1].unicode_repr():
				continue
			else:
				return tree[1].unicode_repr()
				break
		return None

	def parse_fol_representation(self, fol_representation, draw=False):
		'''
		Parses First Order Logic representation according to the 
		grammar rules defined using NLTK's Chart Parser. The grammar defined has some 
		lexicons that are assigned dynamically during Run-Time(Might be a bad thing!). 
		In case of ambiguous parse trees, the code returns only the first one(No logic 
		is applied to select any one).

		Parameters:
		@fol_representation : type - unicode
					Contains the unicode fol representation that will be parsed.
		@draw     : type - boolean
					If True, a pop-up with the Parsed tree will be opened. 
					Code will wait until the pop-up is closed! 
		
		Returning Value(s):
		@parsed_fol : type - nltk.tree.Tree object
					  Parsed tree of the FOL input.

		Note: This is just a toy example with very limited grammar(possibly wrong too!)

		TODO:	1) Make grammar completely static.
				2) Read grammar from file.
		'''
		
		fol_representation = fol_representation[:-1]
		fol_representation = fol_representation.split()[1:]
		fol_representation = ' '.join(fol_representation)
		predicate_names = []
		variables = []
		predicates = re.findall('([a-z_A-Z]+\([^\)]*\)(\.[^\)]*\))?)', fol_representation)
		for i in predicates:
			predicate_names.append(re.findall('.+?(?=\()', i[0])[0])
			variables.append(re.findall('(?<=\()(.+?)(?=\))', i[0])[0])
		selection_part = fol_representation.split('->')[0].split('&')
		selection_part = [i.replace(')','').replace(' ','') for i in selection_part]
		if len(selection_part) > 0:
			variables += selection_part[1:]
		variables = ','.join(variables)
		variables = ' | '.join(set(map(lambda x: '"' + x + '"',variables.split(','))))
		predicate_names = ' | '.join(set(map(lambda x: '"' + x + '"', predicate_names)))
		grammar = nltk.CFG.fromstring(r"""
			% start S
			# Grammar Rules
			S -> ALLQUANT  OPENBRACE BODY CLOSEBRACE | ALLQUANT PREDICATE
			BODY -> HEAD IMPLIES COMPOUND | HEAD
			HEAD -> COMPOUND
			COMPOUND -> SIMPLE | SIMPLE AND COMPOUND | OPENBRACE COMPOUND CLOSEBRACE
			SIMPLE -> PREDICATE | VARIABLENAME
			PREDICATE -> PREDICATENAME OPENBRACE VARIABLE CLOSEBRACE
			VARIABLE -> VARIABLENAME | VARIABLENAME COMMA VARIABLE

			# Lexicon Rules
			OPENBRACE -> "("
			CLOSEBRACE -> ")"
			AND -> "&"
			IMPLIES -> "->"
			ALLQUANT -> "all" "x." 
			COMMA -> ","
			PREDICATENAME -> """ + predicate_names + """
			VARIABLENAME -> """ + variables
		)
		fol_representation = map(str, fol_representation.replace('(',' ( ').replace(')', ' ) ').replace(',',' , ').split())
		chart_parser = nltk.ChartParser(grammar)
		print 'FOL REPRESENTATION  - ' + ' '.join(fol_representation)
		parsed_fol = chart_parser.parse(fol_representation)
		parsed_fol = parsed_fol.next()
		if draw:
			parsed_fol.draw()
		return parsed_fol

	def find_following_NT(self, parent, productions, followups):
		'''
		'''
		for production in productions:
			if not all(map(lambda x: isinstance(x, unicode), production._rhs)):
				flag = 0
				for i, nt in enumerate(production._rhs):
					if flag:
						followups.add(nt)
						flag = 0
						continue
					if nt == parent and len(production._rhs) - 1 > i:
						flag = 1
					elif nt == parent and len(production._rhs) - 1 <= i:
						parent = production._lhs
						self.find_following_NT(parent, productions, followups)
		return followups

	def autosuggestion_by_words(self, draw_nl=False, draw_fol=False):
		'''
		'''
		grammar = nltk.grammar.FeatureGrammar.fromstring(open(self.path_to_grammar, 'r').read())
		productions = grammar.productions()
		key = nltk.featstruct.Feature('type')
		productions_wofeat = productions
		for production in productions_wofeat:
			if not all(map(lambda x: isinstance(x, unicode), production._rhs)):
				production._lhs = nltk.grammar.Nonterminal(production._lhs[key])
				temp = []
				for i in production._rhs:
					# For productions involving Terminal and Non Terminal
					if not isinstance(i, unicode):
						temp.append(nltk.grammar.Nonterminal(i[key]))
				production._rhs = temp
			else:
				production._lhs = nltk.grammar.Nonterminal(production._lhs[key])
		additional_rules = []
		grammar = nltk.grammar.FeatureGrammar.fromstring('\n'.join(['% start S'] + map(lambda x: x.unicode_repr() ,productions_wofeat)))
		_lexical_index = grammar._lexical_index
		input_query = []
		self.date_mapper = {}
		date_count = 0
		input_query_token = raw_input().strip()
		#print '\n'.join(map(lambda x: x.unicode_repr(),grammar.productions()))
		while input_query_token != '':
			try:				
				followups = set()
				suggestions = set()
				propn_flag = 0
				if input_query_token not in _lexical_index.keys():
					propn_flag = 1
					try:
						val = int(input_query_token)
						additional_rules.append("PropN[TYPE=number, SEM=<\P.P('" + input_query_token + "')>] -> '" + input_query_token + "'")
					except:
						date = dateparser.parse(input_query_token)
						if date:
							date_alias = 'd'+str(date_count)
							self.date_mapper[date_alias] = date.strftime("%d-%m-%Y")
							additional_rules.append("PropN[TYPE=date, SEM=<\P.P('" + date_alias + "')>] -> '" + "' '".join(input_query_token.split()) + "'")
							date_count += 1
						else:
							if re.match(r"[^@]+@[^@]+\.[^@]+", input_query_token):
								additional_rules.append("PropN[TYPE=email, SEM=<\P.P('" + input_query_token + "')>] -> '" + input_query_token + "'")
							else:
								additional_rules.append("PropN[TYPE=variable, SEM=<\P.P('" + input_query_token + "')>] -> '" + input_query_token + "'")
				
				if not propn_flag:
					input_production = next(iter(_lexical_index[input_query_token]))
					input_featparent = input_production._lhs
					input_parent = nltk.grammar.FeatStructNonterminal(input_featparent[key] + u'[]')
				else:
					input_parent = nltk.grammar.FeatStructNonterminal(u'PropN[]')
				print input_parent
				followups = self.find_following_NT(input_parent, grammar.productions(), followups)
				#print followups
				for following_nt in followups:
					for suggestion in grammar._leftcorner_words[following_nt]:
						suggestions.add(suggestion)
				print suggestions

				input_query.append(input_query_token)
			except KeyError:
				print "Token not a valid lexicon"
			input_query_token = raw_input().strip()

		#input_query = ' '.join(input_query)
		natural_language = []
		natural_language.append(input_query)
		if not len(additional_rules):
			additional_rules = None
		self.convert_to_sql(natural_language, additional_rules, draw_nl, draw_fol)

	def convert_to_sql(self, natural_language, additional_rules=None, draw_nl=False, draw_fol=False):
		'''
		'''
		print natural_language
		fol_tree = self.convert_to_fol(natural_language, additional_rules, draw_nl)
		fol_representation = self.get_valid_tree(fol_tree)
		parsed_fol = self.parse_fol_representation(fol_representation, draw_fol)
		self.create_queue(parsed_fol.__str__().replace('\n',''))

	def driver(self):
		#natural_language = ['show top 10 records for project soli for employee andy in increasing order of work hours from timesheet from d1 to d2']
		#natural_language = ["show maximum employee id minimum employee id average employee id for project soli for employee andy from d1 from timesheet to d2"]
		#natural_language = ["show count of employee minimum work hours of project soli from date d1 from timesheet for each and every company"]
		natural_language = ["show total number of employee from timesheet"]
		print natural_language[0]
		fol_tree = self.convert_to_fol(natural_language)#, True)
		fol_representation = self.get_valid_tree(fol_tree)
		parsed_fol = self.parse_fol_representation(fol_representation)#, True)
		self.create_queue(parsed_fol.__str__().replace('\n',''))

obj = NLP2SQL()
#obj.driver()
obj.autosuggestion_by_words()