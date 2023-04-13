# Portfolio
The purpose of these projects is to showcase Python centric data science and data analysis skills.  Projects 2 focused on the Rohingya in the refugee camps in Bangladesh. I was inspired to look into this dire topic by my partner, Sifat Reazi, who is a PhD student at the University of California, Irvine. She provided significant input as to the research questions based on her domain knowledge of the subject. 
<br/>Note: The analysis and results should not be used to inform any policies.

## Project 3 - Economic Sentiment Analysis with Twitter’s API

This project is currently underway with AWS setup constructed using RDS PostgreSQL and Lambda and preliminary code has been posted.

The initial goal for this project is to conduct economic sentiment analyses in the US using Twitter data. Twitter granted my developer account elevated access to the Twitter API.  Scraped Tweets will be fed into Sentiment Analysis libraries (e.g. TextBlob or Vader Sentiment: https://github.com/cjhutto/vaderSentiment) and Natural Language Processing libraries (e.g. NLTK: https://www.nltk.org/). Currently, elevated access only allows searching for the past 7 days of Tweets.

Initial questions to explore: What are the current overall sentiments of the economy? Are they positive or negative or neutral? How has it varied over time? Is there a correlation between economic sentiment and perhaps certain economic metrics such as stock market performance?

https://developer.twitter.com/en/docs/twitter-api/tutorials<br/>

Skills: Python; Twitter API; Tweepy; Pandas; Vader; NLTK; Matplotlib; Seaborn; Data Munging; Feature Engineering.

## Project 2 - Rohingya and Hope

Exploring Hope in The Rohingya Survey 2019 with ML Algorithms<br/>
http://xchange.org/reports/TheRohingyaSurvey2019.html<br/>
https://microdata.unhcr.org/index.php/catalog/434/study-description<br/>
https://data.humdata.org/dataset/the-rohingya-survey-2019-march-april-2019

Xchange conducted a survey of the perceptions of new adult arrivals to Rohingya refugee camps in Cox's Bazaar, Bangladesh after the August 2017 military operations in Rakhine State, Myanmar. The goals for this analysis were to utilize Python libraries to explore real world data, generate descriptive statistics and visuals, and to use machine learning (ML) algorithms to assess which survey features were strong predictors of hope expresesed at the very end of the survey. The data were from 2019 and were downloaded on 2021-12-06 in .xlsx format from the third hyperlink above. The majority of the data were categorical with both ordinal and non-ordinal features.

The scikit-learn machine algorithms that are utilized (sklearn calls are in parenthesis): <br/>Support Vector Classifier (SVC) <br/>K-Nearest Neighbors Classifier (KNeighborsClassifier) <br/>Logistic Regression (LogisticRegression) - did not work <br/>Naive Bayes Classifier (MultinomialNB) <br/>Decision Tree Classifier (DecisionTreeClassifier) - implemented with default parameters as well as pruned leaf nodes, max depth and entropy <br/>Random Forest Classifier (RandomForestClassifier) <br/>Ada Boost Classifier (AdaBoostClassifier) <br/>Gradient Boosting Classifier (GradientBoostingClassifier)

Skills: Python; Pandas; Numpy; Matplotlib; Seaborn; Data Munging; Feature Engineering; Machine Learning Algorithms, Grid Search & Cross Validation, and Model Performance Evaluation.

## Project 1 - Global Warming for Two U.S. Counties over 120 years

This project was completed for Coursera's University of Michigan Applied Data Science with Python course. The goal was to plot and compare average monthly temperatures for the past 120 years for Orange County, California and Washtenaw County, Michigan and assess if there is indeed a global warming trend experienced at the micro county level. Eyeballing the visual, it is clear that a warming trend is occurring for both counties when looking over this period as compared to the overall average for each county.

Skills: Python, Pandas, Matplotlib and Seaborn
