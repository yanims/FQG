#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 00:42:13 2019

@author: YM
"""
import spacy
import contractions_copy as contractions # pip install contractions doesn't work, so i copy the file here (change to import contractions in case there's update after 4 july 2019)
import re
import truecase # restores case information for text

"""
Tokenize
"""

nlp = spacy.load('en_core_web_sm')

def inputTokenize(inputText):
    doc = nlp(inputText)
    return doc

def preprocess_text (inputText):
    clean_text = ''    
    clean_text = re.sub(' +', ' ', inputText)    # remove double spaces    
    clean_text = contractions.fix(clean_text)    # contraction
    clean_text = truecase.get_true_case(clean_text)
    return clean_text


# transofrm input into senna_input (preprocessed and tokenized)
def preprocess_senna_input (input_path, senna_input_path):  
    preprocessed = ''
    with open(input_path) as f:
        dlines = f.read().splitlines() #reading a file without newlines
    semList = []    
    for l in dlines:
        if l != '\n': # if not an empty line
            preprocessed = preprocess_text(l)
            tokenized_text = inputTokenize(preprocessed)       
            sentence = ''
            for token in tokenized_text:
                sentence = sentence + token.text + ' '
            semList.append(sentence)
            
    # write to a file        
    with open(senna_input_path, 'w') as f:
        for item in semList:
            f.write("%s\n" % item)
    #print (senna_input_path + ' is successfully generated...')
    
