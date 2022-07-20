import sys
import re
from os import listdir
from os.path import isfile, join

print 'Input File (MUC-6 formal-trng-st keys file) : ' + sys.argv[1]
print 'Input File (MUC-6 formal-trng-st texts file) : ' + sys.argv[2]
print 'Output Folder : ' + sys.argv[3]

p_pattern = re.compile(r'(</?p>)')
multiple_spaces_pattern = re.compile(r'[ ]{2,}')
multiple_newlines_pattern = re.compile(r'[ ]*[\r\n]+[ ]*')

def process_text(text):
	text = p_pattern.sub(r'\n',text)
	text = multiple_newlines_pattern.sub('\n',text)
	text = multiple_spaces_pattern.sub(' ',text)
	return text.strip()

f = open(sys.argv[1])
lines = []
for line in f:
	lines.append(line)
f.close()

per_id_to_name = {}
per_id_to_aliases = {}
org_id_to_name = {}
org_id_to_aliases = {}
for i,line in enumerate(lines):
	if(line.startswith('<ORGANIZATION-')):
		org_id = line.strip().replace(':=','').strip()
		org_alias = None
		j = i+1
		while j < len(lines):
			if(lines[j].strip().startswith('ORG_NAME:')):
				org_name = lines[j].strip().replace('ORG_NAME:','').strip().strip('"')
				org_id_to_name[org_id] = org_name
				temp_lst = []
				temp_lst.append(org_name)
				org_id_to_aliases[org_id] = temp_lst
			elif(lines[j].strip().startswith('ORG_ALIAS:')):
				org_alias = lines[j].strip().replace('ORG_ALIAS:','').strip().replace('/','').strip().strip('"')
				org_id_to_aliases[org_id].append(org_alias)
			elif(org_alias is not None and (lines[j].strip().startswith('/') or lines[j].strip().startswith('"'))):
				org_alias = lines[j].strip().replace('/','').strip().strip('"')
				org_id_to_aliases[org_id].append(org_alias)
			else:
				break
			j = j + 1
	elif(line.startswith('<PERSON-')):
		per_id = line.strip().replace(':=','').strip()
		per_alias = None
		j = i+1
		while j < len(lines):
			if(lines[j].strip().startswith('PER_NAME:')):
				per_name = lines[j].strip().replace('PER_NAME:','').strip().strip('"')
				per_id_to_name[per_id] = per_name
				temp_lst = []
				temp_lst.append(per_name)
				per_id_to_aliases[per_id] = temp_lst
			elif(lines[j].strip().startswith('PER_ALIAS:')):
				per_alias = lines[j].strip().replace('PER_ALIAS:','').strip().strip('"')
				per_id_to_aliases[per_id].append(per_alias)
			elif(per_alias is not None and (lines[j].strip().startswith('/') or lines[j].strip().startswith('"'))):
				per_alias = lines[j].strip().replace('/','').strip().strip('"')
				per_id_to_aliases[per_id].append(per_alias)
			else:
				break
			j = j + 1

in_out_id_to_per_id = {}
in_out_id_to_status = {}
for i,line in enumerate(lines):
	if(line.startswith('<IN_AND_OUT-')):
		in_out_id = line.strip().replace(':=','').strip()
		j = i+1
		while j < len(lines):
			if(lines[j].strip().startswith('IO_PERSON:')):
				per_id = lines[j].strip().replace('IO_PERSON:','').strip()
				in_out_id_to_per_id[in_out_id] = per_id
			elif(lines[j].strip().startswith('NEW_STATUS:')):
				status = lines[j].strip().replace('NEW_STATUS:','').strip()
				in_out_id_to_status[in_out_id] = status
			else:
				break
			j = j + 1

event_id_to_post = {}
event_id_to_org_id = {}
event_id_to_in_per_id = {}
event_id_to_out_per_id = {}
event_id_to_post_aliases = {}
for i,line in enumerate(lines):
	if(line.startswith('<SUCCESSION_EVENT-')):
		event_id = line.strip().replace(':=','').strip()
		in_out_id = None
		post = None
		j = i+1
		while j < len(lines):
			if(lines[j].strip().startswith('SUCCESSION_ORG:')):
				org_id = lines[j].strip().replace('SUCCESSION_ORG:','').strip()
				event_id_to_org_id[event_id] = org_id
			elif(lines[j].strip().startswith('POST:')):
				post = lines[j].strip().replace('POST:','').strip().replace('/','').strip().strip('"').strip()
				event_id_to_post[event_id] = post
				tmp_lst = []
				tmp_lst.append(post)
				event_id_to_post_aliases[event_id] = tmp_lst
			elif(post is not None and in_out_id is None and (lines[j].strip().startswith('/') or lines[j].strip().startswith('"'))):
				post_alias = lines[j].strip().replace('/','').strip().strip('"')
				event_id_to_post_aliases[event_id].append(post_alias)
			elif(lines[j].strip().startswith('IN_AND_OUT:')):
				in_out_id = lines[j].strip().replace('IN_AND_OUT:','').strip()
				status = in_out_id_to_status[in_out_id]
				per_id = in_out_id_to_per_id[in_out_id]
				if(status == 'IN'):
					event_id_to_in_per_id[event_id] = per_id
				else:
					event_id_to_out_per_id[event_id] = per_id
			elif(in_out_id is not None and lines[j].strip().startswith('<IN_AND_OUT')):
				in_out_id = lines[j].strip()
				status = in_out_id_to_status[in_out_id]
				per_id = in_out_id_to_per_id[in_out_id]
				if(status == 'IN'):
					event_id_to_in_per_id[event_id] = per_id
				else:
					event_id_to_out_per_id[event_id] = per_id
			elif(lines[j].strip().startswith('/')):
				j = j + 1
				continue
			else:
				break
			j = j + 1

doc_id_to_event_ids = {}
for event_id in event_id_to_org_id.keys():
	doc_id = event_id.split('-')[1]
	if(doc_id in doc_id_to_event_ids):
		doc_id_to_event_ids[doc_id][event_id] = ''
	else:
		temp_dict = {}
		temp_dict[event_id] = ''
		doc_id_to_event_ids[doc_id] = temp_dict

doc_id_to_text = {}
curr_doc_id = None
curr_text = ''
InText = False
f = open(sys.argv[2])
for line in f:
	if(line.startswith('<DOCNO>')):
		curr_doc_id = line.strip().replace('</DOCNO>','').replace('<DOCNO>','').strip().strip('.').replace('-','')
	elif(curr_doc_id is not None and line.startswith('<TXT>')):
		InText = True
	elif(curr_doc_id is not None and line.startswith('</TXT>')):
		doc_id_to_text[curr_doc_id] = process_text(curr_text)
		curr_doc_id = None
		curr_text = ''
		InText = False
	elif(InText):
		curr_text = curr_text + ' ' + line.strip()
f.close()

#print len(doc_id_to_text)
#print str(org_id_to_name.keys())
print event_id_to_in_per_id
print event_id_to_out_per_id

doc_id_to_entity_instances = {}
doc_id_to_rel_instances = {}
#for doc_id, text in doc_id_to_text.iteritems():
for doc_id in doc_id_to_event_ids.keys():
	if(doc_id not in doc_id_to_text):
		print 'Doc not present:' + str(doc_id)
		continue
	if(doc_id not in doc_id_to_event_ids):
		continue
	event_ids = doc_id_to_event_ids[doc_id].keys()
	if(len(event_ids) == 0):
		continue
	
	entity_instances = []
	relation_instances = []
	for event_id in event_ids:
		print 'Event Id:' + event_id
		org_id = event_id_to_org_id[event_id]
		if(org_id not in org_id_to_name):
			print org_id
			continue
		org_aliases = org_id_to_aliases[org_id]
		post_aliases = event_id_to_post_aliases[event_id]
		
		
		for org_alias in org_aliases:
			entity_instance = 'ORG\t' + org_alias
			if(entity_instance not in entity_instances):
				entity_instances.append(entity_instance)
		for post_alias in post_aliases:
			entity_instance = 'POST\t' + post_alias
			if(entity_instance not in entity_instances):
				entity_instances.append(entity_instance)
		
		in_per_aliases = []
		out_per_aliases = []
		if(event_id in event_id_to_in_per_id):
			in_per_aliases = per_id_to_aliases[event_id_to_in_per_id[event_id]]
		
		if(event_id in event_id_to_out_per_id):
			out_per_aliases = per_id_to_aliases[event_id_to_out_per_id[event_id]]
			
		if(event_id in event_id_to_in_per_id and event_id in event_id_to_out_per_id):
			in_per_aliases = per_id_to_aliases[event_id_to_in_per_id[event_id]]
			out_per_aliases = per_id_to_aliases[event_id_to_out_per_id[event_id]]
		
		for per_alias in in_per_aliases:
			entity_instance = 'PER\t' + per_alias
			if(entity_instance not in entity_instances):
				entity_instances.append(entity_instance)
		for per_alias in out_per_aliases:
			entity_instance = 'PER\t' + per_alias
			if(entity_instance not in entity_instances):
				entity_instances.append(entity_instance)
		
		if(len(in_per_aliases) > 0 and len(out_per_aliases) > 0):
			for org_name in org_aliases:
				for post_name in post_aliases:
					for out_per_name in out_per_aliases:
						for in_per_name in in_per_aliases:
							relation_instance = 'SUCCESSION\t' + org_name + '\t' + post_name + '\t' + out_per_name + '\t' + in_per_name
							if(relation_instance not in relation_instances):
								relation_instances.append(relation_instance)

	if(len(relation_instances) > 0):
		text = doc_id_to_text[doc_id]
		fw = open(join(sys.argv[3],doc_id+'.txt'),'w')
		fw.write(text)
		fw.close()
		
		fw = open(join(sys.argv[3],doc_id+'_instances.txt'),'w')
		for entity_instance in entity_instances:
			fw.write(entity_instance + '\n')
		fw.close()
		
		fw = open(join(sys.argv[3],doc_id+'_relation_instances.txt'),'w')
		for relation_instance in relation_instances:
			fw.write(relation_instance + '\n')
		fw.close()
		
for event_id, post_aliases in event_id_to_post_aliases.iteritems():
	if(len(post_aliases) > 1):
		print post_aliases