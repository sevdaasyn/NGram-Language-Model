import re
import string
import random
import math

DATA_PATH = "assignment1-dataset.txt"
translator = str.maketrans('', '', string.punctuation)
my_n = 3


def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def dataset(path):
	line_array = []
	file = open(path, "r")
	for line in file:
		handled_line = ("<s> " + line[2:-2].replace('|', ' ').replace('\t','').lower().translate(translator).replace('  ',' ') + " </s>" ).split(" ")
		for w in range(len(handled_line)):
			if(w >= len(handled_line)):
				break
			elif(handled_line[w] == ''):
				del handled_line[w]
	
		line_array.append(handled_line)
	return line_array

lines = dataset(DATA_PATH)

def NGram(n):
	model = {}

	for line in lines:
		if(n==3):
			if(("<s> <s> " + line[1]) not in model):
				model["<s> <s> " + line[1]] = 1
			else:
				model["<s> <s> " + line[1]] += 1

		for i in range( 0, len(line)-n+1) : 
			word = ""
			for k in range(i,i+n):
				word += line[k] + " "
			word = word[:-1]

			if (word not in model):
				model[word] = 1
			else:
				model[word] += 1

	return model

unigram_model = NGram(1)
bigram_model = NGram(2)
trigram_model = NGram(3)

sum_of_val = sum(unigram_model.values())
start = 0
vec={}
for k,v in unigram_model.items():
	vec[k] = [start, start + unigram_model[k]/sum_of_val]
	start = start + unigram_model[k]/sum_of_val

#print(unigram_model)
#print(bigram_model)
#print(trigram_model)

def proces_stc(sentence):
	words = ("<s> "+sentence.replace('|', '').replace('\t','').lower().translate(translator).replace('  ',' ') + " </s>").split(" ")
	stcs = []
	for i in range( 0, len(words) - my_n +1) : 
		word = ""
		for k in range(i , i+my_n):
			word += words[k] + " "
		stcs.append( word[:-1] )
	return stcs

def prob(sentence):
	stcs = proces_stc(sentence)
	result = 1
	for s in stcs:
		if  (my_n == 1 and s in unigram_model):
			result *= unigram_model[s] / sum(unigram_model.values())
		elif(my_n == 2 and s in bigram_model):
			result *= bigram_model[s] / unigram_model[s.split()[0]]
		elif(my_n == 3 and s in unigram_model):
			result *= trigram_model[s] / bigram_model[s.split()[0] +" "+s.split()[1]]
		
	return result

def sprob(sentence):
	stcs = proces_stc(sentence.lower())
	result = 1
	for s in stcs:
		if  (my_n == 1 and s in unigram_model):
			result *= unigram_model[s] +1 / sum(unigram_model.values()) + len(unigram_model)
		elif(my_n == 2 and s in bigram_model):
			result *= bigram_model[s] +1 / unigram_model[s.split()[0]] + len(bigram_model)
		elif(my_n == 3 and s in unigram_model):
			result *= trigram_model[s] +1/ bigram_model[s.split()[0] +" "+s.split()[1]] +len(trigram_model)

	return result

def ppl(sentence):
	stcs = proces_stc(sentence.lower())
	total_log_prob = 1

	for s in stcs:
		if my_n==1:
			if(s in unigram_model):
				total_log_prob += math.log2(unigram_model[s] / sum(unigram_model.values()))
			else:
				total_log_prob += math.log2(1 / (len(unigram_model) + sum(unigram_model.values())))
		elif my_n==2:
			if(s in bigram_model):
				total_log_prob += math.log2( (bigram_model[s] +1)/ (len(bigram_model) + unigram_model[s.split()[0]] ) )
			else:
				total_log_prob += math.log2(1 / ( len(bigram_model) + unigram_model[s.split()[0]] ) )
		elif my_n==3:
			if(s in trigram_model):
				total_log_prob += math.log2(trigram_model[s] / bigram_model[ s.split()[0] + " " + s.split()[1] ] )
			else:
				total_log_prob += math.log2(1 / (len(trigram_model) + bigram_model[ s.split()[0] + " " + s.split()[1]]) )

	return (1 / math.pow(2, total_log_prob/len(sentence.split())) )

def next(word):
	filteredDict = dict()
	gan_chart = {}
	rand_num = random.uniform(0.0,1.0)
	result = ""

	if my_n==1:
		gan_chart = vec

	elif my_n==2:		
		for (key, value) in bigram_model.items():
			if(len(key.split()) != 2):
				continue
			if key.split()[0] == word.lower() :
				filteredDict[key] = value
		#sorted(filteredDict.items(), key = lambda kv:(kv[1], kv[0]))

		sum_of_values = sum(filteredDict.values())

		
		start = 0
		for s in filteredDict:
			gan_chart[s.split()[1]] = [start, start + filteredDict[s]/sum_of_values]
			start = start + filteredDict[s]/sum_of_values
		
	
	elif my_n==3:
		for (key, value) in trigram_model.items():
			if(len(key.split()) != 3):
				continue
			words = key.split()
			if words[0] + " " + words[1]  == word.lower():
				filteredDict[key] = value

		sum_of_values = sum(filteredDict.values())
		start = 0
		for s in filteredDict:
			gan_chart[s.split()[2]] = [start, start + filteredDict[s]/sum_of_values]
			start = start + filteredDict[s]/sum_of_values


	for k , v in gan_chart.items():
		if (rand_num >= v[0] and rand_num < v[1]):
			result = k

	return result



def generate(length, count):
	if my_n == 1 or my_n == 2:
		for i in range(count):
			result = ""
			curr_word = "<s>"
			while len(result.split()) < length and curr_word!="</s>":
				next_w = next(curr_word) 
				result += " "+ next_w
				curr_word = next_w
			print("Sentence : "+ str(result) )
			print("Perplexity = " + str(ppl(result)), end='\n\n')
	if my_n==3:
		for i in range(count):
			result = "<s>"
			curr_word = "<s> <s>"
			while len(result.split()) < length and curr_word.split()[1]!="</s>":
				next_w = next(curr_word) 
				result += " "+ next_w
				curr_word = result.split()[-2] + " " + result.split()[-1]
			print("Sentence : " + str(result[4:]) )
			print("Perplexity = " + str(ppl(result[4:]) ) , end='\n\n')


print("GENERATING UNIGRAM SENTENCES")
print("----------------------------")
my_n = 1
generate(7,5)


print("GENERATING BIGRAM SENTENCES")
print("----------------------------")
my_n = 2
generate(7,3)

print("GENERATING BIGRAM SENTENCES")
print("----------------------------")
my_n = 3
generate(7,3)
