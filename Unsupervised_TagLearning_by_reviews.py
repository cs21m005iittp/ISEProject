import os
import pathlib
import re

from matplotlib import pyplot as plt
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import glob
import string
import spacy
from sklearn import metrics
from scipy import spatial

nlp = spacy.load('en_core_web_lg')

import numpy as np

k=0
def embed(tokens, nlp):
    """Return the centroid of the embeddings for the given tokens.

    Out-of-vocabulary tokens are cast aside. Stop words are also
    discarded. An array of 0s is returned if none of the tokens
    are valid.

    """

    lexemes = (nlp.vocab[token] for token in tokens)

    vectors = np.asarray([
        lexeme.vector
        for lexeme in lexemes
        if lexeme.has_vector
        and not lexeme.is_stop
        and len(lexeme.text) > 1
    ])

    if len(vectors) > 0:
        centroid = vectors.mean(axis=0)
    else:
        width = nlp.meta['vectors']['width']  # typically 300
        centroid = np.zeros(width)

    return centroid


def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.replace('\n', ' ')
    text = ' '.join(text.split())  # remove multiple whitespaces
    return text

path = r"C:/Users/UTKARSHA/OneDrive/Desktop/reviews/*.csv"


labels = []


label_names = ['bug', 'performance', 'negative', 'positive','security','login','features', 'addictive']#,'high pricing']


for file in glob.glob(path):
    doc = []
    df = pd.read_csv(file)
    comment = (df["Comment"])
    #print(comment)
    for i in range(len(comment)):

        # passing this text one by one for cleaning then to nearest neibour for closest label
        if(isinstance((comment[i]),str)): #checking whether comment is text format or not
            print("comment ", i, "= ", (comment[i]))
            cleaned_comment = clean_text(comment[i])
            tokens = cleaned_comment.split(' ')  # working on seperate comment
            centroid = embed(tokens, nlp)

            print(centroid[:10], centroid.shape)

            label_vectors = np.asarray([embed(label.split(' '), nlp) for label in label_names])
            print("label_vectors.shape = ", label_vectors.shape)

            neigh = NearestNeighbors(n_neighbors=1,metric=spatial.distance.cosine)

            neigh.fit(label_vectors)
            closest_label = neigh.kneighbors([centroid], return_distance=False)[0, 0]

            print(label_names[closest_label])

            #here trying update column of dataframe wth predicted value
            df["Predicted Tag"][i]=label_names[closest_label]




    #print(file)
    # name, ext=os.path.splitext(file)
    # name1,name2=os.path.splitext(name)
    # print(name)
    # print(os.path.splitext(name)[1])
    name=re.findall(r'^.+\\([^.]+)\.[^\.]+$', file)  # or re.findall(r'([^\/]+)\.',string)
    print("filename= ", name[0])
    if not os.path.exists('processed_reviews/'):
        os.makedirs('processed_reviews/')
    df.to_csv("processed_reviews/_"+name[0]+"_.csv", index=False)

    #from here try save plots data of each app review
    df = pd.read_csv("processed_reviews/_"+name[0]+"_.csv")
    cat_dic_data = {'bug': 0, 'performance': 0, 'negative': 0, 'positive': 0, 'security': 0, 'login': 0, 'features': 0,'addictive':0} #,'high pricing': 0}
    predicted_tags_values = df["Predicted Tag"]

    for i in range(len(predicted_tags_values)):
        if (isinstance((predicted_tags_values[i]), str)):
            cat_dic_data[predicted_tags_values[i]] += 1

    print(cat_dic_data)

    # Data to plot
    labels = []
    sizes = []

    for x, y in cat_dic_data.items():
        labels.append(x)
        sizes.append(y)

    # Plot
    plt.pie(sizes, labels=labels)
    plt.title(name[0])

    plt.axis('equal')
    if not os.path.exists('processed_reviews/Analysis_figures/'):
        os.makedirs('processed_reviews/Analysis_figures/')
    plt.savefig("processed_reviews/Analysis_figures/_" + name[0] + "_.png")
    plt.show()

    #end here



#test file including truth values get predicted values and compute F1 Score
if not os.path.exists('processed_reviews/TestData'):
    os.makedirs('processed_reviews/TestData')

df = pd.read_csv("processed_reviews/TestData/SampleTest.csv")
comment = (df["Comment"])
#print(comment)
for i in range(len(comment)):
    if (isinstance((comment[i]), str)):  # checking whether comment is text format or not
        print("comment ", i, "= ", type(comment[i]))
        cleaned_comment = clean_text(comment[i])
        tokens = cleaned_comment.split(' ')  # working on seperate comment
        centroid = embed(tokens, nlp)

        print(centroid[:10], centroid.shape)

        label_vectors = np.asarray([embed(label.split(' '), nlp) for label in label_names])
        print("label_vectors.shape = ", label_vectors.shape)

        neigh = NearestNeighbors(n_neighbors=1)

        neigh.fit(label_vectors)
        closest_label = neigh.kneighbors([centroid], return_distance=False)[0, 0]

        print(label_names[closest_label])

        # here trying update column of dataframe wth predicted value
        df["Predicted Tag"][i] = label_names[closest_label]

        # passing this text one by one for cleaning then to nearest neibour for closest label
    df.to_csv("processed_reviews/_" + "Performance_model" + "_.csv", index=False)

df = pd.read_csv("processed_reviews/_Performance_model_.csv")
# print(" type of df[Manual_Analysis]", type(df["Manual Analysis"]))

report = metrics.classification_report(y_true=df["Manual Analysis"].tolist(),y_pred=df["Predicted Tag"].tolist(),labels=label_names)
print(report)

#analysis of data generated for 1 app




