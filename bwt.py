import sys
import string
import time

def parse_fasta(in_file):
	'''Input: name of fasta in_file
	Output: contents of fasta file as string'''
	f = file(in_file, 'r')
	s = ''
	for line in f:
		if not (line[0] == '' or line[0] == '>' or line[0] == ';'):
			s += line
	return string.join(s.splitlines(), '')

def get_alpha(text):
	'''Input: text string
	Output: sorted list of chars in text'''
	return sorted(list(set(text)))

def make_triples(text, cclass=0):
	'''Input: text (iterable)
	Output: list of triples of text chars, starting from indices in cclass'''
	text = text[cclass:]
	rdr = len(text) % 3
	if rdr != 0: 
		pad = '$' * (3 - rdr)
		text += pad
	triples = [[list(text[i:i + 3]), i + cclass] for i in xrange(0, len(text), 3)]
	return triples

def rad_sort(triples, alpha, index=0):
	'''Input: triples of alpha chars, rad sort at index
	Output: nested list of matching triples in rad sorted order'''
	groups = {}
	for triple in triples:
		sort_char = triple[0][index]
		bucket = groups.get(sort_char, [])
		bucket.append(triple)
		groups[sort_char] = bucket
	grouped = []
	for key in sorted(groups.keys()):
		if len(groups[key])>1 and index<2:
			grouped += (rad_sort(groups[key], alpha, index+1))
		else: 
			grouped.append(groups[key])
	return grouped

def unique_sort(grouped):
	'''Input: nested list of radix sorted triple-characters
	Output: True if all characters are unique, else False'''
	for group in grouped:
		if len(group)>1: return False
	return True

def stringify(my_list):
	'''Input: list of triples
	Output: list of space delimited triple strs'''
	s = ''
	for item in my_list:
		s += str(item)
		s += ' '
	return s

def make_relabel_dict(grouped):
	'''Input: list of grouped, rad sorted triples
	Output: dictionary of stringified triple-type to priority''' 
	relabel_dict = {}
	for index, group in enumerate(grouped):
		relabel_dict[stringify(group[0][0])] = index
	return relabel_dict

def relabel(triples, relabel_dict):
	relabeled = []
	for triple in triples:
		relabeled.append(relabel_dict[stringify(triple[0])])
	return relabeled

def make_R1R2(text):
	R1 = make_triples(text, 1)
	R2 = make_triples(text, 2)
	return R1+R2

def make_R0(text):
	return make_triples(text)

def unnest_singleton_group_list(grouped):
	'''Input: list of groups of triples that are all unique (singleton)
	Output: the same list, with the triples unnested (groups removed)'''
	unnested = []
	for group in grouped:
		unnested.append(group[0])
	return unnested

def make_priority_dict(R_sorted):
	'''Input: list of sorted triples
	Output: dict with kv pairs position:rank for each triple's pos'''
	priority_dict = {}
	for index, triple in enumerate(R_sorted):
		priority_dict[triple[1]] = index
	return priority_dict

def merge(text, R0_sorted, R1R2_sorted):
	'''Input: text(iterable), sorted subsets of triples R0, R1+R2
	Output: A suffix array for text'''

	if R0_sorted[-1][1] == None: 
		del R0_sorted[-1]
	if R0_sorted[0][1] == None: 
		del R0_sorted[0]
	if R1R2_sorted[-1][1] == None: 
		del R1R2_sorted[-1]
	if R1R2_sorted[0][1] == None: 
		del R1R2_sorted[0]

	pdict_R1R2 = make_priority_dict(R1R2_sorted)

	i = 0
	j = 0

	merged_indices = []

	while i<len(R0_sorted) and j<len(R1R2_sorted):
		try:
			elt0 = R0_sorted[i]
			elt12 = R1R2_sorted[j]
			if elt0[0][0] < elt12[0][0]:
				merged_indices.append(elt0[1])
				i += 1
			elif elt12[0][0] < elt0[0][0]:
				merged_indices.append(elt12[1])
				j += 1
			elif elt12[1] % 3 == 1:
				if elt0[0][1] < elt12[0][1]:
					merged_indices.append(elt0[1])
					i += 1
				elif elt12[0][1] < elt0[0][1]:
					merged_indices.append(elt12[1])
					j += 1
				else: 
					if pdict_R1R2[elt0[1] + 1] < pdict_R1R2.get(elt12[1] + 1, -1):
						merged_indices.append(elt0[1])
						i += 1
					elif pdict_R1R2[elt0[1] + 1] > pdict_R1R2.get(elt12[1] + 1, -1):
						merged_indices.append(elt12[1])
						j += 1
			elif elt12[1] % 3 == 2:
				if elt0[0][1] < elt12[0][1]:
					merged_indices.append(elt0[1])
					i += 1
				elif elt12[0][1] < elt0[0][1]:
					merged_indices.append(elt12[1])
					j += 1
				else:
					if elt0[0][2] < elt12[0][2]:
						merged_indices.append(elt0[1])
						i += 1
					elif elt12[0][2] < elt0[0][2]:
						merged_indices.append(elt12[1])
						j += 1
					else:
						if pdict_R1R2[elt0[1] + 2] < pdict_R1R2.get(elt12[1] + 2, -1):
							merged_indices.append(elt0[1])
							i += 1
						elif pdict_R1R2[elt0[1] + 2] > pdict_R1R2.get(elt12[1] + 2, -1):
							merged_indices.append(elt12[1])
							j += 1
		except TypeError:
			print R0_sorted[i], R1R2_sorted[j]

	if i == len(R0_sorted):
		for k in xrange(j, len(R1R2_sorted)):
			merged_indices.append(R1R2_sorted[k][1])
	elif j == len(R1R2_sorted):
		for k in xrange(i, len(R0_sorted)):
			merged_indices.append(R0_sorted[k][1])

	return merged_indices

def sort_triplist_by_As(triplist, suff_arr):
	triplist_sorted = []
	for index in suff_arr:
		triplist_sorted.append(triplist[index])
	return triplist_sorted

def sort_triplist(alpha, triplist):
	triplist_grouped = rad_sort(triplist, alpha)
	unique = unique_sort(triplist_grouped)
	if not unique:
		relabel_dict = make_relabel_dict(triplist_grouped)
		relabeled = relabel(triplist, relabel_dict)
		suff_arr = dc3_loop(relabeled)
		triplist_sorted = sort_triplist_by_As(triplist, suff_arr)
	else:
		triplist_sorted = unnest_singleton_group_list(triplist_grouped)
	return triplist_sorted

def dc3_loop(text):
	alpha = get_alpha(text)
	R1R2 = make_R1R2(text)
	R1R2_sorted = sort_triplist(alpha, R1R2)
	R0 = make_R0(text)
	R0_sorted = sort_triplist(alpha, R0)
	suff_arr = merge(text, R0_sorted, R1R2_sorted)
	return suff_arr

def make_bwt(text, suff_arr):
	'''Input: text string, list of suff_arr indices
	Output: bwt string'''
	s = ''
	for index in suff_arr:
		try:
			s += text[index-1]
		except TypeError:
			pass
	return s

def make_m_occ(bwt):
	'''Input: bwt iterable
	Output: M[c] dict, occ array by index in bwt'''
	occ_arr = []
	occ_dict = {}
	for index, char in enumerate(bwt):
		char_occ = occ_dict.get(char, 0)
		occ_arr.append(char_occ)
		occ_dict[char] = char_occ + 1

	m = {}
	lesser_char = 0
	for char in sorted(occ_dict.keys()):
		m[char] = lesser_char 
		lesser_char += occ_dict[char]

	return (m, occ_arr)

def decode(bwt, m, occ_arr):
	'''Input: bwt, m[c] -> 1st pos c in F, array of occ for char at each pos
	Output: decoded string'''
	s = '$'
	char_idx = 0
	char = bwt[char_idx]
	while char != '$':
		s = char + s
		char_idx = m[char] + occ_arr[char_idx]
		char = bwt[char_idx]
	return s

def make_fasta(out_file, header, text):
	f = file(out_file, 'w')
	f.write('>' + header + '\n')
	i = 0
	while len(text) - i > 80:
		f.write(text[i:i + 80] + '\n')
		i += 80
	f.write(text[i:])
	f.close()

def test_suff_arr(suff_arr):
	for index, value in enumerate(sorted(suff_arr)):
		if index != value:
			return "Bad suffix array"
	return "Good suffix array"

def route():
	transform = sys.argv[1]
	in_file = sys.argv[2]
	out_file = sys.argv[3]

	if transform == '-bwt':
		text = parse_fasta(in_file)
		triples = make_triples(text)
		suff_arr = dc3_loop(text)
		bwt = make_bwt(text, suff_arr)
		make_fasta(out_file, 'BWT', bwt)
		return "see output file for bwt"

	elif transform == '-ibwt':
		bwt = parse_fasta(in_file)
		m, occ_arr = make_m_occ(bwt)
		text = decode(bwt, m, occ_arr)
		make_fasta(out_file, 'iBWT', text)
		return "see output file for text"

	else: 
		return "Please enter valid procedure flag [-bwt, -ibwt]"

if __name__ == "__main__":
	# start = time.time()
	print route()
	# finish = time.time()
	# print finish-start