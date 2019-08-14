#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:42:16 2019

@author: YM
Follow-up Question Generation
Forked from https://github.com/evania
"""

import re
import os
import spacy
from lxml import etree as ET



"""
Tokenize
"""
nlp = spacy.load('en_core_web_sm') 

def inputTokenize(inputText):
    doc = nlp(inputText)
    return doc

def getLemma(word):
    w = nlp(word)
    result = ''
    for token in w:
        result = result + token.lemma_ + ' '
    return result.rstrip()

def seq_in_seq(subseq, seq):
     while subseq[0] in seq:
         index = seq.index(subseq[0])
         if subseq == seq[index:index + len(subseq)]:
             return True
         else:
             seq = seq[index + 1:]
     else:
         return False


"""
Semantic role labelling 
"""

def getSRL():
    
    srlInputFile = workPath + output_file
    with open(srlInputFile) as f:
        slines = f.readlines()
    sentenceListSRL = []
    forSRobj = []
    srlCounter = 1
    for l in slines:
        row = re.split(r'\t+', l)
        if row[0] != '\n':
            srlword = str(row[0]).strip()
            mainverb = str(row[1]).strip()
            srlresult = []
            try:
                srlresult.append(str(row[2]).strip())
            except:
                foo='bar'
            column = 3
            while (len(row) != 0) and (column < len(row)):
                srlresult.append(str(row[column]).strip())
                column = column + 1
            forSRobj.append([srlCounter, srlword, mainverb, srlresult])
            srlCounter = srlCounter + 1
        else:
            sentenceListSRL.append(forSRobj)
            forSRobj = []
            srlCounter = 1
    return sentenceListSRL


"""
Semantic Representation
"""

class SemanticRepresentation:
    
    def __init__(self):
        self.wordid = 0
        # The following variables are for lemma, NER and POS tagging Result
        self.word = ''
        self.tokenindex = ''
        self.lemma = ''
        self.ner = ''
        self.pos = ''
        self.tag = ''
        # The following variable(s) are for Semantic Role Labelling Result
        self.srlword = ''
        self.srlmainverb = ''
        self.srlresult = []

"""
Question Generation
"""
def getV(vList):
    vs = []
    bieWords = ''
    verb = ''
    for a in vList:
        bie = re.search('([BIE]|[bie])-[Vv]', a[2])
        if bie is not None:
            bieWords = bieWords + a[1] + ' '
            bie_group = bie.group(0)
            bie_0 = re.split('-', bie_group)[0]
            bie_1 = re.split('-', bie_group)[1]
            if bie_0 == 'E' or bie_0 == 'e':
                vs.append([bie_1, bieWords])
                bieWords = ''
        else:
            just_v = re.search('[^Cc]-[Vv]', a[2])
            if just_v is not None:
                vs.append(['S-V', a[1]])
    for x in vs:
        verb = verb + x[1] + ' '
    return verb.rstrip() # remove space at the end of the string

class getPosner:
    def __init__(self):
        # The following variables are for lemma, NER and POS tagging Result
        self.arg = ''
        self.location = ''
        self.person = ''
        self.organization = ''   
        self.misc = ''
        self.nns = '' #noun, plural
        self.nn = '' #noun, singular or mass
        self.nnp = '' #proper noun
        self.nnps = '' #proper noun plural
        self.noun = ''
        self.prp = ''
        self.to = ''
        self.vb = ''
        self.arg_words = []
        self.tag_seq = []
        
def getTags(arg, argsList): #input: string arg and list argsList
    tags = getPosner()
    arg_words = []
    tag_seq = []
    flag_loc = flag_per = flag_per = flag_misc = ''
    flag_nns = flag_nn = flag_nnp = flag_nnps = flag_vb = flag_prp = flag_noun = ''
    for a in argsList: #[srl.wordid, srl.srlword, srl.srlresult[column], ner, pos, pos tag google]
        tags.arg = arg        
        # ner tag: location
        if a[3] == 'GPE' or a[3] == 'LOC' or a[3] == 'FAC':
            if tags.location == '' and a[4] != 'DT': #first word, don't include 'the'
                tags.location = tags.location + a[1] + ' '
                flag_loc = a[3]
            elif flag_loc == a[3]: #second word, and so on...
                tags.location = tags.location + a[1] + ' '
        else:
            flag_loc = ''
                
        if (a[3]) == 'PERSON':
            if tags.person == '': #first word
                tags.person = tags.person + a[1] + ' '
                flag_per = a[3]
            elif flag_per == a[3]: #second word, and so on...
                tags.person = tags.person + a[1] + ' '
        else:
            flag_per = ''
            
        if (a[3]) == 'ORG':
            if tags.organization == '':
                tags.organization = tags.organization + a[1] + ' '
                flag_org = a[3]
            elif flag_org == a[3]:
                tags.organization = tags.organization + a[1] + ' '
        else:
            flag_org = ''
            
        if (a[3]) == 'PRODUCT' or a[3] == 'EVENT' or a[3] == 'WORK_OF_ART' or a[3] == 'NORP':
            if tags.misc == '' and a[4] != 'DT': #first word
                tags.misc = tags.misc + a[1] + ' '
                flag_misc = a[3]
            elif flag_misc == a[3]:
                tags.misc = tags.misc + a[1] + ' '
        else:
            flag_misc = ''
            
        if (a[5]) == 'NOUN':
            if (a[4]) == 'NN' or (a[4]) == 'NNS' :
                if tags.noun == '': #first word
                    tags.noun = tags.noun + a[1] + ' '
                    flag_noun = a[5]
                elif flag_noun == a[5]:
                    tags.noun = tags.noun + a[1] + ' '
        else:
            flag_noun = ''
        
        if (a[4]) == 'NNS':
            if tags.nns == '': #first word
                tags.nns = tags.nns + a[1] + ' '
                flag_nns = a[4]
            elif flag_nns == a[4]:
                tags.nns = tags.nns + a[1] + ' '
        else:
            flag_nns = ''
            
        # pos tag: singular words
        if (a[4]) == 'NN':
            if tags.nn == '': #first word
                tags.nn = tags.nn + a[1] + ' '
                flag_nn = a[4]
            elif flag_nn == a[4]:
                tags.nn = tags.nn + a[1] + ' '
        else: flag_nn = ''
        
        # pos tag: proper noun singular
        if (a[4]) == 'NNP':
            if tags.nnp == '': #first word
                tags.nnp = tags.nnp + a[1] + ' '
                flag_nnp = a[4]
            elif flag_nnp == a[4]:
                tags.nnp = tags.nnp + a[1] + ' '
        else: flag_nnp = ''
        
        # pos tag: proper noun singular
        if (a[4]) == 'NNPS':
            if tags.nnps == '': #first word
                tags.nnps = tags.nnps + a[1] + ' '
                flag_nnps = a[4]
            elif flag_nnps == a[4]:
                tags.nnps = tags.nnps + a[1] + ' '
        else: flag_nnps = ''
        
        # pos tag: proper noun singular
        if (a[4]) == 'PRP':
            if tags.prp == '': #first word
                tags.prp = tags.prp + a[1] + ' '
                flag_prp = a[4]
            elif flag_prp == a[4]:
                tags.prp = tags.prp + a[1] + ' '
        else: flag_prp = ''
        
        # pos tag: to
        if (a[4]) == 'TO':
            tags.to = True
 
        #if (a[4]) == 'VB': #aString.startswith("hello")
        if (a[4]).startswith("VB"):    
            if tags.vb == '': #first word
                tags.vb = tags.vb + a[1] + ' '
                flag_vb = a[4]
            elif flag_vb == a[4]:
                tags.vb = tags.vb + a[1] + ' '    
        else:
            flag_vb = ''
            
        arg_words.append(a[1])
        tag_seq.append(a[4])
        
    tags.arg_words = arg_words
    tags.tag_seq = tag_seq
    tags.location=tags.location.rstrip()  # remove space at the end of the string
    tags.person=tags.person.rstrip()
    tags.organization=tags.organization.rstrip()
    tags.misc=tags.misc.rstrip()
    tags.nns=tags.nns.rstrip()
    tags.nn=tags.nn.rstrip()
    tags.nnp=tags.nnp.rstrip()
    tags.nnps=tags.nnps.rstrip()
    tags.noun=tags.noun.rstrip()
    tags.prp=tags.prp.rstrip()
    tags.vb=tags.vb.rstrip()
      
    return tags
        

def getArgs(argsList):
    args = []
    checkTags = []
    tag = []
    bieWords = ''      # a[0]       , a[1]       , a[2]                   a[3], a[4]
    for a in argsList: # [srl.wordid, srl.srlword, srl.srlresult[column], ner, tag]
        s = re.search('([Ss])-[Aa][0-9]', a[2])
        bie = re.search('([BIE]|[bie])-[Aa][0-9]', a[2])
        my = re.match('([Mm]y)', a[1])
        I = re.match('([Ii]$)', a[1])
        me = re.match('([Mm]e$)', a[1])
        if my is not None and a[4] == 'PRP$':
            a[1] = 'your'
        if (I is not None or me is not None) and a[4] == 'PRP':
            a[1] = 'you'
        if s is not None:
            s_group = s.group(0) #ex: S-A0
            s_arg = re.split('-', s_group)[1] #ex: A0
            args.append([s_arg, a[1]])
            checkTags.append(a) #store the value of a in checkTags list
            tag.append(getTags(s_arg, checkTags)) #call function getTags to check  ner and pos tags and store it in 'tag' list
            checkTags = [] # reset the content of checkTags list
        if bie is not None:
            bieWords = bieWords + a[1] + ' '
            bie_group = bie.group(0) #ex: B-A1
            bie_0 = re.split('-', bie_group)[0] #ex: B
            bie_1 = re.split('-', bie_group)[1] #ex: A1
            checkTags.append(a) #store the value of a in checkTags list
            if bie_0 == 'E' or bie_0 == 'e':
                args.append([bie_1, bieWords])
                bieWords = ''
                tag.append(getTags(bie_1, checkTags)) #call function getTags to check  ner and pos tags and store it in 'tag' list
                checkTags = [] # reset the content of checkTags list
    return args, tag

def getArgMs(argMsList):
    argMs = []
    for a in argMsList: # [srl.wordid, srl.srlword, srl.srlresult[column]]
        bie = re.search('([BIE]|[bie])-[Aa][Mm]-(ADV|adv|LOC|loc|MNR|mnr|TMP|tmp)', a[2])
        if bie is not None:
            argMs.append(a[1])
    return argMs

def checkWordsInArgM(inputWord): #TODO: hapus, gak perlu
    firstWordtoDel = 0
    if len(inputWord) > 0:
        whi = re.search('[W|w]hile', inputWord[0])
        into = re.search('[I|i]nto', inputWord[0])
        to = re.search('[T|t]o', inputWord[0])
        aas = re.match('[A|a]s', inputWord[0])
        if (whi is not None) or (into is not None) or (to is not None) or (aas is not None):
            firstWordtoDel = 1
    return firstWordtoDel
               

def getAux(argument_0):
    aux = ''
                         # a[0]       , a[1]       , a[2]                   a[3], a[4]
    for a in argument_0: # [srl.wordid, srl.srlword, srl.srlresult[column], ner, tag]
        s = re.search('([Ss])-[Aa][0-9]', a[2])
        bie = re.search('([BIE]|[bie])-[Aa][0-9]', a[2])
        if s is not None:
            I = re.match('([Ii]$)', a[1])
            you = re.match('([Yy]ou$)', a[1])
            we = re.match('([Ww]e$)', a[1])
            they = re.match('([Tt]hey$)', a[1])
            she = re.match('([Ss][Hh][Ee]$)', a[1])
            he = re.match('([Hh]e$)', a[1])
            it = re.match('([Ii]t$)', a[1])                        
            if (I is not None) or (you is not None) or (we is not None) or (they is not None) :
                aux = 'do'
            elif (she is not None) or (he is not None) or (it is not None):
                aux = 'does'
            elif a[4] == 'NN':
                aux = 'does'
            elif a[4] == 'NNS':
                aux = 'do'
        if bie is not None:
            if a[4] == 'NN':
                aux = 'does'
            elif a[4] == 'NNS':
                aux = 'do'
    return aux

def clean_preposition(argument_x_words):
    argument_x_words.split(' ', 1)
    return argument_x_words.split(' ', 1)[1]

def item_no_comma(argument_x_words):
    s=re.search(r'([^,|.|!|?|;|:]+)', argument_x_words)
    s=s.group()
    return s  

def get_pronoun(prp):
    she = re.match('([Ss]he$)', prp)
    he = re.match('([Hh]e$)', prp)
    my = re.match('([Mm]y)', prp)
    I = re.match('([Ii]$)', prp)
    me = re.match('([Mm]e$)', prp)
    if my is not None:
        prp = 'your'
    elif (I is not None or me is not None):
        prp = 'you'
    elif she is not None: 
        prp = 'her'
    elif he is not None:
        prp = 'him'
    return prp

def checkTemplate(srlObjectList): #input: sentenceListForQA[i] or sentenceList[i] 
    columnLen = len((srlObjectList[0]).srlresult)
    column = 0
    qa = []
    qa_result = []
    
    if columnLen == 0: # if there are no SRL results
        argument = []
        argTags = [] # to store ner and pos tags for objects with empty Args (no SRL results)
        item_qa = ''
        aux = ''
        sentence_nosrl = []
        
        for srl in srlObjectList:
            argument.append([srl.wordid, srl.srlword, srl.wordid, srl.ner, srl.tag, srl.pos]) # here index 2 (the second srl.wordid) is dummy (just to fill the parameter)
            
        argTags = getTags('NO-ARG', argument) # get pos and ner tag
        if argTags.location != '':
            qa.append (['Which part of ' +  argTags.location + '?','WHC2'])
            qa.append (['How is the weather in ' + argTags.location + '?','HOW4'])

        elif argTags.organization != '':
            qa.append (['Where is ' +  argTags.organization + ' located?','WHR2'])
        elif argTags.misc != '':
            qa.append (['What do you know about ' +  argTags.misc + '?','WHT1'])
        elif argTags.noun != '':
            qa.append(['Which ' + argTags.noun + ' do you like?','WHC1']) 
        elif seq_in_seq (['PRP','VBP','DT'] , argTags.tag_seq) == True: #example:I am a...
            qa.append(['How do you like that so far?','DEF4'])
        elif seq_in_seq(['PRP','VBP','NN'] , argTags.tag_seq) == True or seq_in_seq(['PRP','VBP','NNS'] , argTags.tag_seq) == True:
            sentence_nosrl.append ([1,argTags.prp, 'S-A0','' ,'PRP']) # [srl.wordid, srl.srlword, srl.srlresult[column], ner, tag]
            aux = getAux(sentence_nosrl)
            prp = get_pronoun(argTags.prp)
            if seq_in_seq(['PRP','VBP','NNS'] , argTags.tag_seq) == True or seq_in_seq(['PRP','VBP','NN'] , argTags.tag_seq) == True:
                qa.append(['Why '+ aux + ' ' + prp + ' ' + argTags.vb + ' ' + argTags.noun+ '?','WHY3'])

        else:
            qa.append(['Could you tell me more?', 'DEF2'])
    
    else: #if there are SRL results   
        for column in range(columnLen):
            V = ''
            Vtag = ''
            vList = []
            argument = []
            argument_0 = []
            argument_1 = []
            aux = 'does'
            modifierAdverbials = []
            modifierLocatives = []
            modifierDirectional = []
            modifierManner = []
            modifierTemporal = []
            modifierModals = []
            modifierNegation = []
            modifierModal = []
            #modifierCause = []
            #modifierPurpose = []
            #modifierOrdered = ''
            ArgM_ADV = ''
            ArgM_LOC = ''
            ArgM_MNR = ''
            ArgM_TMP = ''
            ArgM_MOD = ''
            ArgM_CAU = ''
            ArgM_PNC = ''
            #ArgM_DIR = ''
            arg_sequence = []
            ner_sequence = []
            pos_sequence = [] 
            a1_pos_sequence = []
            aux = ''
            
            try:
                for srl in srlObjectList:
                    if srl.srlresult[column] != 'O': #  take the existing srl result
                        checkVerb = re.search('-[Vv]', srl.srlresult[column])
                        checkArgs = re.search('-[Aa][0-9]', srl.srlresult[column])
                        checkArgMs_ADV = re.search('-[Aa][Dd][Vv]', srl.srlresult[column])
                        checkArgMs_LOC = re.search('-[Ll][Oo][Cc]', srl.srlresult[column])
                        checkArgMs_MNR = re.search('-[Mm][Nn][Rr]', srl.srlresult[column])
                        checkArgMs_TMP = re.search('-[Tt][Mm][Pp]', srl.srlresult[column])
                        checkArgMs_MOD = re.search('-[Mm][Oo][Dd]', srl.srlresult[column]) 
                        checkArgMs_CAU = re.search('-[Cc][Aa][Uu]', srl.srlresult[column]) 
                        checkArgMs_PNC = re.search('-[Pp][Nn][Cc]', srl.srlresult[column])
                        checkArgMs_DIR = re.search('-[Dd][Ii][Rr]', srl.srlresult[column])
                        checkArgMs_NEG = re.search('-[Nn][Ee][Gg]', srl.srlresult[column])
                        checkArgMs_MOD = re.search('-[Mm][Oo][Dd]', srl.srlresult[column])
                        if checkVerb is not None:
                            vList.append([srl.wordid, srl.srlword, srl.srlresult[column], srl.lemma, srl.ner, srl.tag, srl.pos])
                            arg_sequence.append('V')
                        if checkArgs is not None:
                            argument.append([srl.wordid, srl.srlword, srl.srlresult[column], srl.ner, srl.tag, srl.pos])
                            arg_sequence.append(checkArgs.group()[1:]) # ex result: A0 ([1:]-> remove the first character)
                            if (checkArgs.group()[1:]) == 'A1':
                                argument_1.append([srl.wordid, srl.srlword, srl.srlresult[column], srl.ner, srl.tag, srl.pos])
                                a1_pos_sequence.append(srl.pos)
                            if (checkArgs.group()[1:]) == 'A0':
                                argument_0.append([srl.wordid, srl.srlword, srl.srlresult[column], srl.ner, srl.tag, srl.pos])
                        if checkArgMs_ADV is not None:
                            modifierAdverbials.append([srl.wordid, srl.srlword, srl.srlresult[column]])
                            arg_sequence.append('AM-ADV')
                        if checkArgMs_LOC is not None:
                            modifierLocatives.append([srl.wordid, srl.srlword, srl.srlresult[column], srl.ner, srl.tag, srl.pos])
                            arg_sequence.append('AM-LOC')
                        if checkArgMs_MNR is not None:
                            modifierManner.append([srl.wordid, srl.srlword, srl.srlresult[column]])
                            arg_sequence.append('AM-MNR')
                        if checkArgMs_TMP is not None:
                            modifierTemporal.append([srl.wordid, srl.srlword, srl.srlresult[column], srl.ner, srl.tag, srl.pos])
                            arg_sequence.append('AM-TMP')
                        if checkArgMs_MOD is not None:
                            modifierModals.append([srl.wordid, srl.srlword, srl.srlresult[column]])
                            arg_sequence.append('AM-MOD')
                        if checkArgMs_CAU is not None:
                            #modifierCause.append([srl.wordid, srl.srlword, srl.srlresult[column]])
                            arg_sequence.append('AM-CAU')
                        if checkArgMs_PNC is not None:
                            #modifierPurpose.append([srl.wordid, srl.srlword, srl.srlresult[column]])
                            arg_sequence.append('AM-PNC')
                        if checkArgMs_DIR is not None:
                            modifierDirectional.append([srl.wordid, srl.srlword, srl.srlresult[column], srl.ner, srl.tag, srl.pos])
                            arg_sequence.append('AM-DIR')
                        if checkArgMs_NEG is not None:
                            modifierNegation.append([srl.wordid, srl.srlword, srl.srlresult[column], srl.ner, srl.tag, srl.pos])
                            arg_sequence.append('AM-NEG')
                        if checkArgMs_MOD is not None:
                            arg_sequence.append('AM-MOD')
                    ner_sequence.append(srl.ner)
                    pos_sequence.append(srl.tag)
                    # debug
                    #print(pos_sequence)
                argumentOrdered = [] # to store arg 0..9
                argTags = [] # to store ner and pos tags from arg 0...
                amlocTag = [] # to store ner and pos tags from AM-LOC
                amtmpTag = [] # to store ner and pos tags from AM-TMP
                amdirTag = []
                if len(vList) > 0:
                    Vtag = str(vList[0][5])
                    if len(vList) > 1:
                        V = getV(vList)
                    if len(vList) ==1:
                        V = str(vList[0][1])
                        #Vlemma = str (vList[0][3])
                    if len(argument) > 0:
                        argumentOrdered, argTags = getArgs(argument) # a list consists of argument number + argument words
                    if len(modifierAdverbials) > 0:
                        modifierOrderedAdverbials = getArgMs(modifierAdverbials) # list contains only the words 
                        # some kind of syntax / discourse cues improvements (on the next few lines): #
                        ArgM_ADV_firstWord = '' #
                        ArgM_ADV_restOfWords = '' #
                        firstWordtoDel_ADV = checkWordsInArgM(modifierOrderedAdverbials) #
                        if firstWordtoDel_ADV == 1: #
                            ArgM_ADV_firstWord = modifierOrderedAdverbials[0] #
                            count = 0 #
                            for n in modifierOrderedAdverbials: #
                                if count >= 1: #
                                    ArgM_ADV_restOfWords = ArgM_ADV_restOfWords + n + ' ' #
                                count = count + 1 #
                        for m in modifierOrderedAdverbials:
                            ArgM_ADV = ArgM_ADV + m + ' ' # str subclause from argm adv
                    if len(modifierLocatives) > 0:
                        amlocTag = getTags('AM-LOC', modifierLocatives) # get pos and ner tag for AM-LOC
                        modifierOrderedLocatives = getArgMs(modifierLocatives)
                        for m in modifierOrderedLocatives:
                            ArgM_LOC = ArgM_LOC + m + ' '
                    if len(modifierManner) > 0:
                        modifierOrderedManner = getArgMs(modifierManner)
                        for m in modifierOrderedManner:
                            ArgM_MNR = ArgM_MNR + m + ' '
                    if len(modifierTemporal) > 0:
                        amtmpTag = getTags('AM-TMP', modifierTemporal) # get pos and ner tag for AM-TMP
                        modifierOrderedTemporal = getArgMs(modifierTemporal) # a list of the modifier words
                        ArgM_TMP_firstWord = ''
                        ArgM_TMP_restOfWords = ''
                        firstWordtoDel_TMP = checkWordsInArgM(modifierOrderedTemporal)
                        if firstWordtoDel_TMP == 1:
                            ArgM_TMP_firstWord = modifierOrderedTemporal[0]
                            count = 0
                            for n in modifierOrderedTemporal:
                                if count >= 1:
                                    ArgM_TMP_restOfWords = ArgM_TMP_restOfWords + n + ' '
                                count = count + 1
                        for m in modifierOrderedTemporal:
                            ArgM_TMP = ArgM_TMP + m + ' '
                    if len(modifierModals) > 0:
                        ArgM_MOD = modifierModals[0][1]
                    if len(modifierDirectional) > 0:
                        amdirTag = getTags('AM-DIR', modifierDirectional) # get pos and ner tag for AM-DIR
                    if len(argument_0) > 0:
                        aux = getAux(argument_0)
            except (IndexError): # mismatch index between variable sentenceList (from Spacy) and sentenceListSRL (from SENNA)
                qa.append(['Can you elaborate?','DEF1']) # break and give default question 
                break
                
            try:
                #A0 = ''
                #A1 = ''
                #A2 = ''
                #A3 = ''
                i = 0
                c = 0
                #xx = ''
                Arg_0 = False
                Arg_1 = False
                Arg_2 = False
                Arg_3 = False
                Arg_4 = False
                item_qa = ''
                Arg_1_words = ''
                Arg_0_words = ''
                Arg_TMP_words = ''
                #question = ''
                #answer = ''
                #print argumentOrdered
                
                for ao in argumentOrdered: #loop per subclause in arg        
                    if argumentOrdered[c][0] == 'A0':
                        Arg_0 = True
                        Arg_0_words = str(argumentOrdered[c][1]).rstrip()
                    elif argumentOrdered[c][0] == 'A1':
                        Arg_1 = True
                        Arg_1_words = str(argumentOrdered[c][1]).rstrip() # remove spaces at the end of the string
                        Arg_1_words = re.sub(r'\s([?.,!"](?:\s|$))', r'\1', Arg_1_words) # remove spaces before punctuation
                    elif argumentOrdered[c][0] == 'A2':
                        Arg_2 = True
                    elif argumentOrdered[c][0] == 'A3':
                        Arg_3 = True
                    elif argumentOrdered[c][0] == 'A4':
                        Arg_4 = True
                    c = c + 1        
                    
                if seq_in_seq (['AM-NEG'] , arg_sequence) == False:
                    if len(argumentOrdered) > 1: # a list consists of a list; argument number + argument words
                        # making sure that the argumentOrdered is ordered, using the following loop: #
                        for passnum in range(len(argumentOrdered)-1,0,-1): #start, stop[, step]
                            for i in range(passnum): #
                                if int(argumentOrdered[i][0][1]) > int(argumentOrdered[i+1][0][1]): #nested list, accessing argument's number
                                    temp = argumentOrdered[i] #
                                    argumentOrdered[i] = argumentOrdered[i+1] #
                                    argumentOrdered[i+1] = temp #   
                        doubleSameArgs = 0
                        countArg = 0
                        for ao in argumentOrdered:
                            if countArg > 0:
                                if ao[0] == prevArg:
                                    doubleSameArgs = 1
                            prevArg = ao[0]
                            countArg = countArg + 1
                        
                        if doublewhSameArgs == 0: # there should be no same arguments in a clause, there should be only 1 A0, 1 A1, 1 A2, etc.
                        
                            if Arg_1 == True:
                                for tag in argTags:
                                    if tag.arg == 'A1':
                                        if tag.location != '':  
                                            qa.append (['Where in ' + tag.location + '?','WHR3']) # Where is [A1 loc]?
                                        elif tag.organization != '':
                                            qa.append (['What is ' + tag.organization + '?', 'WHT2'])
                                        if Arg_0 == True and ArgM_LOC == ''  and tag.location == '' and tag.organization == '' and seq_in_seq (['LOC'] , ner_sequence) == False and seq_in_seq (['GPE'] , ner_sequence) == False: # if ArgM_LOC is empty
                                            if tag.tag_seq[0] == 'TO' and tag.vb != '':
                                                if Vtag == 'VBD' or Vtag == 'VBN':
                                                    qa.append (['Where did ' + Arg_0_words + ' ' + getLemma(V) + ' ' + item_no_comma (Arg_1_words) + '?','WHR4'])
                                                elif Vtag == 'VBP' or Vtag == 'VBZ' or Vtag == 'VBG' or Vtag == 'VB':
                                                    qa.append (['Where ' + aux + ' ' + Arg_0_words + ' ' + getLemma(V) + ' ' + item_no_comma (Arg_1_words) + '?','WHR4'])
                                        if tag.tag_seq[0] == 'NNS': # if first word in A1 is plural                                    
                                            if ArgM_MNR == '':
                                                qa.append(['What kind of ' + tag.noun + '?','WKD4']) # [A1 NNS1]
                                        if tag.tag_seq[0] == 'NN' and tag.noun != '': # if first word is a noun single
                                            qa.append(['What kind of ' + tag.noun + '?','WKD1'])
                                        if len(tag.tag_seq) > 1:
                                            if tag.tag_seq[0] == 'DT' and tag.tag_seq[1] == 'NNS': # preceded by a determinant
                                                qa.append(['Which ' + tag.noun + ' do you like?','WHC3'])
                                        if ArgM_TMP == '': # to avoid temporal noun. ex: a year, some weeks
                                            if seq_in_seq (['CD','NNS'] , tag.tag_seq) == True and len(tag.tag_seq) < 3:
                                                qa.append(['What kind of ' + tag.noun + '?','WKD2'])
                                            elif seq_in_seq (['DT','NNS'], tag.tag_seq) == True and len(tag.tag_seq) < 3:
                                                qa.append(['What kind of ' + tag.noun + '?','WKD3'])
                                            if len(tag.tag_seq) > 1:
                                                if tag.tag_seq[0] == 'IN' and tag.tag_seq[1] == 'NNS': # ex: to festivals
                                                    qa.append(['What kind of ' + tag.noun + '?','WKD6'])
                                                elif tag.tag_seq[0] == 'IN' and tag.tag_seq[1] == 'NN':
                                                    qa.append(['What kind of ' + tag.noun + '?','WKD5'])
                                        if seq_in_seq (['AM-PNC'] , arg_sequence) == False and seq_in_seq (['AM-CAU'] , arg_sequence) == False:
                                            if tag.tag_seq[0] == 'VBG': 
                                                qa.append(['Why are you ' + item_no_comma(Arg_1_words) + '?', 'WHY2']) 
                                            else:
                                                if Arg_0 == True and (Vtag == 'VBD' or Vtag == 'VBN') and seq_in_seq (['VERB'] , a1_pos_sequence) == False:
                                                    qa.append (['Why did ' + Arg_0_words + ' ' + getLemma(V) + ' ' + item_no_comma(Arg_1_words) + '?','WHY4'])
                                                elif Arg_0 == True and (Vtag == 'VBP' or Vtag == 'VBZ' or Vtag == 'VBG' or Vtag == 'VB') and seq_in_seq (['VERB'] , a1_pos_sequence) == False:
                                                    qa.append (['Why ' + aux + ' ' + Arg_0_words + ' ' + getLemma(V) + ' ' + item_no_comma(Arg_1_words) + '?','WHY4'])
                                        if seq_in_seq (['AM-TMP','V','A1'] , arg_sequence) == True and Vtag == 'VBD': #if len(argumentordered) > 1 and ArgM_TMP has something and ArgTMP is followed by V
                                            if Arg_0 == True:
                                                qa.append(['When did ' + Arg_0_words + ' '+ getLemma(V) + ' ' + Arg_1_words + '?', 'WHN1']) 
                                        
                                        if Arg_0 == True and Arg_2 == False and Arg_3 == False and Arg_4 == False:                                        
                                            if seq_in_seq (['AM-MNR'] , arg_sequence) == False and seq_in_seq (['AM-DIS'] , arg_sequence) == False:
                                                if (Vtag == 'VBD' or Vtag == 'VBN') and seq_in_seq (['VERB'] , a1_pos_sequence) == False:
                                                    qa.append(['How did ' + Arg_0_words + ' ' + getLemma(V) + ' ' + item_no_comma(Arg_1_words) + '?','HOW3'])
                                                elif (Vtag == 'VBP' or Vtag == 'VBZ' or Vtag == 'VBG' or Vtag == 'VB') and seq_in_seq (['VERB'] , a1_pos_sequence) == False:
                                                    qa.append(['How ' + aux + ' ' + Arg_0_words + ' ' + getLemma(V) + ' ' + item_no_comma(Arg_1_words) + '?','HOW3'])
                                            if seq_in_seq (['AM-ADV','V'] , arg_sequence) == True and seq_in_seq (['AM-TMP'] , arg_sequence) == False:
                                                if (Vtag == 'VBD' or Vtag == 'VBN'):
                                                    qa.append(['When did ' + Arg_0_words + ' ' + getLemma(V) + ' ' + item_no_comma(Arg_1_words) + '?','WHN3'])
                                                elif (Vtag == 'VBP' or Vtag == 'VBZ' or Vtag == 'VBG' or Vtag == 'VB'):
                                                    qa.append(['When ' + aux + ' ' + Arg_0_words + ' ' + getLemma(V) + ' ' + item_no_comma(Arg_1_words) + '?','WHN3'])
                                    else: #there is A1, but current tag is not A1 nor A0
                                        if tag.location != '': 
                                            qa.append (['What do you think about ' + tag.location + '?','WHT4'])
                                        
                            if seq_in_seq (['AM-LOC'] , arg_sequence)  == True: # arg > 1, has AM-LOC
                                if amlocTag.location != '':                            
                                    item_qa = 'Where in ' +  amlocTag.location + '?' # Where in [AM-LOC -lpp]? # or: Which part of LOC?
                                    qa.append ([item_qa,'WHR5'])
    
                            elif Arg_1 == False: # no arg1, no AM-LOC
                                if tag.arg != 'A0':
                                    for tag in argTags:
                                        if tag.location != '':  
                                            qa.append (['Which part of ' + tag.location + '?','WHC4']) # Where is [A1 loc]?
                                        elif seq_in_seq (['IN','NNP'] , tag.tag_seq) == True: #ex: to HBS 
                                            qa.append (['Where is ' + tag.nnp + '?','WHR1'])
                                        elif seq_in_seq (['IN','NNPS'] , tag.tag_seq) == True: 
                                             qa.append (['What do you think about ' + tag.nnps + '?','WHT9'])
                            else: 
                                if tag.arg != 'A0' and tag.arg != 'A1':
                                    for tag in argTags:
                                        if tag.location == '':  
                                            if Vtag == 'VBD' or Vtag == 'VBN':
                                                qa.append(['How was it?','DEF5']) 
                          
                    elif len(argumentOrdered) == 1:
                        #if ArgM_LOC != '': # if there is ArgM_LOC
                        if seq_in_seq (['AM-LOC'] , arg_sequence) == True:
                            if amlocTag.location != '': # if there is LOC ner
                                qa.append (['Where in ' +  amlocTag.location + '?','WHR6'])
                            else:
                                qa.append(['Is that a good or a bad thing?','DEF6'])
    
                        elif argTags[0].organization != '':
                            qa.append (['What is ' + argTags[0].organization + '?', 'WHT3'])
                        elif seq_in_seq (['AM-DIR'] , arg_sequence) == True: 
                            if amdirTag.location != '': # if there is LOC ner
                                qa.append (['What do you think about ' + amdirTag.location + '?', 'WHT5'])
                        
                                                    
                                
                        if Arg_0 == True:
                            if seq_in_seq (['AM-ADV'] , arg_sequence) == False and seq_in_seq (['AM-LOC'] , arg_sequence) == False and ArgM_MNR == '' and seq_in_seq (['AM-TMP'] , arg_sequence) == False and seq_in_seq (['AM-MOD'] , arg_sequence) == False: # if other argms are empty
                                item_qa = 'Where ' + aux + ' ' + Arg_0_words + ' ' + getLemma(V) + '?'  
                            #elif seq_in_seq (['A0','V','AM-TMP'] , arg_sequence) == True: #ArgM_TMP != '': # if there is ArgM_TMP
                            #    if Vtag == 'VBD' or Vtag == 'VBN':
                            #        qa.append(['How did ' + Arg_0_words + ' ' + getLemma(V) + ' ' + ArgM_TMP + '?', 'HOW1']) 
                            #    elif Vtag == 'VBP' or Vtag == 'VBZ' or Vtag == 'VBG':
                            #        qa.append(['How ' + aux + ' ' + Arg_0_words + ' ' + getLemma(V) + ' ' + ArgM_TMP + '?', 'HOW2'])
                        elif Arg_1 == True:
                            if argTags[0].tag_seq[0] == 'IN' and ('PRP' not in argTags[0].tag_seq) :
                                qa.append(['Why do you ' + getLemma(V) + ' ' +  item_no_comma(Arg_1_words) + '?','WHY1'])
                                
                    elif len(argumentOrdered) == 0:
                        if seq_in_seq (['AM-LOC'] , arg_sequence) == True and seq_in_seq (['AM-TMP'], arg_sequence) == False: # if there is ArgM_LOC
                            if amlocTag.location == '': # but no LOC ner
                                if Vtag == 'VBD' or Vtag == 'VBN':
                                    qa.append(['When was that?','WHN4'])
                        elif seq_in_seq (['AM-ADV'] , arg_sequence) == True or seq_in_seq (['AM-TMP'] , arg_sequence) == True:
                            if Vtag == 'VBD' or Vtag == 'VBN' :
                                qa.append(['How was it?','DEF8'])
                            if Vtag == 'VBP' or Vtag == 'VBZ' or Vtag == 'VBG' or Vtag == 'VB':
                                qa.append(['How is it?','DEF8'])
                
                else: # AM-NEG ==True    
                    if Arg_1_words == '' or Arg_0_words == '' :
                        argumentOrdered, argTags = getArgs(argument)
                        if argumentOrdered[0][0] == 'A0':
                            Arg_0_words = str(argumentOrdered[0][1]).rstrip()
                            aux = getAux(argument_0) 
                        elif argumentOrdered[0][0] == 'A1':
                            Arg_1_words = str(argumentOrdered[0][1]).rstrip()
                            aux = getAux(argument_1)                        
                    if seq_in_seq (['AM-MOD'] , arg_sequence) == True:
                        if ArgM_MOD == '':
                            ArgM_MOD = modifierModals[0][1]
                        
                    if seq_in_seq (['AM-MOD'] , arg_sequence) == True:
                        if seq_in_seq (['A0'] , arg_sequence) == True and seq_in_seq (['A1'] , arg_sequence) == False and seq_in_seq (['AM-PNC'] , arg_sequence) == False  and seq_in_seq (['AM-CAU'] , arg_sequence) == False:
                            if ArgM_MOD == 'can':
                                qa.append (['Why '+ ArgM_MOD + '\'t '  +  Arg_0_words + '?','NEG3'])
                            else:
                                qa.append (['Why '+ ArgM_MOD + 'n\'t '  +  Arg_0_words + '?','NEG3'])
                        elif seq_in_seq (['A0'] , arg_sequence) == False and seq_in_seq (['A1'] , arg_sequence) == True and seq_in_seq (['AM-PNC'] , arg_sequence) == False  and seq_in_seq (['AM-CAU'] , arg_sequence) == False:
                            if ArgM_MOD == 'can':
                                qa.append (['Why '+ ArgM_MOD + '\'t '  +  Arg_1_words + '?','NEG4'])
                            else:
                                qa.append (['Why '+ ArgM_MOD + 'n\'t '  +  Arg_1_words + '?','NEG4'])
                        elif seq_in_seq (['A0'] , arg_sequence) == True and seq_in_seq (['A1'] , arg_sequence) == True and seq_in_seq (['AM-PNC'] , arg_sequence) == False  and seq_in_seq (['AM-CAU'] , arg_sequence) == False:
                            if ArgM_MOD == 'can':
                                qa.append (['Why '+ ArgM_MOD + '\'t '  +  Arg_0_words + ' ' + getLemma(V) + ' ' + Arg_1_words +  '?','NEG5'])
                            else:
                                qa.append (['Why '+ ArgM_MOD + 'n\'t '  +  Arg_0_words + ' ' + getLemma(V) + ' ' + Arg_1_words + '?','NEG5'])
                    else:
                        if seq_in_seq (['A0'] , arg_sequence) == True and seq_in_seq (['A1'] , arg_sequence) == True and seq_in_seq (['AM-PNC'] , arg_sequence) == False  and seq_in_seq (['AM-CAU'] , arg_sequence) == False: 
                            if Vtag == 'VBD' or Vtag == 'VBN':
                                qa.append (['Why didn\'t '  +  Arg_0_words + ' ' + getLemma(V) + ' ' + Arg_1_words + '?','NEG1'])
                            elif Vtag == 'VBP' or Vtag == 'VBZ' or Vtag == 'VBG'  or Vtag == 'VB':
                                qa.append (['Why ' + aux + 'n\'t '  + Arg_0_words + ' ' + getLemma(V) + ' ' + Arg_1_words + '?','NEG1'])
                        elif seq_in_seq (['A0'] , arg_sequence) == False and seq_in_seq (['A1'] , arg_sequence) == True and seq_in_seq (['AM-PNC'] , arg_sequence) == False  and seq_in_seq (['AM-CAU'] , arg_sequence) == False: 

                            if seq_in_seq (['PRP', 'VBD'] , pos_sequence) == True or seq_in_seq (['PRP', 'VBN'] , pos_sequence) == True:
                                qa.append (['Why did' + 'n\'t ' + Arg_1_words + '?','NEG2'])
                            elif seq_in_seq (['PRP', 'VBP'] , pos_sequence) == True or seq_in_seq (['PRP', 'VBZ'] , pos_sequence) == True or seq_in_seq (['PRP', 'VBZ'] , pos_sequence) == True or seq_in_seq (['PRP', 'VB'] , pos_sequence) == True:
                                qa.append (['Why ' + aux + 'n\'t '  + Arg_1_words + '?','NEG2'])
                        elif seq_in_seq (['A0'] , arg_sequence) == True and seq_in_seq (['A1'] , arg_sequence) == False and seq_in_seq (['AM-PNC'] , arg_sequence) == False  and seq_in_seq (['AM-CAU'] , arg_sequence) == False: 

                            if seq_in_seq (['PRP', 'VBD'] , pos_sequence) == True or seq_in_seq (['PRP', 'VBN'] , pos_sequence) == True:
                                qa.append (['Why did' + 'n\'t ' + Arg_0_words + '?','NEG2'])
                            elif seq_in_seq (['PRP', 'VBP'] , pos_sequence) == True or seq_in_seq (['PRP', 'VBZ'] , pos_sequence) == True or seq_in_seq (['PRP', 'VBZ'] , pos_sequence) == True or seq_in_seq (['PRP', 'VB'] , pos_sequence) == True:
                                qa.append (['Why ' + aux + 'n\'t '  + Arg_0_words + '?','NEG2'])

            except:
                foo = 'bar'
                
    if len(qa) == 0:
        argument = []
        for srl in srlObjectList:
            argument.append([srl.wordid, srl.srlword, srl.wordid, srl.ner, srl.tag, srl.pos]) # here index 2 (the second srl.wordid) is dummy (just to fill the parameter)
            
        argTags = getTags('RAND-ARG', argument) # get pos and ner tag
        if argTags.location != '':
            qa.append (['What do you think about ' +  argTags.location + '?','WHT6'])
        elif argTags.person != '':
            qa.append (['Who is ' +  argTags.person + '?','WHO2'])
        elif argTags.organization != '':
            qa.append (['Where is ' +  argTags.organization + ' located?','WHR7'])
        elif argTags.misc != '':
            qa.append (['What do you know about ' +  argTags.misc + '?','WHT7'])
        elif argTags.nnp != '':
            qa.append (['What do you think about ' +  argTags.nnp + '?','WHT8'])
        elif Arg_0 == True:
            #if Vtag == 'VBP':
                #qa.append ([aux + ' ' + Arg_0_words + '?','IST1'])
            if Vtag == 'VBD':
                qa.append (['Did ' + Arg_0_words+ '?','IST1'])
            else:
                qa.append(['How is that going for you?','DEF7'])
        else:
            qa.append(['Can you elaborate?','DEF3'])
        
    qa_result = [list(i) for i in set(map(tuple, qa))]    # remove duplicate list 

    return qa_result
            
def writeQA(sentenceQAList, sentenceText, number, QAroot):
    sentence = ET.SubElement(QAroot, 'sentence')
    sentence.set('number', str(number + 1))
    statement = ET.SubElement(sentence, 'statement')
    statement.text = sentenceText
    for aPair in sentenceQAList:
        question = ET.SubElement(sentence, 'question')
        question.set('template',aPair[1])
        question.text = aPair[0]


"""
Create the Semantic Representation/Annotation
"""


def create_SR(PreprocessedInputFile):

    sentenceList = [] # a list for the SemanticRepresentation objects

    with open(PreprocessedInputFile) as f:
        dlines = f.read().splitlines() #reading a file without newlines
        
    #Now try to parse the text:
    #print ('Getting POS and NER tag for the sentence(s)...')
    #len_dlines = len(dlines)
    count_dlines = 1    
    
    
    for l in dlines:
        if l != '\n': # if not an empty line
            tokenized_text = inputTokenize(l)
            theID = 0
            semList = []
            for token in tokenized_text:
                sem = SemanticRepresentation()
                #print (token)            
                sem.wordid = theID
                sem.word = token.text
                sem.tokenindex = (token.i)+1 #because spacy token starts from 0
                sem.lemma = token.lemma_
                sem.ner = token.ent_type_
                sem.pos = token.pos_
                sem.tag = token.tag_
                semList.append(sem)
                theID = theID + 1
            sentenceList.append(semList)
            count_dlines = count_dlines + 1
            
            
    #print ('Getting the semantic role labels...')
    sentenceListSRL = getSRL()
        
    # fill in the class SemanticRepresentation()
    i = 0
    if len(sentenceList) == len(sentenceListSRL):
        while i < len(sentenceList):
            for sr in sentenceList[i]:
                for fsro in sentenceListSRL[i]:
                    #fsro content: [1, 'Alice', '-', ['B-A1']]
                    #print ('fsro[0] == int(sr.tokenindex) and fsro[1] == sr.depword', fsro[0], sr.tokenindex, fsro[1], sr.word)
                    if fsro[0] == int(sr.tokenindex):
                        sr.srlword = sr.word
                        sr.srlmainverb = fsro[2]
                        sr.srlresult = fsro[3]
            i = i + 1
    
    return sentenceList, dlines


"""
Generate the questions
"""

def generate_questions (sentenceList, dlines):
    QAroot = ET.Element('sentences')
    QAroot.set('version', '1.0')
    
    sentenceQAList = []
    listOfAllGeneratedQA = []
    for i in range(len(sentenceList)): 
        sentenceText = '' #gak perlu kalo gak nulis xml
        sentenceText = dlines[i]
        
        #for debug purpose
        if i == 211:
            print('')
        
            
        sentenceQAList = checkTemplate(sentenceList[i])
        if len(sentenceQAList) == 0:
            print (sentenceText)
        listOfAllGeneratedQA.append(sentenceQAList)
        try:
            writeQA(sentenceQAList, sentenceText, i, QAroot)
        except:
            print ('Failed to write the QA XML for:', sentenceText)
            
    xml = ET.tostring(QAroot,encoding='utf8', pretty_print=True)
    fp = open("generated_qa.xml", "wb")
    fp.write(xml)
    fp.close()
    #print ('Statement and follow-up question pairs are successfully generated.')
            
    return listOfAllGeneratedQA


   

###################################### Running the program for training ########################################
workPath = os.getcwd()
output_file = '/senna/output.txt'
TRAINING = False
TESTING = False

if TRAINING:
    import preprocess as pp
    import runSENNA as rs
            
    
    input_file = 'input-evaluation-1.txt'
    input_path = workPath + '/senna/' + input_file
    senna_input_file = 'input_preprocess.txt' 
    senna_input_path = workPath + '/senna/' + senna_input_file
    
    pp.preprocess_senna_input (input_path, senna_input_path) # input is transformed into senna_input (preprocessed & tokenized)
    rs.runSENNA(senna_input_file)
    
    sentenceList, dlines = create_SR(senna_input_path)
    listOfAllGeneratedQA = generate_questions (sentenceList, dlines)


    
    
if TESTING:
    import random
    import preprocess as pp
    import runSENNA as rs
    
    workPath = os.getcwd()
    input_file = 'input.txt'
    input_path = workPath + '/senna/' + input_file
    senna_input_file = 'input_preprocess.txt' 
    senna_input_path = workPath + '/senna/' + senna_input_file
    
    workPath = os.getcwd()
    starter_questions = workPath+'/starters.txt'
    with open(starter_questions) as f:
        dlines = f.read().splitlines() #reading a file without newlines
    
    # display starter question:    
    print(random.choice(dlines))
    
    # ask for answer
    statement = input("Enter an answer: \n")
    
    # write to input file        
    with open(input_path, 'w') as f:
        f.write("%s\n" % statement)
        
    pp.preprocess_senna_input (input_path, senna_input_path) # input is transformed into senna_input (preprocessed & tokenized)
    rs.runSENNA(senna_input_file)
    
    # getting semantic representation
    sentenceList, dlines = create_SR(senna_input_path)
    
    listOfAllGeneratedQA = []
    # generate the questions
    listOfAllGeneratedQA = generate_questions (sentenceList, dlines)
    
    #print(random.choice(listOfAllGeneratedQA[0])[0])
    for q in listOfAllGeneratedQA[0]:
        print(q)    