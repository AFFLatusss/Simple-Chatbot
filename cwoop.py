import random
import numpy as np
import scipy
import csv
import nltk 
# nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.snowball import PorterStemmer
from scipy import spatial
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from math import log10
from termcolor import colored


class chatbot():
    username = ["Name"]
    greeting = ["hello", "hi", "hey", "hola", "g'day"]
    change = ["call me ", "change my name to ", "set my name to "] 
    smallTalk = {
                "who are you": ["I am your favorite chatbot", "Some people call me Jarvis", "Your friendly neighbourhood chat bot"],   
                "how are you":["I am fine, thank you." , "Excellent!", "Never been better"], 
                "how old are you":["10 days old", " 10 days young!", "I have only been created for 10 days"],
                "how is the weather": ["It is raining cats and dogs!", "It is now 15'C", "The weather is warm and cozy"],
                "what is your gender" :["I don't have a specific gender", "I am a BOT!"],
                "what is my name" :["your name is" ]
                }
    data = []
    question = []
    document = []

    def __init__(self):
        self.response("Hello! Welcome!" )
        self.getData()
        self.getName()
        
    
    def getData(self):
        with open('cw1Dataset.csv', encoding='utf8') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if row  and row[3] != 'Document':
                    self.data.append([row[1].lower(), row[2], row[3].lower()])
                    self.question.append(row[1].lower())
                    self.document.append(row[3].lower())

    def getName(self):
        print(colored("Bot: ",'red'), end="")

        userinput = str(input('What is your Name?') )
    
        while userinput == "" or userinput == None:
            userinput = str(input('What is your Name?')) 

        self.username[0] = userinput.split()[-1]
        self.botGreeting()

    def changeName(self, newName):
        self.username[0] = newName
        sentence = f"I have change your name to {self.username[0].capitalize()}"
        bot.response(sentence)

    def responseName(self, sentence):
        print("Bot: ", sentence.capitalize(), self.username[0])

    def botGreeting(self):
        self.response(f"{random.choice(self.greeting).capitalize()}, {self.username[0].capitalize()}. Nice to meet you!")
        

    def stem(self, doc):
        p_stemmer = PorterStemmer()

        analyzer = CountVectorizer().build_analyzer()
        return (p_stemmer.stem(w) for w in analyzer(doc))

    def getSimilarity(self, list1, stop=False):
        
        if stop:
            countVect = CountVectorizer(stop_words=stopwords.words('english')).fit_transform(list1)
        else:
            countVect = CountVectorizer().fit_transform(list1 )

        countVect = TfidfTransformer(use_idf=True, sublinear_tf=True).fit_transform(countVect)
        similarity = cosine_similarity(countVect[-1], countVect)

        return similarity.flatten()

    def startingSearch(self, input1):
        docList = self.document.copy()
        docList.append(input1)
        docSimilarity = self.getSimilarity(docList, stop=True)
        # print("max" ,max(docSimilarity[:-1]))

        docIndex = self.indexSort(docSimilarity[:-1])
        docFound = docList[docIndex[0]]

        qList = self.question.copy()
        qList.append(input1)
        qSimilarity = self.getSimilarity(qList)
        # qIndex = self.indexSort(qSimilarity)
        # qFound = qList[qIndex[0]]

        if max(docSimilarity[:-1]) < 0.3 and max(qSimilarity[:-1]) < 0.3:
            self.response("Sorry, I am not able to answer this at the moment")
            return False
        elif max(docSimilarity[:-1]) > 0.5:
            
            ansSim, ansFound = self.searchAnswer(input1, doc=docFound)
            if ansSim > 0.25:
                self.response(ansFound)
            else:    
                self.searchQuestion(input1, doc=docFound)
        else:
            self.searchQuestion(input1)

    # def searchDocument(self, input1):
    #     documentList = self.document.copy()
    #     # [element[2] for element in self.data]
    #     documentList.append(input1)

    #     documentSimilarity = self.getSimilarity(documentList)

    #     index = self.indexSort(documentSimilarity)
    #     document = documentList[index[0]]

        # print("Document Found:", document, "Similarity Score:", max(documentSimilarity[:-1]))

    def searchQuestion(self, input1, doc=False):
        if doc:
            questionList =[element[0] for element in self.data if element[2] == doc]
            print("form doc")
        else:
            questionList = self.question.copy()

        questionList.append(input1)
        
        similarityScores = self.getSimilarity(questionList)
        index = self.indexSort(similarityScores[:-1])

        questionFound = questionList[index[0]]

        # print("SimilarityScores: ", max(similarityScores[:-1]))
        if max(similarityScores[:-1]) < 0.35:
            self.response("Sorry, I am not able to answer this at the moment")
            return False

        elif max(similarityScores[:-1]) < 0.5:
            if self.errorMsg(questionFound):
                self.searchAnswer(input1, questionFound)
            else:
                self.response("Sorry I can't help you with this")
                #newly added
                return False
        else:
            self.searchAnswer(input1,questionFound)
            return questionFound
    

    def searchAnswer(self, input1, question=False, doc=False):
        if question:
            print("Qget:", question)
            ansList = [element[1] for element in self.data if element[0] == question]
        else:
            ansList = [element[1] for element in self.data if element[2] == doc]

        # print(ansList)
        ansList.append(input1)
        
        similarityScores = self.getSimilarity(ansList, stop=True)
        # print("Ans:" ,similarityScores)
        index = self.indexSort(similarityScores[:-1])
        # index = index[1:]
        ansFound = ansList[index[0]]

        # print(ansFound)
        if doc:
            return max(similarityScores[:-1]), ansFound
        else:
            bot.response(ansFound)


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
        return indexList



    def Talk(self, query):
        talk = True
        proceed = True
        smallTalkList = [element for element in self.smallTalk.keys()]
        greetingList = self.greeting.copy()
        greetingList.append(query)
        smallTalkList.append(query)

        smallTalkScores = self.getSimilarity(smallTalkList)
        smallTalkIndex = self.indexSort(smallTalkScores[:-1])

        greetingScores = self.getSimilarity(greetingList)


        if max(greetingScores[:-1]) < 0.4 and max(smallTalkScores[:-1]) < 0.4:
            talk = False
        elif max(greetingScores[:-1]) > max(smallTalkScores[:-1]):
            self.botGreeting()
        else:
            smallTalkFound = smallTalkList[smallTalkIndex[0]]
            # print("Talk:",max(smallTalkScores[:-1]))
            if max(smallTalkScores[:-1]) < 0.65:
                if not self.errorMsg(smallTalkFound):
                    talk = False
                    proceed = False
                
            if (talk == True and proceed == True) and smallTalkFound == "what is my name":
                self.responseName(self.smallTalk["what is my name"][0])
            elif talk:
                bot.response(random.choice(self.smallTalk[smallTalkFound]))
                

        return talk

    def errorMsg(self, alternative):
        self.response("I'm sorry, I don't quite understand your question.")
        self.response(f"Do you mean [{alternative}?] (y/n)")
        print(f"{bot.username[0].capitalize()}: ",end ="")
        userInput = input()

        if userInput.lower() == 'y' or userInput.lower() == 'yes':
            print("input yes")
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

            self.changeName(usrInput.split()[-1])
            talk = True
        elif self.Talk(usrInput):
            talk = True

        if talk == False :
            self.startingSearch(usrInput)



    # self.searchDocument(usrInput)
    # self.searchQuestion(usrInput)
    def response(self, output):
        # print("Bot: ",output)
        print(colored("Bot: ",'red'), end="")

        print(output)


    

    
    

if __name__ == "__main__":
    bot = chatbot()
    run  = True
    bot.response("What can I help you with?")
    # print(colored(f"{bot.username[0]}:", 'blue'), end="")
    # a = input()
    while run: 
        # print(colored(f"{bot.username[0].capitalize()}:", 'blue'), end="")
        print(f"{bot.username[0].capitalize()}:",end="")

        userInput = input()

        if userInput.lower() == "quit":
            run = False
            print("Good Bye")
        else:
            bot.userIntent(userInput)
            
        bot.response("What else can I help you with?")
