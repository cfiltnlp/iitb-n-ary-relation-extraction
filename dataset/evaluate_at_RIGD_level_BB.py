import glob
import codecs
import re
import sys
from nltk.metrics.distance import edit_distance
import scipy.cluster.hierarchy

path_sep = "\\" #For Windows
#path_sep = "/" #For Linux
print 'Gold annotations folder : ' + sys.argv[1]
print 'Predicted relations folder : ' + sys.argv[2]
print 'Results file :' + sys.argv[3]

folder1 = sys.argv[1]
folder2 = sys.argv[2]
if(not(folder1.endswith(path_sep))):
	folder1 = folder1 + path_sep
if(not(folder2.endswith(path_sep))):
	folder2 = folder2 + path_sep

relations = ['Lives_In']


filesList = glob.glob(folder1+"*.txt")
print len(filesList)

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
				entity_to_instances[entity].append(value.lower())
	print filePath
	return (entity_to_instances)
	
def get_relations(filePath):
	relation_instances = {}
	for rtype in relations:
		datas = {}
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
				relation_instances[rtype][line.strip()] = ''
	#print relation_instances
	return relation_instances

def do_instances_match(s1, s2):
	s1 = s1.lower()
	s2 = s2.lower()
	
	if(s1 == s2):
		return True
		
	if((s1.startswith(s2) and (float(len(s1))/float(len(s2))) < 2.0) or (s2.startswith(s1) and (float(len(s2))/float(len(s1))) < 2.0)):
		return True
	
	s1_words = s1.lower().split(' ')
	s2_words = s2.lower().split(' ')
	if(len(s1_words) == len(s2_words)):
		first_word_same = False
		if(len(s1_words[0]) > len(s2_words[0])):
			if((s2_words[0] == s1_words[0][0]+'.') or (s2_words[0] == s1_words[0][0])):
				first_word_same = True
		else:
			if((s1_words[0] == s2_words[0][0]+'.') or (s1_words[0] == s2_words[0][0])):
				first_word_same = True
		other_words_same = True
		for i in range(1,len(s1_words)):
			if(s1_words[i] != s2_words[i]):
				other_words_same = False
				break
		if(other_words_same and first_word_same):
			return True
	return False
	
def do_relation_instances_match(r1, r2):
	r1_parts = r1.split('\t')
	r2_parts = r2.split('\t')
	for i,r1_part in enumerate(r1_parts):
		if(not(do_instances_match(r1_part, r2_parts[i]))):
			return False
	return True

def cluster_rel_instances(rel_instances):
	clusters = []
	lst_rel_instances = []
	for rel_instance in rel_instances.keys():
		lst_rel_instances.append(rel_instance)
	
	y = []
	for i in range(len(lst_rel_instances)-1):
		ri_i = lst_rel_instances[i]
		for j in range(i+1,len(lst_rel_instances)):
			ri_j = lst_rel_instances[j]
			if(do_relation_instances_match(ri_i,ri_j)):
				y.append(0.0)
			else:
				y.append(1.0)
	
	if(len(y) == 0):
		new_cluster = []
		if(len(lst_rel_instances) == 1):
			new_cluster.append(lst_rel_instances[0])
		clusters.append(new_cluster)
		return clusters
	
	z = scipy.cluster.hierarchy.single(y)
	n = len(lst_rel_instances)
	cluster_num_to_indices = {}
	cluster_num_to_max_dist = {}
	for i in range(n):
		indices = []
		indices.append(i)
		cluster_num_to_indices[i] = indices
		cluster_num_to_max_dist[i] = 0

	for i in range(len(z)):
		c1 = int(z[i][0])
		c2 = int(z[i][1])
		dist = float(z[i][2])
		if(dist > 0.5):
			continue
		new_cluster_num = n+i
		new_indices = []
		c1_indices = cluster_num_to_indices[c1]
		new_indices.extend(c1_indices)
		c2_indices = cluster_num_to_indices[c2]
		new_indices.extend(c2_indices)
		cluster_num_to_indices[new_cluster_num] = new_indices
		cluster_num_to_max_dist[new_cluster_num] = dist
		del cluster_num_to_indices[c1], cluster_num_to_indices[c2]
		
	for cl_num, indices in cluster_num_to_indices.iteritems():
		cluster = []
		for ii in indices:
			cluster.append(lst_rel_instances[ii])
		clusters.append(cluster)

	return clusters
	
def do_clusters_match(c1, c2):
	for r1 in c1:
		for r2 in c2:
			if(do_relation_instances_match(r1, r2)):
				return True
	return False

def compare_relation_instances_alias(ri_actual, ri_predicted):
	rtype_to_result = {}
	for rtype in relations:
		print rtype
		instances_actual = ri_actual[rtype]
		instances_predicted = ri_predicted[rtype]

		rel_instances_clusters_actual = cluster_rel_instances(instances_actual)
		rel_instances_clusters_predicted = cluster_rel_instances(instances_predicted)
		
		print len(rel_instances_clusters_actual)
		print rel_instances_clusters_actual
		print len(rel_instances_clusters_predicted)
		print rel_instances_clusters_predicted
		
		TP = 0
		FP = 0
		FN = 0
		
		for cluster_actual in rel_instances_clusters_actual:
			if(len(cluster_actual) == 0):
				continue
			match_found = False
			for cluster_predicted in rel_instances_clusters_predicted:
				if(len(cluster_predicted) == 0):
					continue
				if(do_clusters_match(cluster_actual, cluster_predicted)):
					match_found = True
					break
			if(match_found):
				TP = TP + 1
				print 'TP:' + str(cluster_actual)
			else:
				FN = FN + 1
				print 'FN:' + str(cluster_actual)
		
		for cluster_predicted in rel_instances_clusters_predicted:
			if(len(cluster_predicted) == 0):
				continue
			match_found = False
			for cluster_actual in rel_instances_clusters_actual:
				if(len(cluster_actual) == 0):
					continue
				if(do_clusters_match(cluster_actual, cluster_predicted)):
					match_found = True
					break
			if(not(match_found)):
				FP = FP + 1
				print 'FP:' + str(cluster_predicted)
		rtype_to_result[rtype] = (TP, FP, FN)
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
		results.append((fileName,compare_relation_instances_alias(relation_instances_actual, relation_instances_predicted)))

tps = 0
fns = 0
fps = 0
totals = 0
with open(sys.argv[3],'w') as f:
	for rtype in relations:
		f.write('\n==========\n'+rtype+'\n===========\n')
		TPs = 0
		FPs = 0
		FNs = 0
		for result in results:
			f.write(result[0]+'\n')
			f.write(str(result[1][rtype])+'\n')
			print result[1][rtype]
			TPs = TPs + result[1][rtype][0]
			FPs = FPs + result[1][rtype][1]
			FNs = FNs + result[1][rtype][2]
		pr = float(TPs)/float(TPs+FPs)
		re = float(TPs)/float(TPs+FNs)
		f1 = 2*pr*re/(pr+re)
		f.write('TP = ' + str(TPs) + ', FP = ' + str(FPs) + ', FN = ' + str(FNs))
		f.write("\n\nPrecision : "+ str(pr))
		f.write("\nRecall : " +str(re))
		f.write("\nF1 measure :" +str(f1))