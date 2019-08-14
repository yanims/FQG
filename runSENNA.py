#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 13:19:48 2019

@author: YM
"""

import os
import pandas as pd
import random


def runSENNA(preprocessed_file):
                                           
  # remember the directory where the program should be run from
  cwd = os.getcwd()
  # change directories to the generated project directory 
  # (the installation command must be run from here)
  path=cwd+'/senna/'
  os.chdir(path)
  
  try:
      # run the shell command
      cmd = './senna -srl < ' + preprocessed_file + ' > output.txt'
      #cmd = './senna -pos -ner -srl < ' + preprocessed_file + ' > output.txt'
      os.system(cmd)
  except:    
      print ('Failed to run SENNA...')
  finally:
      # always change directories to the program directory
      os.chdir(cwd)

#workPath = os.getcwd()  
#senna_input_file = 'input_preprocess.txt'  
#senna_input_path = workPath + '/senna/' + senna_input_file
#runSENNA(senna_input_path)   


def get_score(template):
    list_evaluation_results=[ # default question templates are not included
            ['DEF2',4.3],
            ['DEF3',3.8],
            ['DEF4',4.4],
            ['DEF5',4.4],
            ['DEF6',3.4],
            ['DEF7',4.1],
            ['DEF8',3.8],
            ['HOW3',3.6],
            ['HOW4',4.2],
            ['IST1',2.9],
            ['IST2',3.5],
            ['NEG1',3.2],
            ['NEG2',3.0],
            ['NEG3',3.8],
            ['NEG4',3.8],
            ['NEG5',3.8],
            ['WHC1',4.5],
            ['WHC2',4.3],
            ['WHC3',4.4],
            ['WHC4',4.5],
            ['WHN1',3.9],
            ['WHN3',3.4],
            ['WHN4',4.3],
            ['WHO1',2.5],
            ['WHR1',4.3],
            ['WHR2',4.1],
            ['WHR3',3.8],
            ['WHR4',4.0],
            ['WHR5',4.3],
            ['WHR6',4.0],
            ['WHR7',4.1],
            ['WHT1',4.3],
            ['WHT2',4.0],
            ['WHT3',4.2],
            ['WHT4',4.3],
            ['WHT5',3.8],
            ['WHT8',3.4],
            ['WHY1',4.2],
            ['WHY2',3.5],
            ['WHY4',3.7],
            ['WKD1',4.1],
            ['WKD3',4.3],
            ['WKD4',4.2],
            ['WKD5',4.5],
            ['WKD6',3.7],
            ]
    for score in list_evaluation_results:
        if template == score[0]:
            return score[1]
        
def ranking(listOfAllGeneratedQA):
    list_template_score = []
    
    if len(listOfAllGeneratedQA[0]) == 1: # if there is only 1 sublist
        return listOfAllGeneratedQA[0][0][0]
    
    elif len(listOfAllGeneratedQA[0]) > 1: # if there is more than one sublist
        for template_name in listOfAllGeneratedQA[0]: # loop thru the template 
            list_template_score.append([template_name[0],template_name[1],get_score(template_name[1])])
            
        #print(list_template_score)
        df=pd.DataFrame(list_template_score, columns=['Question','Template','Score'])
        
        # ranking of score in order by descending
        df['Score_ranked']=df['Score'].rank(ascending=1)
        # get questions with the highest rank
        questions=(df[['Question']][df.Score_ranked == df.Score_ranked.max()]) 
        # if there are more than 1 question with highest rank, then pick random one of them
        if len(questions['Question']) > 1:
            return (random.choice(questions['Question']))
        else:
            return questions['Question']