import sys
import re
from os import listdir
from os.path import isfile, join
from shutil import copyfile
import scipy.cluster.hierarchy

print 'Input Folder : ' + sys.argv[1]
print 'Output Folder : ' + sys.argv[2]

#brackets_pattern = re.compile(r'\([^\(\)]*[ \.0-9][^\(\)]*\)')
brackets_pattern = re.compile(r'\([^\(\)A-Za-z]*\)')
multiple_spaces_pattern = re.compile(r'[ ]{2,}')

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

onlyfiles = [f for f in listdir(sys.argv[1]) if isfile(join(sys.argv[1], f))]
for fl in onlyfiles:
	if(str(fl).endswith('.txt')):
		src = join(sys.argv[1],fl)
		dest = join(sys.argv[2],fl)
		f = open(src)
		fw = open(dest,'w')
		for line in f:
			line = brackets_pattern.sub(' ',line)
			line = multiple_spaces_pattern.sub(' ',line)
			fw.write(line)
		f.close()
		fw.close()
		#copyfile(src, dest)
	elif(str(fl).endswith('.a2')):
		instance_to_etype = {}
		instance_to_start_end = {}
		start_end_to_instance = {}
		rel_instance_to_rtype = {}
		id_to_instance = {}
		f = open(join(sys.argv[1],fl))
		for line in f:
			line = line.strip()
			parts = line.split('\t')
			if(line.startswith('T')):
				etype = parts[1].split(' ')[0]
				si = int(parts[1].split(' ')[1])
				ei = int(parts[1].split(' ')[2].split(';')[0])
				instance = parts[2].strip()
				instance_to_etype[instance] = etype
				instance_to_start_end[instance] = (si,ei)
				start_end = str(si) + ':' + str(ei)
				start_end_to_instance[start_end] = instance
				id_to_instance[parts[0]] = instance
			elif(line.startswith('R')):
				rel_parts = parts[1].split(' ')
				rtype = rel_parts[0]
				id1 = rel_parts[1].split(':')[1]
				id2 = rel_parts[2].split(':')[1]
				if(id1 not in id_to_instance or id2 not in id_to_instance):
					print 'ERROR!!'
				else:
					rel_instance = id_to_instance[id1] + '\t' + id_to_instance[id2]
					rel_instance_to_rtype[rel_instance] = rtype
		f.close()
		
		#print instance_to_start_end
		
		instances_to_discard = {}
		start_end_discarded = []
		rel_instances_to_discard = {}
		for start_end, instance in start_end_to_instance.iteritems():
			si = int(start_end.split(':')[0])
			ei = int(start_end.split(':')[1])
			for start_end_inner, instance_inner in start_end_to_instance.iteritems():
				#if(instance == instance_inner or instance_inner in instances_to_discard):
				if(instance == instance_inner):
					continue
				si_inner = int(start_end_inner.split(':')[0])
				ei_inner = int(start_end_inner.split(':')[1])
				#print instance + '\t' + instance_inner
				#print str(si) + ' ' + str(si_inner)
				#print str(ei) + ' ' + str(ei_inner)
				if(si >= si_inner and si <= ei_inner and ei >= si_inner and ei <= ei_inner):
					print instance + ': is contained within ' + instance_inner
					#instances_to_discard[instance] = ''
					start_end_discarded.append(start_end)
		
		new_instances = {}
		for start_end, instance in start_end_to_instance.iteritems():
			if(start_end in start_end_discarded):
				continue
			new_instances[instance] = ''
		print new_instances
		for instance, etype in instance_to_etype.iteritems():
			if(instance not in new_instances):
				instances_to_discard[instance] = ''
				print instance + ': is discarded '
		
		"""instance_to_etype_new = {}
		for instance, etype in instance_to_etype.iteritems():
			if(instance not in instances_to_discard):
				instance_to_etype_new[instance] = etype
		instance_to_etype = instance_to_etype_new
				
		rel_instance_to_rtype_new = {}
		for rel_instance,rtype in rel_instance_to_rtype.iteritems():
			if(rel_instance not in rel_instances_to_discard):
				rel_instance_to_rtype_new[rel_instance] = rtype
		rel_instance_to_rtype = rel_instance_to_rtype_new"""
				
		instance_to_cluster = {}
		cluster_to_instances = {}
		instances = instance_to_etype.keys()
		y = []
		for i in range(len(instances)-1):
			i1 = instances[i]
			et1 = instance_to_etype[i1]
			for j in range(i+1, len(instances)):
				i2 = instances[j]
				et2 = instance_to_etype[i2]
				if(et1 != et2):
					y.append(1.0)
				elif(do_instances_match(i1, i2)):
					y.append(0.0)
				else:
					y.append(1.0)
		if(len(y) > 0):
			z = scipy.cluster.hierarchy.single(y)
			n = len(instances)
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
				cl_instances = []
				for ii in indices:
					cl_instances.append(instances[ii])
					instance_to_cluster[instances[ii]] = cl_num
				cluster_to_instances[cl_num] = cl_instances
		
		rel_instance_to_rtype_new = {}
		for rel_instance, rtype in rel_instance_to_rtype.iteritems():
			rel_instance_to_rtype_new[rel_instance] = rtype
			i1 = rel_instance.split('\t')[0]
			i2 = rel_instance.split('\t')[1]
			i1_sim_instances = cluster_to_instances[instance_to_cluster[i1]]
			i2_sim_instances = cluster_to_instances[instance_to_cluster[i2]]
			for ii1 in i1_sim_instances:
				for ii2 in i2_sim_instances:
					rel_instance_new = ii1 + '\t' + ii2
					rel_instance_to_rtype_new[rel_instance_new] = rtype
					print 'Added : ' + rel_instance_new
					
		for rel_instance,rtype in rel_instance_to_rtype_new.iteritems():
			rel_instance_parts = rel_instance.split('\t')
			if(rel_instance_parts[0] in instances_to_discard or rel_instance_parts[1] in instances_to_discard):
				rel_instances_to_discard[rel_instance] = ''
		
		"""instances_involved_in_relation = {}
		for rel_instance, rtype in rel_instance_to_rtype_new.iteritems():
			i1 = rel_instance.split('\t')[0]
			i2 = rel_instance.split('\t')[1]
			instances_involved_in_relation[i1] = ''
			instances_involved_in_relation[i2] = ''
			
		for instance, etype in instance_to_etype.iteritems():
			if(etype == 'Bacteria'):
				continue
			for instance_inner, etype_inner in instance_to_etype.iteritems():
				if(etype != etype_inner):
					continue
				if(instance == instance_inner or instance in instances_to_discard):
					continue
				contained_pattern = re.compile(r'\b'+instance_inner+r'\b')
				if(len(instance) > len(instance_inner) and contained_pattern.search(instance) and instance not in instances_involved_in_relation and instance_inner in instances_involved_in_relation):
					print instance_inner + ': is contained within ' + instance + ' and ' + instance + ' is not involved in any relation'
					instances_to_discard[instance] = ''"""
			
		
		fw = open(join(sys.argv[2],str(fl).replace('.a2','_instances.txt')),'w')
		for instance,etype in instance_to_etype.iteritems():
			if(etype == 'Geographical'):
				etype = 'Habitat'
			if(instance in instances_to_discard):
				continue
			fw.write(etype + '\t' + instance + '\n')
		fw.close()
		fw = open(join(sys.argv[2],str(fl).replace('.a2','_relation_instances.txt')),'w')
		for rel_instance,rtype in rel_instance_to_rtype_new.iteritems():
			if(rel_instance in rel_instances_to_discard):
				continue
			fw.write(rtype + '\t' + rel_instance + '\n')
		fw.close()