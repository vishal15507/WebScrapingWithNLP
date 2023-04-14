# -*- coding: utf-8 -*-


import pandas as pd

#path="/content/drive/MyDrive/Internshala/BlackCoffer/"
path=""
df=pd.read_excel(f"{path}Input.xlsx")
urls=df.URL

print(df.head())

print(urls)

import os

#listing the stopwords
folder_path = f'{path}StopWords' 
file_list = os.listdir(folder_path)
stopwords=[]
for file_name in file_list:
    # do something with each file name
    print(file_name)
    with open(f"{path}StopWords/{file_name}","r",encoding ="latin-1") as file:
      f=file.read()
      f=f.split("\n")
      f=[word.split("|")[0] for word in f]
      f=[word.strip() for word in f]
      f=[word.lower() for word in f if word !=""]
      print(f)
      for word in f:
        stopwords.append(word)
print(stopwords)

#listing the positive and negative words 
master_dictionary={}
with open(f"{path}MasterDictionary/positive-words.txt","r",encoding="latin-1") as pos_file:
  fp=pos_file.read()
  fp=fp.split("\n")
  # print(fp)
  for word_p in fp:
    if word_p !="":
      master_dictionary.update({word_p:1}) #1 if the word is positive

with open(f"{path}MasterDictionary/negative-words.txt","r",encoding="latin-1") as neg_file:
  fn=neg_file.read()
  fn=fn.split("\n")
  # print(fn)
  for word_n in fn:
    if word_n !="":
      master_dictionary.update({word_n:0}) #0 if the word is positive

print(master_dictionary)

#importing modules
from bs4 import BeautifulSoup
import requests

# modules for nlp
import re
import nltk
# nltk.download("stopwords")
# from nltk.corpus import stopwords
#from nltk.stem.porter import PorterStemmer

from textblob import TextBlob
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

import time

#making a empty dictionary for saving data
data={
    "URL_ID":[],
    "URL":[],
    "POSITIVE SCORE":[],
    "NEGATIVE SCORE":[],
    "POLARITY SCORE":[],
    "SUBJECTIVITY SCORE":[],
    "AVG SENTENCE LENGTH":[],
    "PERCENTAGE OF COMPLEX WORDS":[],
    "FOG_INDEX":[],
    "AVG NUMBER OF WORDS PER SENTENCE":[],
    "COMPLEX WORD COUNT":[],
    "WORD COUNT":[],
    "SYLLABLE PER WORD":[],
    "PERSONAL PRONOUNS":[],
    "AVG WORD LENGTH":[]
    }

corpus=[]
personal_pronouns_list = ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'mine', 'yours', 'his', 'hers', 'its', 'ours', 'theirs', 'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves']

#looping through each url
for i in range(len(urls)):
  
  url_id=df.loc[i,"URL_ID"]
  print(f"URL_ID:{url_id}")
  data["URL_ID"].append(url_id)
  link=df.loc[i,"URL"]
  print(f"URL:{link}")
  data["URL"].append(link)

  # loading the web page
  response=requests.get(link)
  content=response.text
  soup=BeautifulSoup(content,"html.parser")

  # selecting heading and content in two different list
  heading_tags=soup.findAll(name="h1")
  heading_list=[element.string for element in heading_tags ]

  para_tags=soup.select("p:not(:has(a,strong))")
  para_list=""
  for element in para_tags:
    para_list=f"{para_list} {element.string}"

  # printing the heading and the content
  print(heading_list) #heading
  print(para_list)  #raw content/data

  #Saving content to the file inside a folder named url_contents
  with open(f"{path}url_contents/{url_id}.txt", "w") as content_file:
    content_file.write(para_list)

  # data cleaning
  content1=re.sub("[^a-zA-Z]"," ",para_list) #for removing the non alphabetical characters
  content2=content1.lower() #converting the words to lower case
  content3=content2.split() #making the list of words
  # ps=PorterStemmer()#->(followed by ps.stem() for each word if we use stemmer) #for stemming eg:(played=play)
  # all_stopwords=stopwords.words("english")
  # all_stopwords.remove("not") #because we dont want 'not' to be removed from the content
  content4=[word for word in content3 if word not in set(stopwords)] #if the word from content is not in stopwords only then consider it in the list
  content=" ".join(content4) #joining all the words with spaces
  corpus.append(content)  #adding the content of the ith url to corpus list
  print(content)

  # finding positive negative
  positive=0
  negative=0
  for word in content.split():
    if word in set(master_dictionary.keys()):
      if master_dictionary[word]==1:
        positive=positive+1
      elif master_dictionary[word]==0:
        negative=negative+1
  print(f"positive:{positive}")
  data["POSITIVE SCORE"].append(positive)
  print(f"negative:{negative}")
  data["NEGATIVE SCORE"].append(negative)

  # finding polarity score
  blob = TextBlob(content)
  polarity_score = blob.sentiment.polarity
  print(f"polarity_score:{polarity_score}")
  data["POLARITY SCORE"].append(polarity_score)

  #finding subjectivity score
  subjectivity_score=blob.sentiment.subjectivity
  print(f"subjectivity_score:{subjectivity_score}")
  data["SUBJECTIVITY SCORE"].append(subjectivity_score)

  #finding average sentense length
  total_sentence_length=0
  sentence_no=0
  for sentence in para_list.split("."):
    total_sentence_length=len(sentence)+total_sentence_length
    sentence_no=sentence_no+1
  avg_sentence_length=total_sentence_length/sentence_no
  print(f"avg_sentence_length:{avg_sentence_length}")
  data["AVG SENTENCE LENGTH"].append(avg_sentence_length)

  # finding the percentage of complex words
  complex_word_count=0
  total_word_count=0
  total_syllables=0
  personal_pronoun=0
  for word in content2:
    pos = nltk.pos_tag([word])[0][1]
    # print(nltk.pos_tag([word])[0])
    # print(nltk.pos_tag([word])[0][1])
    if pos.startswith('NN') or pos.startswith('VB') or pos.startswith('JJ'):
        complex_word_count=complex_word_count+1
    total_word_count=total_word_count+1
    
    # counting the syllables
    syllable_in_word=0
    for i in range(len(word)) :
      if(i==0 and word[i] in "aeiou"):
        syllable_in_word=syllable_in_word+1
      elif(word[i] in "aeiou" and word[i-1] not in "aeiou"):
        syllable_in_word=syllable_in_word+1
    if(word[-1]=="e"):
      syllable_in_word=syllable_in_word-1
    if syllable_in_word==0:
      syllable_in_word=1
    total_syllables=total_syllables+syllable_in_word

    # personal pronouns
    if word in personal_pronouns_list:
      personal_pronoun=personal_pronoun+1 

  #percentage of complex word
  percent_of_complex_words=(complex_word_count*100)/total_word_count
  print(f"percent of complex words is:{percent_of_complex_words}")
  data["PERCENTAGE OF COMPLEX WORDS"].append(percent_of_complex_words)

  # finding the fog index: measures the difficulty level of a written text
  # Fog Index = 0.4 * ( (words ÷ sentences) + 100 * (complex_words ÷ words) )
  fog_index= 0.4*((total_word_count/len(para_list.split("."))))+100*(percent_of_complex_words)
  print(f"fog_index:{fog_index}")
  data["FOG_INDEX"].append(fog_index)

  # average number of words per sentence
  avg_word_count=total_word_count/sentence_no
  print(f"average number of words per sentence:{avg_word_count}")
  data["AVG NUMBER OF WORDS PER SENTENCE"].append(avg_word_count)

  # complex word count
  print(f"complex word count:{complex_word_count}")
  data["COMPLEX WORD COUNT"].append(complex_word_count)

  # word count
  print(f"word count:{total_word_count}")
  data["WORD COUNT"].append(total_word_count)

  #finding syllables per word
  syllables_per_word=total_syllables/total_word_count
  print(f"total no. of syllables per word are:{syllables_per_word}")
  data["SYLLABLE PER WORD"].append(syllables_per_word)

  # personal pronouns
  print(f"personal_pronoun:{personal_pronoun}")
  data["PERSONAL PRONOUNS"].append(personal_pronoun)

  # average word length
  avg_word_length=len(content2)/len(content2.split())
  print(f"avg_word_length:{avg_word_length}")
  data["AVG WORD LENGTH"].append(avg_word_length)
  
  print("///////////////////////////////")
  time.sleep(2) #in order to avoid loss or data or any other data scraping related problem, we give 2 seconds to the system to rest


print(data)


#making a dataframe
df=pd.DataFrame(data)
print(df)

#writing output to the excel file
writer = pd.ExcelWriter(f'{path}Output Data Structure.xlsx')
df.to_excel(writer, index=False)
writer.save()

