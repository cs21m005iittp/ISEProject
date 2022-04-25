# ISEProject
This project intends to classify user reviews on Game apps.

Steps followed:
1.data scrapping of 10 game apps on play store
2.extracting user reviews from scrapped data
3.analysis of reviews using ML Unsupervised learning  model and predicting which TAG suitable for comments
4.Based on TAGs performing statistical analysis on overall Games app performance
5.Calculating accuracy of our model

Analysis results of our model:
For testing accuracy of our model use Test data file store it in "processed_reviews\TestData\" folder
Accuracy:
              precision    recall  f1-score   support

         bug       1.00      0.25      0.40        12
 performance       0.00      0.00      0.00         3
    negative       0.50      0.20      0.29         5
    positive       0.47      0.50      0.49        18
    security       0.00      0.00      0.00         0
       login       0.00      0.00      0.00         0
    features       0.07      0.50      0.12         2
   addictive       0.00      0.00      0.00         0

   micro avg       0.35      0.35      0.35        40
   macro avg       0.26      0.18      0.16        40
weighted avg       0.58      0.35      0.38        40

How to run project?
prerequisites:
1.Python Installed on machine

For scrapping play store review data run "python PlayStoreDataScrappingAndCleaning.py"
  i.check your PWD where you run above command, goto "reviews\" folder where you find App wise review data excelsheet 
For reviews analysis,classification and statistical view of data run  "python Unsupervised_TagLearning_by_reviews.py"
  i.check your PWD where you run above command, goto "processed_reviews\" folder where you find App wise review classification and predicted TAGS for each review
  ii.statistical analysis of each App based on their user reviews in folder "processed_reviews\Analysis_figures\"

