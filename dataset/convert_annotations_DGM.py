import sys
import re
import codecs
import json
import pprint
from os import listdir
from os.path import isfile, join
from shutil import copyfile

print 'Input JSON file : ' + sys.argv[1]
print 'Output Folder : ' + sys.argv[2]
print 'Known drugs : ' + sys.argv[3]
print 'Known genes : ' + sys.argv[4]
print 'Known variants : ' + sys.argv[5]
print 'Fold : ' + sys.argv[6]

bracket_text_pattern = re.compile(r'\([^\(\)]+\)')
multiple_spaces_pattern = re.compile(r'[ ]{2,}')

def load_gazette(filename):
	fw_to_names = {}
	f = codecs.open(filename, encoding='utf-8')
	for line in f:
		parts = line.strip().lower().split(' ')
		if(parts[0] in fw_to_names):
			fw_to_names[parts[0]].append(parts)
		else:
			lst_names = []
			lst_names.append(parts)
			fw_to_names[parts[0]] = lst_names
	f.close()
	return fw_to_names

def match_with_gazette(doc_contents, fw_to_names):
	matches = []
	sentences = doc_contents.split('\n')
	for sentence in sentences:
		words = sentence.split(' ')
		print 'Words : ' + str(words)
		for i,word in enumerate(words):
			if(word.lower() in fw_to_names):
				lst_names = fw_to_names[word.lower()]
				longest_match = ''
				max_len = 0
				for name in lst_names:
					match_found = True
					for j in range(len(name)):
						if((i+j) >= len(words)):
							match_found = False
							break
						if(words[i+j].lower() != name[j]):
							match_found = False
							break
						else:
							print 'Same : ' + words[i+j].lower() + '\t' + name[j]
					if(match_found):
						if(len(name) > max_len):
							max_len = len(name)
							longest_match = name
				if(len(longest_match) > 0):
					matches.append(' '.join(longest_match))
	return matches

fw_to_drugs = load_gazette(sys.argv[3])
fw_to_genes = load_gazette(sys.argv[4])
fw_to_variants = load_gazette(sys.argv[5])
	
article_to_sno_to_sentence = {}
article_to_entities_rel_types = {}
f = open(sys.argv[1])
line_no = 1
cnt = 1
for line in f:
	line = line.strip()
	data = json.loads(line)
	print len(data)
	print data[0].keys()
	print data[0][u'entities']
	print data[0][u'relationLabel']
	for data_part in data:
		article = data_part[u'article']
		doc = data_part[u'article']
		sentences = data_part[u'sentences']
		entities = data_part[u'entities']
		rel_type = data_part[u'relationLabel']
		print 'Relation: ' + rel_type
		if(len(entities) > 3):
			print '\t' + str(entities)
		snos = {}
		for sentence in sentences:
			sno = int(sentence[u'sentence'])
			snos[sno] = ''
		sorted_snos = sorted(snos.keys())
		#article = article + '_' + '_'.join(sorted_snos)
		for sentence in sentences:
			sno = sentence[u'sentence']
			nodes = sentence[u'nodes']
			sent = []
			for node in nodes:
				word = node[u'label']
				sent.append(word)
			#print str(article) + '\t' + str(sno) + '\t' + str(sent)
			
			if(article in article_to_sno_to_sentence):
				sno_to_sentence = article_to_sno_to_sentence[article]
				sno_to_sentence[sno] = sent
			else:
				sno_to_sentence = {}
				sno_to_sentence[sno] = sent
				article_to_sno_to_sentence[article] = sno_to_sentence
		
		entity_instances = []
		for entity in entities:
			sno = entity[u'sentence']
			etype = entity[u'type']
			indexes = entity[u'indices']
			mention = entity[u'mention']
			entity_instances.append((sno,etype,indexes,mention))
		
		if(article in article_to_entities_rel_types):
			entities_rel_types = article_to_entities_rel_types[article]
			entities_rel_types.append((entity_instances,rel_type,sorted_snos[0],sorted_snos[-1]))
		else:
			entities_rel_types = []
			entities_rel_types.append((entity_instances,rel_type,sorted_snos[0],sorted_snos[-1]))
			article_to_entities_rel_types[article] = entities_rel_types
		cnt = cnt + 1

article_to_sections = {}
print '#Articles = ' + str(len(article_to_sno_to_sentence))
for article, sno_to_sentence in article_to_sno_to_sentence.iteritems():
	sorted_snos = sorted(sno_to_sentence)
	start_index = -1
	end_index = -1
	sections = []
	for i,sno in enumerate(sorted_snos):
		print str(article) + '\t' + str(sno) + '\t' + str(article_to_sno_to_sentence[article][sno])
		if(i == 0 or (i > 0 and sno > (sorted_snos[i-1]+1))):
			if(start_index >= 0 and end_index >= 0):
				sections.append((start_index,end_index))
			start_index = sno
			end_index = sno
		elif(sno == (sorted_snos[i-1]+1)):
			end_index = sno
	if(start_index >= 0 and end_index >= 0):
		sections.append((start_index,end_index))
	article_to_sections[article] = sections
	print article + '\tSections:' + str(sections)

outDir = sys.argv[2]
distinct_rel_types = {}
distinct_etypes = {}
for article, entities_rel_types in article_to_entities_rel_types.iteritems():
	print article
	sections = article_to_sections[article]
	sno_to_sentence = article_to_sno_to_sentence[article]
	for section in sections:
		start_index = section[0]
		end_index = section[1]
		doc_name = sys.argv[6]+'_'+str(article)+'_'+str(start_index)+'_'+str(end_index)
		doc_contents = ''
		fw = codecs.open(join(outDir,doc_name+'.txt'),'w', encoding='utf-8')
		for i in range(start_index,end_index+1):
			if(i in sno_to_sentence):
				doc_sent = ' '.join(sno_to_sentence[i])
				#fw.write(doc_sent+'\n')
				doc_contents = doc_contents + '\n' + doc_sent
		#fw.close()
		doc_contents = doc_contents.strip()
		
		"""doc_contents = bracket_text_pattern.sub(' ',doc_contents)
		doc_contents = multiple_spaces_pattern.sub(' ',doc_contents)
		doc_contents = doc_contents.strip()"""
		fw.write(doc_contents)
		fw.close()
		
		fw = codecs.open(join(outDir,doc_name+'_relation_instances.txt'),'w', encoding='utf-8')
		rel_lines = []
		for entities_rel_type in entities_rel_types:
			pprint.pprint(entities_rel_type)
			rel_type = entities_rel_type[1]
			start_sno = entities_rel_type[2]
			end_sno = entities_rel_type[3]
			if(end_sno < start_index or start_sno > end_index):
				print '\tSkipping becuase of misplaced relation instance..'
				continue
			
			if(rel_type.lower().strip() == 'none'):
				rel_type = 'NULL'
			else:
				rel_type = 'Rel'
			if(rel_type in distinct_rel_types):
				curr_cnt = distinct_rel_types[rel_type]
				distinct_rel_types[rel_type] = curr_cnt + 1
			else:
				distinct_rel_types[rel_type] = 1
			if(doc_contents.find(entities_rel_type[0][0][3]) < 0 or doc_contents.find(entities_rel_type[0][1][3]) < 0 or doc_contents.find(entities_rel_type[0][2][3]) < 0):
				continue
			line = rel_type + '\t' + entities_rel_type[0][0][3] + '\t' + entities_rel_type[0][1][3] + '\t' + entities_rel_type[0][2][3]
			#rel_lines[line] = ''
			rel_lines.append(line)
			#fw.write(line+'\n')
		#for line in rel_lines.keys():
		for line in rel_lines:
			fw.write(line+'\n')
		fw.close()
		
		fw = codecs.open(join(outDir,doc_name+'_instances.txt'),'w', encoding='utf-8')
		etype_to_instances = {}
		for entities_rel_type in entities_rel_types:
			for i in range(3):
				etype = entities_rel_type[0][i][1]
				instance = entities_rel_type[0][i][3]
				if(doc_contents.find(instance) < 0):
					continue
				if(etype in etype_to_instances):
					etype_to_instances[etype][instance] = ''
				else:
					temp_dict = {}
					temp_dict[instance] = ''
					etype_to_instances[etype] = temp_dict
				if(etype in distinct_etypes):
					curr_cnt = distinct_etypes[etype]
					distinct_etypes[etype] = curr_cnt + 1
				else:
					distinct_etypes[etype] = 1
		all_instances = {}
		for etype, instances in etype_to_instances.iteritems():
			for instance in instances.keys():
				all_instances[instance.lower()] = ''
				fw.write(etype + '\t' + instance + '\n')
				
		#Gazette lookup
		matched_drugs = match_with_gazette(doc_contents, fw_to_drugs)
		matched_genes = match_with_gazette(doc_contents, fw_to_genes)
		matched_variants = match_with_gazette(doc_contents, fw_to_variants)
		
		for dd in matched_drugs:
			if(dd not in all_instances):
				print 'New drug : ' + dd
				fw.write('drug\t' + dd + '\n')
		for gg in matched_genes:
			if(gg not in all_instances):
				print 'New gene : ' + gg
				fw.write('gene\t' + gg + '\n')
		for vv in matched_variants:
			if(vv not in all_instances):
				print 'New variant : ' + vv
				fw.write('variant\t' + vv + '\n')
		fw.close()

pprint.pprint(distinct_etypes)
pprint.pprint(distinct_rel_types)