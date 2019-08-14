#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 21:19:57 2019

@author: ym
gui from - http://code.activestate.com/recipes/580757-chatbox-megawidget-for-tkinter/
"""

import datetime
import collections
import pandas as pd

try:
    from Tkinter import StringVar, IntVar, Text, Frame, PanedWindow, Scrollbar, Label, Entry, Radiobutton, Button, Canvas
    from Tkconstants import *
    import ttk
except ImportError:
    from tkinter import StringVar, IntVar, Text, Frame, PanedWindow, Scrollbar, Label, Entry, Radiobutton, Button, Canvas
    from tkinter.constants import *
    import tkinter.ttk as ttk
    from tkinter.messagebox import showinfo, showwarning, OK
    from tkinter import font  as tkfont
    
import os
import random
import preprocess as pp
import runSENNA as rs
import fqg

workPath = os.getcwd()
input_file = 'input.txt'
input_path = workPath + '/senna/' + input_file
senna_input_file = 'input_preprocess.txt' 
senna_input_path = workPath + '/senna/' + senna_input_file
starter_questions = workPath+'/starters.txt'

User_Message = collections.namedtuple('User_Message', 'nick content')
Notification_Message = collections.namedtuple('Notification_Message', 'content tag')
Notification_Message.__new__.__defaults__ = ('notification',)

Notification_Of_Private_Message = collections.namedtuple('Notification_Message', 'content from_ to')
"%Y-%m-%d %H:%M:%S"
counter_question_global = 1
flag_press_enter = False
flag_continue = False
flag_close = False
counter_enter_global = 0
#maximum_counter = 10

class Chatbox(object):
    
    def __init__(self, master, my_nick=None, command=None, topic=None, entry_controls=None, maximum_lines=None, timestamp_template=None, scrollbar_background=None, scrollbar_troughcolor=None, history_background=None, history_font=None, history_padx=None, history_pady=None, history_width=None, entry_font=None, entry_background=None, entry_foreground=None, label_template=u"{nick}", label_font=None, logging_file='log.txt', tags=None):
        self._master = master
        self.interior = Frame(master, class_="Chatbox")

        self._command = command

        self._is_empty = True

        self._maximum_lines = maximum_lines
        self._timestamp_template = timestamp_template
        
        self._command = command

        self._label_template = label_template
        
        self._logging_file = logging_file
        
        if logging_file is None:
            self._log = None
        else:
            try:
                self._log = open(logging_file, "a")
            except:
                self._log = None
        
        ####    INSTRUCTION: 
        
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold")
        self.content_font = tkfont.Font(family='Helvetica', size=13) 
        self.instruction_font = tkfont.Font(family='Courier', size=13) 
        
        instruction_label_frame = Frame(self.interior, class_="Instruction_label")
        instruction_label_frame.pack(fill=X)
        
        self._label_instruction = Label(instruction_label_frame, text="INSTRUCTIONS", font=self.title_font)
        self._label_instruction.pack(side=LEFT)
        
        instruction_frame = Frame(self.interior, class_="Instruction")
        instruction_frame.pack(fill=X)
        
         
        self._text_instruction = Text(instruction_frame, height = 13, borderwidth=2, relief="groove", font=self.instruction_font)
        self._text_instruction.pack(fill=X, side=LEFT, expand=True)
        quote = """1. Read the question.
2. Fill your answer  
   Please answer in a COMPLETE SENTENCE, not just keywords.    
   
   Example:
   Good:                                          Bad:
   Question: What kind of food do you like?       Question: What kind of food do you like?
   Reply: I like spicy food.                      Reply: spicy food.
   
   If you are reluctant to answer the question, click "Next Dialogue" button to go to the next question.
3. press Enter to submit your answer. 
4. Rate the reply question in the Evaluation section
5. Click "Next Dialogue" button at the bottom to continue. """
        self._text_instruction.insert (END, quote)   
        
        counter_frame = Frame(self.interior)
        counter_frame.pack(fill=X)
        
        global counter_question
        counter_question = StringVar()
        counter_question.set(str(1))
        
        Label(counter_frame, text="").pack(side = 'top', anchor = 'w')
        self._label_counter_1 = Label(counter_frame, text="DIALOGUE", font=self.title_font).pack(side=LEFT)
        self._label_counter_2 = Label(counter_frame, textvariable=counter_question, font=self.title_font).pack(side=LEFT)
        self._label_counter_3 = Label(counter_frame, text="OF 10 ", font=self.title_font).pack(side=LEFT)
               
        
        ####     MESSAGE DISPLAY AREA:
          
        
        top_frame = Frame(self.interior, class_="Top")
        top_frame.pack(expand=True, fill=BOTH) # True: the widget is expanded to fill any extra space, BOTH: fill X&Y
        
        self._textarea = Text(top_frame, height = 1, borderwidth=2, relief="groove", state=DISABLED, font=self.content_font)

        self._vsb = Scrollbar(top_frame, takefocus=0, command=self._textarea.yview)
        self._vsb.pack(side=RIGHT, fill=Y) #scroll bar di kanan, sepanjang sumbu Y

        self._textarea.pack(side=RIGHT, expand=YES, fill=BOTH)
        self._textarea.insert (END, '\n')
        self._textarea["yscrollcommand"]=self._vsb.set # text area tempat display chat
        
        
        ####     MESSAGE ENTRY:
        
        entry_frame = Frame(self.interior, class_="Chatbox_Entry")
        entry_frame.pack(fill=X, anchor=N) # fill=X: make all widgets as wide as parent widget, anchor=N: place the text at the top 
        
        #self.var_entry = StringVar()
        
        if entry_controls is not None:
            controls_frame = Frame(entry_frame, class_="Controls")
            controls_frame.pack(fill=X)
            entry_controls(controls_frame, chatbox=self)
            
            bottom_of_entry_frame = Frame(entry_frame)
            self._entry_label = Label(bottom_of_entry_frame)
            self._entry = Entry(bottom_of_entry_frame) #,textvariable=self.var_entry
        else:            
            self._entry_label = Label(entry_frame)
            self._entry = Entry(entry_frame) #, width = 70, textvariable=self.var_entry
        
        
        self._entry.pack(side=LEFT, fill = X, expand=YES)
        self._entry.bind("<Return>", self._on_message_sent) # when user press enter in the chatbox, call on_message_sent
        self._entry.focus()
        
        
        #self._buttonmessage = Button(entry_frame, text="Submit", width = 20, command=self._on_message_sent)
        #self._buttonmessage.bind("<Button-1>", self._on_message_sent) # bind the action of the left button of your mouse to the button assuming your primary click button is the left one.
        #self._buttonmessage.pack(side=LEFT)
        
        ####
        
        label_evaluation = Frame(self.interior)
        label_evaluation.pack(fill=X, anchor=N)
        
        Label(label_evaluation, text="").pack(side='top', anchor='w')
        Label(label_evaluation, text="EVALUATION", font=self.title_font).pack(side='top', anchor='w')
        Label(label_evaluation, text="Please indicate how strongly you agree or disagree with all the following statements.").pack(side='top', anchor='w')
        #Label(label_evaluation, text="").pack(side='top', anchor='w')
        
        ####    QUESTIONNAIRES:    
        
        ''' Questionnaire frame'''
        
        question_frame = Frame(self.interior)
        #question_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        #question_frame.columnconfigure(0, weight=1)
        #question_frame.rowconfigure(0, weight=1)
        #self.configure(background="white")
        question_frame.pack()
            
        self.var_q1 = IntVar()
        self.var_q2 = IntVar()
        self.var_q3 = IntVar()
        self.var_q4 = IntVar()
        self.var_q1.set(0) # none selected        
        self.var_q2.set(0) # none selected
        self.var_q3.set(0) # none selected
        self.var_q4.set(0) # none selected
        
        #Label(question_frame, text="").grid(column=0, row=0, sticky="W")
        #Label(question_frame, text="EVALUATION", font=self.title_font).grid(column=0, row=1, sticky="W")
        
        
        Label(question_frame, text="Strongly disagree").grid(column=1, row=3, padx=4)
        Label(question_frame, text="Disagree").grid(column=2, row=3, padx=4)
        Label(question_frame, text="Neither agree nor disagree").grid(column=3, row=3, padx=4)
        Label(question_frame, text="Agree").grid(column=4, row=3, padx=4)
        Label(question_frame, text="Strongly agree").grid(column=5, row=3, padx=4)
        
        Label(question_frame,  text="The grammar of the reply question is correct").grid(column=0, row=4, sticky="W")
        Radiobutton(question_frame,  variable=self.var_q1, value=1).grid(column=1, row=4)        
        Radiobutton(question_frame,  variable=self.var_q1, value=2).grid(column=2, row=4)        
        Radiobutton(question_frame,  variable=self.var_q1, value=3).grid(column=3, row=4)        
        Radiobutton(question_frame,  variable=self.var_q1, value=4).grid(column=4, row=4)
        Radiobutton(question_frame,  variable=self.var_q1, value=5).grid(column=5, row=4)
        
        Label(question_frame,  text="The reply question is appropriate to be asked \nin a conversation", justify=LEFT).grid(column=0, row=5, sticky="W")
        Radiobutton(question_frame,  variable=self.var_q2, value=1).grid(column=1, row=5)        
        Radiobutton(question_frame,  variable=self.var_q2, value=2).grid(column=2, row=5)        
        Radiobutton(question_frame,  variable=self.var_q2, value=3).grid(column=3, row=5)        
        Radiobutton(question_frame,  variable=self.var_q2, value=4).grid(column=4, row=5)
        Radiobutton(question_frame,  variable=self.var_q2, value=5).grid(column=5, row=5)
        
        Label(question_frame,  text="The reply question is related to my answer").grid(column=0, row=6, sticky="W")
        Radiobutton(question_frame,  variable=self.var_q3, value=1).grid(column=1, row=6)        
        Radiobutton(question_frame,  variable=self.var_q3, value=2).grid(column=2, row=6)        
        Radiobutton(question_frame,  variable=self.var_q3, value=3).grid(column=3, row=6)        
        Radiobutton(question_frame,  variable=self.var_q3, value=4).grid(column=4, row=6)
        Radiobutton(question_frame,  variable=self.var_q3, value=5).grid(column=5, row=6)
        
        Label(question_frame,  text="The dialogue as a whole feels natural").grid(column=0, row=7, sticky="W")
        Radiobutton(question_frame,  variable=self.var_q4, value=1).grid(column=1, row=7)        
        Radiobutton(question_frame,  variable=self.var_q4, value=2).grid(column=2, row=7)        
        Radiobutton(question_frame,  variable=self.var_q4, value=3).grid(column=3, row=7)        
        Radiobutton(question_frame,  variable=self.var_q4, value=4).grid(column=4, row=7)
        Radiobutton(question_frame,  variable=self.var_q4, value=5).grid(column=5, row=7)
        
        
        #E1 = Entry(question_frame)
        
        ####    NEXT QUESTIONS BUTTON:
        button_next = Frame(self.interior, class_="Evaluation_3")
        button_next.pack(fill=X, anchor=N)
        
        Label(button_next, text="").pack(side='top', anchor='w')
        Label(button_next, text="Please give your comment here.\nFor example, give the reason why do you think the reply question is not appropriate, \nincorrect grammar, not related to your answer, or why it does not feel natural.", justify=LEFT).pack(side='top', anchor='w')
        
        self.var_comment = StringVar()
        self.E1 = Entry(button_next, textvariable=self.var_comment)
        self.E1.pack(side='top', anchor='w', expand=YES, fill = X)
        Label(button_next, text="").pack()
        
        #button
        self._button_next = Button(button_next, text="Next Dialogue >>", command=self._on_click_next, width = 50)
        self._button_next.pack()
        
        ####
        
        if history_background:
            self._textarea.configure(background=history_background)
        
        if history_font:
            self._textarea.configure(font=history_font)

        if history_padx:
             self._textarea.configure(padx=history_padx)
             
        if history_width:
             self._textarea.configure(width=history_width)

        if history_pady:
            self._textarea.configure(pady=history_pady)

        if scrollbar_background:
            self._vsb.configure(background = scrollbar_background)

        if scrollbar_troughcolor:
            self._vsb.configure(troughcolor = scrollbar_troughcolor)

        if entry_font:
            self._entry.configure(font=entry_font)

        if entry_background:
            self._entry.configure(background=entry_background)
            
        if entry_foreground:
            self._entry.configure(foreground=entry_foreground)
        
        if label_font:
            self._entry_label.configure(font=label_font)

        if tags:
            for tag, tag_config in tags.items():
                self._textarea.tag_config(tag, **tag_config)
                
        self.set_nick(my_nick)

    @property
    def topic(self):
        return
        
    @topic.setter
    def topic(self, topic):
        return
        
    def focus_entry(self):
        self._entry.focus()

    def bind_entry(self, event, handler):
        self._entry.bind(event, handler)
        
    def bind_textarea(self, event, handler):
        self._textarea.bind(event, handler)
        
    def bind_tag(self, tagName, sequence, func, add=None):
        self._textarea.tag_bind(tagName, sequence, func, add=add) 
        
    def focus(self):
        self._entry.focus()

    def user_message(self, nick, content):
        if self._timestamp_template is None:
            self._write((u"%s:"%nick, "nick"), " ", (content, "user_message"))
        else:
            timestamp = datetime.datetime.now().strftime(self._timestamp_template)
            self._write((timestamp, "timestamp"), " ", (u"%s:"%nick, "nick"), " ", (content, "user_message"))

    def notification_message(self, content, tag=None):
        if tag is None:
            tag = "notification"

        self._write((content, tag))
        
    notification = notification_message
    
    def notification_of_private_message(self, content, from_, to):
        if self._timestamp_template is None:
            self.notification_message(u"{from_} -> {to}: {content}".format(from_=from_, to=to, content=content), "notification_of_private_message")
        else:
            timestamp = datetime.datetime.now().strftime(self._timestamp_template)
            self.notification_message(u"{timestamp} {from_} -> {to}: {content}".format(timestamp=timestamp, from_=from_, to=to, content=content), "notification_of_private_message")
        
    def new_message(self, message):
        if isinstance(message, User_Message):
            self.user_message(message.content, message.nick)
        elif isinstance(message, Notification_Message):
            self.notification(message.content, message.tag)
        elif isinstance(message, Notification_Of_Private_Message):
            self.notification_of_private_message(message.from_, message.to, message.content)
        else:
            raise Exception("Bad message")

    def tag(self, tag_name, **kwargs):
        self._textarea.tag_config(tag_name, **kwargs)

    def clear(self):
        self._is_empty = True
        self._textarea.delete('1.0', END)

    @property
    def logging_file(self):
        return self._logging_file

    def send(self, content):
        if self._my_nick is None:
            raise Exception("Nick not set")

        self.user_message(self._my_nick, content)

    def _filter_text(self, text):
        return "".join(ch for ch in text if ch <= u"\uFFFF")
    
    def _write(self, *args):
        if len(args) == 0: return
            
        relative_position_of_scrollbar = self._vsb.get()[1]
        
        self._textarea.config(state=NORMAL)
        
        if self._is_empty:
            self._is_empty = False
        else:
            self._textarea.insert(END, "\n")
            if self._log is not None:
                self._log.write("\n")

        for arg in args:
            if isinstance(arg, tuple):
                text, tag = arg
                        # Parsing not allowed characters
                text = self._filter_text(text)
                self._textarea.insert(END, text, tag)
            else:
                text = arg

                text = self._filter_text(text)
                self._textarea.insert(END, text)
            
            if self._log is not None:
                self._log.write(text)

        if self._maximum_lines is not None:
            start_line = int(self._textarea.index('end-1c').split('.')[0]) -self._maximum_lines 
            
            if lines_to_delete >= 1:
                self._textarea.delete('%s.0'%start_line, END)

        self._textarea.config(state=DISABLED)
        
        if relative_position_of_scrollbar == 1:
            self._textarea.yview_moveto(1)

    def _on_message_sent(self, event):
        
        if not self._entry.get(): # or not self.var_entry.get()
            showwarning('Empty answer', 'Please fill your anwer')
        else:            
            #  update flag press enter
            global flag_press_enter
            global counter_enter_global
            
            if flag_press_enter == False:
                flag_press_enter = True
                #counter_enter += 1
            
            if flag_press_enter == True:
                if counter_enter_global < 2:
                    
                    counter_enter_global +=1
                
                    # get the input from user
                    #print("var_entry:",self.var_entry.get())
                    message = self._entry.get() 
                    # clear entry
                    self._entry.delete(0, END)
                    
                    self.send(message)
            
                    if self._command:
                        self._command(message) # display user input to the chat window
                    
                    
                
                    
            
                    if counter_enter_global > 1:
                        self._textarea.config(state=NORMAL)
                        self._textarea.insert(END, "\n[Thank you for your response. Continue to evaluate the Reply Question]")
                        self._textarea.config(state=DISABLED)
                    
                    else:
                        
                        ''' running the follow-up question generation '''
                        
                        with open(input_path, 'w') as f:
                            f.write("%s\n" % message)
                            
                        pp.preprocess_senna_input (input_path, senna_input_path)
                        rs.runSENNA(senna_input_file)
                
                        # getting semantic representation
                        sentenceList, dlines = fqg.create_SR(senna_input_path)
                
                        # generate the questions
                        listOfAllGeneratedQA = fqg.generate_questions (sentenceList, dlines)
                        print(listOfAllGeneratedQA)
                        
                        #reply_list = random.choice(listOfAllGeneratedQA[0])
                        reply = rs.ranking(listOfAllGeneratedQA)
                        
                        
                        if self._log is not None:
                            self._log.write("\nTemplate: %s" % listOfAllGeneratedQA)
                        #reply = reply_list[0]
                        print(reply)            
                        self.user_message("Reply question", reply)   
                
                else:
                    showinfo('Thank you','Thank you for your response. Please continue to evaluate the Reply Question')
                    self._entry.focus()
            
        
            
    def set_nick(self, my_nick):
        self._my_nick = my_nick

        if my_nick:
            text = self._label_template.format(nick=my_nick)

            self._entry_label["text"] = text
            self._entry_label.pack(side=LEFT,padx=(5,5), before=self._entry)
        else:
            self._entry_label.pack_forget()
            
    def _on_click_next (self):
        global flag_press_enter
        global counter_enter_global
        maximum_counter = 10
        
        if flag_press_enter == True and self.var_q1.get() != 0 and self.var_q2.get() != 0 and self.var_q3.get() != 0 and self.var_q4.get() != 0:
            global counter_question_global
            
            if self._log is not None:
                self._log.write("\nDialogue number: %s" % str(counter_question_global))
            
            # increase question counter
            counter_question_global += 1
            
            # write questionnaire's answers to log file
            if self._log is not None:
                self._log.write("\nQ1: %s" % self.var_q1.get())
                self._log.write("\nQ2: %s" % self.var_q2.get())
                self._log.write("\nQ3: %s" % self.var_q3.get())  
                self._log.write("\nQ3: %s" % self.var_q4.get())  
                self._log.write("\nComment: %s" % self.var_comment.get())                   
        
        #print ('debug: ',self.var_q1.get())
        if counter_question_global > maximum_counter:
            showinfo('Finish', 'Thank you for your participation! \nWe will now save your responses. \nPress OK to close the application.')
            if OK:
                self._master.destroy()
                global flag_close
                flag_close = True
        elif self.var_q1.get() == 0 and flag_press_enter == True:
            showinfo('Rate the evaluation', 'Please rate all evaluations.')
        elif self.var_q2.get() == 0 and flag_press_enter == True:
            showinfo('Rate the evaluation', 'Please rate all evaluations.')
        elif self.var_q3.get() == 0 and flag_press_enter == True:
            showinfo('Rate the evaluation', 'Please rate all evaluations.')
        elif self.var_q4.get() == 0 and flag_press_enter == True:
            showinfo('Rate the evaluation', 'Please rate all evaluations.')
        else:
            # clear chat area
            self._textarea.config(state=NORMAL)
            self._textarea.delete('1.0', END)
            self._textarea.config(state=DISABLED)
            
            # fill with new starter's question
            with open(starter_questions) as f:
                dlines = f.read().splitlines() #reading a file without newlines
            starter = (random.choice(dlines)) 
            self.user_message("Question", starter)
            
            # update question counter
            counter_question.set (str(counter_question_global))           
                        
             # reset
            flag_press_enter = False 
            counter_enter_global = 0
            self.var_q1.set(0) # questionnaire 1
            self.var_q2.set(0) # questionnaire 2
            self.var_q3.set(0) # questionnaire 3
            self.var_q4.set(0) # questionnaire 3
            self.E1.delete(0, END) # clear comment
            self._entry.delete(0, END) # clear entry message
  
class Consent(object):
    def __init__(self, master):
        self._master = master
        self.interior = Frame(master, class_="Consent")
        
        instruction_label_frame = Frame(self.interior, class_="Consent")
        instruction_label_frame.pack(fill=X)
        
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")        
        self._label_instruction = Label(instruction_label_frame, text="WELCOME!", font=self.title_font)
        self._label_instruction.pack()
        
        instruction_frame = Frame(self.interior, class_="Instruction")
        instruction_frame.pack(fill=X)

        self.content_font = tkfont.Font(family='Helvetica', size=14)  
        self._text_instruction = Text(instruction_frame, font=self.content_font, wrap=WORD) # wrap: to manage hypenation
        self._text_instruction.pack(fill=X, side=LEFT)
        quote = """You are invited to participate in a study of the development of a dialogue agent. You will be asked 10 casual conversation questions in total. After you answer each conversation's question, the system will generate a reply question. After that, the system will ask your opinion regarding the quality of reply question in a scale-based survey. There are no “right” or “wrong” answers; we just want to know what you think and feel about the system.

PARTICIPATION
Your participation in this study is voluntary. You may refuse to take part in the study or exit the study at any time without penalty. You are free to decline to answer any particular question in the conversation you do not wish to answer for any reason.

CONFIDENTIALITY
Your responses will be stored in an electronic format. Your responses to the conversation will be made anonymized in written materials resulting from the study. 

CONTACT
If you have questions at any time about the study or the procedures, you may contact me via e-mail at yanimandasari@student.utwente.nl.

By clicking the button below, you acknowledge that your participation in the study is voluntary, you are 18 years of age or older, fluent in English, and that you are aware that you may choose to terminate your participation in the study at any time and for any reason.

Thank you!"""
        self._text_instruction.insert (END, quote)   
        
        #button
        button_frame = Frame(self.interior, class_="Instruction")
        button_frame.pack(fill=X)
        
        self._button_next = Button(button_frame, text="I agree, begin the study", command=self.close_window, width = 50, font=self.content_font)
        self._button_next.pack()
        self._button_next = Button(button_frame, text="I disagree, I do not wish to participate", command=self.close_window2, width = 50, font=self.content_font)
        self._button_next.pack()
        
        
    def close_window (self):
        global flag_continue
        flag_continue = True
        self._master.destroy()
        
    def close_window2 (self):
        self._master.destroy()

class closing_comment():
    def __init__(self, master):
        self._master = master
        self.interior = Frame(master, class_="closing")
        
        instruction_label_frame = Frame(self.interior, class_="closing")
        instruction_label_frame.pack(fill=X)
        
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")        
        self.content_font = tkfont.Font(family='Helvetica', size=14)  
        self._label_instruction = Label(instruction_label_frame, text="Please give your overall comment to the system.", font=self.title_font)
        self._label_instruction.pack()      
        
        

        # entry form
        self.var_entry = StringVar()
        entry_frame = Frame(self.interior, class_="entry")
        entry_frame.pack(fill=X)
        
        self._entry_comment = Entry(entry_frame, width = 70, textvariable=self.var_entry)
        self._entry_comment.pack(side=LEFT, fill = 'both', expand=True)
        
        
        #button
        button_frame = Frame(self.interior, class_="Submit")
        button_frame.pack(fill=X)
        
        self._button_next = Button(button_frame, text="Submit", command=self.close_window, width = 50, font=self.content_font)
        self._button_next.pack()
        self._button_next.bind("<Button-1>", self._on_button_submit)
        self._button_next.focus()

        
    def close_window (self):
        self._master.destroy()
    
    def _on_button_submit(self, event):
        # get the input from user
        print("var_entry:",self.var_entry.get())
        
        _log = open("log.txt", "a")
        _log.write("\nClosing comment: %s" % self.var_entry.get())

    
        
if __name__ == "__main__":

    try:
        from Tkinter import Tk
    except ImportError:
        from tkinter import Tk
        
    # first window: consent form
    root = Tk()
    root.title("Follow-up Question Generation")
    
    consent_form = Consent(root)
    consent_form.interior.pack(expand=True, fill=BOTH)
    root.mainloop()
    
    # second window: main dialogue
    if flag_continue == True:
        root2 = Tk()
        root2.title("Follow-up Question Generation")
    
        def command(txt):
            print(txt)
        
        with open(starter_questions) as f:
            dlines = f.read().splitlines() #reading a file without newlines
        
        starter = (random.choice(dlines))    
    
        chatbox = Chatbox(root2, my_nick="Your answer", command=command)
        
        date_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if chatbox._log is not None:
                chatbox._log.write("\n\n######## Session: %s ########\n" % date_time)
        
        chatbox.user_message("Question", starter)
        
        
        #chatbox.send("Hi, you are welcome!")
        chatbox.interior.pack(expand=True, fill=BOTH)
     
        root2.mainloop()
    
    # third window: closing comment    
    if flag_continue == True:
        root3 = Tk()
        root3.title("Follow-up Question Generation")
        comment_form = closing_comment(root3)
        comment_form.interior.pack(expand=True, fill=BOTH)
        root3.mainloop()