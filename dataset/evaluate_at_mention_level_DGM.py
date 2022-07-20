import glob
import codecs
import re
import sys
from nltk.metrics.distance import edit_distance

path_sep = "\\" #For Windows
#path_sep = "/" #For Linux
print 'Gold annotations folder : ' + sys.argv[1]
print 'Predicted relations folder : ' + sys.argv[2]
print 'Results file :' + sys.argv[3]

brackets_pattern = re.compile(r'-lrb- [^\r\n]+ -rrb-',re.IGNORECASE)
rb_pattern = re.compile(r'\-[lr][rs]b\-',re.IGNORECASE)

folder1 = sys.argv[1]
folder2 = sys.argv[2]
if(not(folder1.endswith(path_sep))):
	folder1 = folder1 + path_sep
if(not(folder2.endswith(path_sep))):
	folder2 = folder2 + path_sep

#relations = ['Interact','NULL']
relations = ['Rel','NULL']


filesList = glob.glob(folder1+"*.txt")
print len(filesList)

def compute_similarity(s1, s2):
	s11 = brackets_pattern.sub('',s1).strip()
	if(s11 == ''):
		s11 = rb_pattern.sub('',s1).strip()
	s22 = brackets_pattern.sub('',s2).strip()
	if(s22 == ''):
		s22 = rb_pattern.sub('',s2).strip()
		
	s11 = rb_pattern.sub('',s11).strip()
	s22 = rb_pattern.sub('',s22).strip()

	ed = edit_distance(s11, s22)
	sim1 = 1.0 - (float(ed)/float(max(len(s11),len(s22))))
	
	ed = edit_distance(s1, s2)
	sim2 = 1.0 - (float(ed)/float(max(len(s1),len(s2))))
	
	ed = edit_distance(s11, s2)
	sim3 = 1.0 - (float(ed)/float(max(len(s11),len(s2))))
	
	ed = edit_distance(s1, s22)
	sim4 = 1.0 - (float(ed)/float(max(len(s1),len(s22))))
	
	sim = max(sim1,sim2,sim3,sim4)
	return(sim)
	
"""def compute_similarity(s1, s2):
	s11 = brackets_pattern.sub('',s1).strip()
	if(s11 == ''):
		s11 = rb_pattern.sub('',s1).strip()
	s22 = brackets_pattern.sub('',s2).strip()
	if(s22 == ''):
		s22 = rb_pattern.sub('',s2).strip()
		
	s11 = rb_pattern.sub('',s11).strip()
	s22 = rb_pattern.sub('',s22).strip()
	#print s1 + '\t' + s2
	ed = edit_distance(s11, s22)
	#print ed
	sim = 1.0 - (float(ed)/float(max(len(s11),len(s22))))
	#print sim
	return(sim)"""

def pre_process_value(val):
	val = val.replace('(',' ( ')
	val = val.replace(')',' ) ')
	val = re.sub(r'[ ]+',' ',val)
	val = val.replace('(','-lrb-')
	val = val.replace(')','-rrb-')
	return(val.strip())

def get_entities(filePath):
	entity_to_instances = {}
	for entity in entities:
		temp_lst = []
		entity_to_instances[entity] = temp_lst
	with codecs.open(filePath, "r", encoding="utf-8-sig") as f:
	#with codecs.open(filePath, "r", encoding="ascii") as f:
		for line in f:
			line = line.strip()
			if(len(line) == 0):
				continue
			#print line
			if line.strip() != '':
				#print line
				(entity, value) = line.split("\t")
				entity = entity.strip()
				value = value.strip()
				value = pre_process_value(value)
				if(entity not in entities):
					continue
				entity_to_instances[entity].append(value)
	print filePath
	return (entity_to_instances)
	
def get_relations(filePath):
	relation_instances = {}
	for rtype in relations:
		datas = []
		relation_instances[rtype] = datas
	with open(filePath, "r") as f:
		content = f.readlines()
		print(filePath)
		for line in content:
			if line.strip() != '':
				line = line.replace("("," -lrb- ")
				line = line.replace(")"," -rrb- ")
				#print line
				parts = line.split("\t")
				rtype = parts[0]
				if(rtype not in relations):
					continue
				relation_instances[rtype].append(line.strip())
				#relation_instances[rtype].append(('\t'.join(parts[1:])).strip())
	#print relation_instances
	return relation_instances

def do_instances_match(v1, v2):
	v1 = v1.lower()
	v11 = v1.replace(' ','')
	v2 = v2.lower()
	v22 = v2.replace(' ','')
	if(v22 == v11):
		sim = 1.0
	else:
		sim = compute_similarity(v1, v2)
	if(sim >= 1.0):
		return True
	else:
		return False

def compare_relation_instances(ri_actual, ri_predicted):
	rtype_to_result = {}
	instances_actual_NULL = ri_actual['NULL']
	rtype = 'Rel'
	print rtype
	instances_actual = ri_actual[rtype]
	instances_predicted = ri_predicted[rtype]
	#print len(ri_actual[rtype])
	#print len(ri_predicted[rtype])
	TP = 0
	FP = 0
	FN = 0
	TN = 0
	for instance_actual in instances_actual:
		match_found = False
		for instance_predicted in instances_predicted:
			instance_actual_parts = instance_actual.split('\t')
			instance_predicted_parts = instance_predicted.split('\t')
			num_parts_matched = 0
			#print instance_actual_parts
			#print instance_predicted_parts
			for i in range(1,len(instance_predicted_parts)):
				if(do_instances_match(instance_actual_parts[i], instance_predicted_parts[i])):
					num_parts_matched = num_parts_matched + 1
			if(num_parts_matched == (len(instance_actual_parts)-1)):
				match_found = True
				break
		if(match_found):
			TP = TP + 1
			print 'TP:\t'+instance_actual
		else:
			print 'FN:\t'+instance_actual
			FN = FN + 1
	
	"""for instance_predicted in instances_predicted:
		match_found = False
		for instance_actual in instances_actual:
			instance_actual_parts = instance_actual.split('\t')
			instance_predicted_parts = instance_predicted.split('\t')
			num_parts_matched = 0
			for i in range(1,len(instance_predicted_parts)):
				if(do_instances_match(instance_actual_parts[i], instance_predicted_parts[i])):
					num_parts_matched = num_parts_matched + 1
			if(num_parts_matched == (len(instance_actual_parts)-1)):
				match_found = True
				break
		if(not(match_found)):
			print 'FP:\t'+instance_predicted
			FP = FP + 1"""
			
	for instance_actual_NULL in instances_actual_NULL:
		match_found = False
		for instance_predicted in instances_predicted:
			instance_actual_parts = instance_actual_NULL.split('\t')
			instance_predicted_parts = instance_predicted.split('\t')
			num_parts_matched = 0
			for i in range(1,len(instance_predicted_parts)):
				if(do_instances_match(instance_actual_parts[i], instance_predicted_parts[i])):
					num_parts_matched = num_parts_matched + 1
			if(num_parts_matched == (len(instance_actual_parts)-1)):
				match_found = True
				break
		if(not(match_found)):
			TN = TN + 1
		else:
			print 'FP:\t'+instance_actual_NULL
			FP = FP + 1
	#print (TP, FP, FN)
	rtype_to_result[rtype] = (TP, FP, FN, TN)
	return(rtype_to_result)

results = []
for fileName in filesList:
	name = fileName.split(path_sep)[-1].split(".txt")[0]
	file1 = fileName
	file2 = folder2+name+".txt"
	if(name.find('_relation_') >= 0):
		relation_instances_actual = get_relations(file1)
		relation_instances_predicted = get_relations(file2)
		#print '**'+name
		results.append((fileName,compare_relation_instances(relation_instances_actual, relation_instances_predicted)))

tps = 0
fns = 0
fps = 0
tns = 0
totals = 0
with open(sys.argv[3],'w') as f:
	for rtype in relations:
		if(rtype == 'NULL'):
			continue
		f.write('\n==========\n'+rtype+'\n===========\n')
		TPs = 0
		FPs = 0
		FNs = 0
		TNs = 0
		for result in results:
			f.write(result[0]+'\n')
			f.write(str(result[1][rtype])+'\n')
			print result[1][rtype]
			TPs = TPs + result[1][rtype][0]
			FPs = FPs + result[1][rtype][1]
			FNs = FNs + result[1][rtype][2]
			TNs = TNs + result[1][rtype][3]
		pr = 0.0
		if(TPs+FPs > 0):
			pr = float(TPs)/float(TPs+FPs)
		re = 0.0
		if(TPs+FNs > 0):
			re = float(TPs)/float(TPs+FNs)
		f1 = 0.0
		if(pr+re > 0):
			f1 = 2*pr*re/(pr+re)
		accuracy = 0
		if(TPs+TNs+FPs+FNs > 0):
			accuracy = float(TPs+TNs)/float(TPs+TNs+FPs+FNs)
		f.write('TP = ' + str(TPs) + ', FP = ' + str(FPs) + ', FN = ' + str(FNs) + ', TN = ' + str(TNs))
		f.write("\n\nPrecision : "+ str(pr))
		f.write("\nRecall : " +str(re))
		f.write("\nF1 measure :" +str(f1))
		f.write("\nAccuracy : " + str(accuracy))