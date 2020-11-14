import random
import numpy as np
import scipy
import csv
import random 
import nltk 

# nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from scipy import spatial
from sklearn. feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from math import log10
# nltk.download('wordnet')




class chatbot():
    username = ["Name"]
    greeting = ["hello", "hi", "hey", "hola", "g'day"]
    change = ["call me ", "change my name to ", "set my name to "] 
    data = []
    smallTalk = {   
                "how are you":["I am fine, thank you." , "Excellent!", "Never been better"], 
                "how old are you":["10 days old", " 10 days young!", "I have only been created for 10 days"],
                "how is the weather": ["It is raining cats and dogs!", "It is now 15'C"],
                "what is your gender" :["I don't have a specific gender", "I am a BOT!"],
                "what can you do" :["I can answer your question", "Try me!"],
                "what is my name" :["your name is " ]
                }

    def __init__(self):
        print("Hello! Welcome!")
        self.getData()
        self.getName()
        
    
    def getData(self):
        with open('testset.csv', encoding='utf8') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                # print(row)
                if row  and row[3] != 'Document':
                    self.data.append([row[1].lower(), row[2], row[3]])

    def getName(self):
        userinput = str(input('What is your Name?')) 
    
        while userinput == "" or userinput == None:
            userinput = str(input('What is your Name?')) 

        self.username[0] = userinput.split()[-1]
        self.botGreeting()

    def changeName(self, newName):
        self.username[0] = newName
        print(f"I have change your name to {self.username[0].capitalize()}")

    def responseName(self, sentence):
        print(sentence.capitalize(), self.username[0])

    def botGreeting(self):
        print(f"{random.choice(self.greeting).capitalize()}, {self.username[0].capitalize()}. Nice to meet you!")
                

    def getSimilarity(self, list1):
        countVect = CountVectorizer().fit_transform(list1)
        similarity = cosine_similarity(countVect[-1], countVect)

        return similarity.flatten()


    def searchQuestion(self, input1):
        questionList = [element[0] for element in self.data]
        questionList.append(input1)
       
        similarityScores = self.getSimilarity(questionList)
        # print("Searching question:", max(similarityScores[:-1]))

        index = self.indexSort(similarityScores)
        questionFound = questionList[index[0]]

        if max(similarityScores[:-1]) < 0.45:
            if self.errorMsg(questionFound):
                self.searchAnswer(questionFound, input1)
            else:
                print("Sorry I can't help you with this")
        else:
            self.searchAnswer(questionFound, input1)
            # return questionFound
    

    def searchAnswer(self, question, input1):
        ansList = [element[1] for element in self.data if element[0] == question]
        ansList.append(input1)
        
        similarityScores = self.getSimilarity(ansList)
        # print(similarityScores)
        index = self.indexSort(similarityScores)
        # index = index[1:]
        ansFound = ansList[index[0]]

        # print(ansFound)
        # self.response(ansFound)
        print(ansFound)


    def indexSort(self, array):
        length = len(array)
        indexList = list(range(0, length))

        x = array
        for i in range(length):
            for j in range(length):
                if x[indexList[i]] > x[indexList[j]]:
                    temp = indexList[i]
                    indexList[i] = indexList[j]
                    indexList[j] = temp

        return indexList[1:]



    def Talk(self, query):
        talk = False
        smallTalkList = [element for element in self.smallTalk.keys()]
        greetingList = self.greeting.copy()
        greetingList.append(query)
        # print(greetingList)
        smallTalkList.append(query)
        # print(smallTalkList)

        smallTalkScores = self.getSimilarity(smallTalkList)
        smallTalkIndex = self.indexSort(smallTalkScores)

        greetingScores = self.getSimilarity(greetingList)
        # print(greetingScores)
        # print(max(smallTalkScores[:-1]))

        if max(greetingScores[:-1]) < 0.1 and max(smallTalkScores[:-1]) < 0.1:
            talk = False
        elif max(greetingScores[:-1]) > max(smallTalkScores[:-1]):
            self.botGreeting()
            # print("greeted")
            talk = True
        else:
            smallTalkFound = smallTalkList[smallTalkIndex[0]]
            if max(smallTalkScores[:-1]) < 0.7:
                if not self.errorMsg(smallTalkFound):
                    talk = False
            elif smallTalkFound == "what is my name":
                # print("my name")
                self.responseName(self.smallTalk["what is my name"][0])
                talk = True
            else:
                print(random.choice(self.smallTalk[smallTalkFound]))
                talk = True

        if talk:
            return True
        else:
            return False

    def errorMsg(self, alternative):
        print("I'm sorry, I don't understand your question.")
        print("Do you mean [" ,alternative, "?] (y/n)")
        userInput = input()

        if userInput.lower() == 'y' or userInput.lower() == 'yes':
            return True
        else:
            return False

        
    def userIntent(self, query):
        usrInput = query.lower()
        talk = False

        changename = self.change.copy()
        changename.append(usrInput)
        similarity = self.getSimilarity(changename)

        if max(similarity[:-1]) > 0.5:
            print(usrInput)
            self.changeName(usrInput.split()[-1])
            talk = True

        elif self.Talk(usrInput):
            talk = True

        if talk == False:
            self.searchQuestion(usrInput)

    
        


if __name__ == "__main__":
    print("in main function")
    bot = chatbot()
    run  = True
    # print(bot.searchQuestion("old"))
    while run: 
        print("in while")
        # bot.getName()
        userInput = input()
        if userInput.lower() == "quit":
            run = False
            print("Good Bye")
        else:
            bot.userIntent(userInput)


        # print(f"you typed {userInput}")

    # bot.changeName("Alex")
    
