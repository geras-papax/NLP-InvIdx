from Inverted_Index import functions
import random
import time
import matplotlib.pyplot as plt
# from WebCrawler import dailymailWebCrawler
# from WebCrawler import nbcWebCrawler

# functions.postag()
# functions.inv_idx()

print("-----------------------------------")
print("CHOOSE: \n1->QUERY\n2->TEST")
print("-----------------------------------")
input1= input()

if input1 == '1':
    print("-----------------------------------")
    print('INSERT YOUR QUERY')
    print("-----------------------------------")
    input2= input()
    print("-----------------------------------")
    res = functions.queryInvIdx(input2)
    functions.getlinks(res['DocId'].values.tolist())
elif input1 == '2':
    words= functions.inv_idx()
    start_time = time.time()
    for i in range(20):
        query= ' '
        query = '' + query.join(random.sample(words, 1))
        functions.queryInvIdx(query)
    time1 = (time.time() - start_time)/20
    start_time = time.time()
    for i in range(20):
        query= ' '
        query = '' + query.join(random.sample(words, 2))
        functions.queryInvIdx(query)
    time2 = (time.time() - start_time)/20
    start_time = time.time()
    for i in range(30):
        query= ' '
        query = '' + query.join(random.sample(words, 3))
        functions.queryInvIdx(query)
    time3 = (time.time() - start_time)/30
    start_time = time.time()
    for i in range(30):
        query= ' '
        query = '' + query.join(random.sample(words, 4))
        functions.queryInvIdx(query)
    time4 = (time.time() - start_time)/30
    
    names = ['1 Word', '2 Words', '3 Words', '4 Words']
    values = [time1, time2, time3, time4]

    plt.plot(names, values)
    plt.ylabel('Seconds')
    plt.show()