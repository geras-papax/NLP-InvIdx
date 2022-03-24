from os import link
import mysql.connector
import nltk
from nltk.stem import WordNetLemmatizer
import csv
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
import string
from xml.dom import minidom

# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')
wordnet_lemmatizer =WordNetLemmatizer()

#connect to database
mydb = mysql.connector.connect(
    host="localhost",
    user="******",
    passwd="******",
    database="newscrawler",
    auth_plugin='mysql_native_password'
    )
mycursor = mydb.cursor()
#pos tags every article and stores the tags into csv for each article
def postag():

    #getting each articles text
    mycursor.execute("SELECT idarticles,content FROM articles")
    myresult = mycursor.fetchall()

    for x in myresult:
        id = x[0]
        fname = 'article'+str(id)
        my_file = Path('part1\Inverted_Index\Tagged\%s.csv' %fname)
        #only new articles
        if not my_file.is_file():
            #preprocess the text
            x = ''.join(x[1])
            x = x.lower()
            trans = str.maketrans('', '', string.punctuation)
            x = x.translate(trans)
            #tokenize the text
            tokens = nltk.word_tokenize(x)
            #tagging the parts
            tagged = nltk.pos_tag(tokens)
            # opening the csv file in 'w+' mode
            with open('part1\Inverted_Index\Tagged\%s.csv' %fname, 'w+', newline ='', encoding='utf-8') as file:    
                write = csv.writer(file)
                write.writerows(tagged)
#creating inverted index xml and returning all the words for the duration test
def inv_idx():

    closed_tags=['CD','CC','DT','EX','IN','LS','MD','PDT','POS',
    'PRP','PRP$','RP','TO','UH','WDT','WP','WP$','WRB']
    clr_articles = []
    clean_text= []
    id= []
    #getting every csv
    for path in sorted(Path("part1\Inverted_Index\Tagged").iterdir()):
        #if exists
        num=""
        if path.is_file():
            #getting articles parse order
            for s in list(str(path)): 
                if s.isdigit():
                    num= num+s
            id.append(num)
            #cleaning from stopwords
            cleaned_text = ""
            df = pd.read_csv(path, header= None)
            for index, data in df.iterrows():
                if data[1] not in closed_tags:
                   cleaned_text += wordnet_lemmatizer.lemmatize(data[0]) + " "
            clr_articles.append(cleaned_text)
    #counting words' frequency
    countv = CountVectorizer()
    cvect = countv.fit_transform(clr_articles)
    #tfid vectorizing text
    tfid = TfidfTransformer()
    Y = tfid.fit_transform(cvect)
    docvectors = Y.toarray()
    docvectors = docvectors.T
    words = countv.get_feature_names()
    #creating xml
    root = minidom.Document()
    xml = root.createElement('inverted_index')
    root.appendChild(xml)
    for index, word in enumerate(countv.get_feature_names()):
        lemmaChild = root.createElement('lemma')
        lemmaChild.setAttribute('name', word)
        xml.appendChild(lemmaChild)
        for docId, weight in enumerate(docvectors[index]):
            if weight > 0:
                docChild = root.createElement('document')
                docChild.setAttribute('id', id[docId])
                docChild.setAttribute('weight', str(weight))
                lemmaChild.appendChild(docChild)

    xml_str = root.toprettyxml() 
    save_path_file = "part1\Inverted_Index\invIdx.xml"
    
    with open(save_path_file, "w", encoding="utf-8") as f:
        f.write(xml_str)
    return words 
#parses xml and returns the article ids and weight
def queryInvIdx(query):
    xml = minidom.parse('part1\Inverted_Index\invIdx.xml')
    docId= []
    query = query.split()
    #searching in xml for each word in query
    for word in query:
        tagname= xml.getElementsByTagName('lemma')
        for lemma in tagname:
            if lemma.attributes['name'].value == wordnet_lemmatizer.lemmatize(word):
                for doc in lemma.getElementsByTagName('document'):
                    Id = int(doc.attributes['id'].value)
                    weight = float(doc.attributes['weight'].value)
                    docId.append([Id,weight])
    docpd = pd.DataFrame(docId, columns =['DocId', 'Weight'])
    #recalculating the weights according to the length of the query
    docpd['Weight'] = docpd['Weight'] / len(query)
    docpd = docpd.groupby(['DocId']).sum().sort_values(by=['Weight'], ascending=False)
    return docpd.reset_index()
#prints the links of given ids from the database
def getlinks(ids):
    query="""SELECT link FROM articles WHERE idarticles = %s """
    for id in ids:
        mycursor.execute(query, (int(str(id)[1:]),))
        myresult = mycursor.fetchall()
        link = "".join(myresult[0])
        print(link)

