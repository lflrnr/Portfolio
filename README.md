# Portfolio
The purpose of these projects is to showcase Python centric data science skills.  Projects 1 through 3 will focus on the Rohingya in the refugee camps in Bangladesh. I was inspired to look into this dire topic by my partner, Sifat Reazi, who is a PhD student at the University of California, Irvine. She provided significant input as to the research questions based on her domain knowledge of the subject. 
Note: The analysis and results should not be used to inform any policies.


## Project 1 - Rohingya Humanitarian Operations

Rohingya Refugees in Cox's Bazar, Bangladesh - Exploring and Visualizing Data<br/>
https://data.humdata.org/dataset/iscg-4w-influx-cox-s-bazar-bangladesh

The Inter Sector Coordination Group (ISCG) is an umbrella entity of partners and organizations coordinating the provision of services to Rohingya refugees and host communities in the Cox's Bazar area of Bangladesh. Each month, the ISCG collects and publishes data on activities for the affected communities and areas. The data below is for for the month of July 2021 and was downloaded on 2021-09-28 in .xlsx format. The goal is to use Python libraries to explore real world data, generate descriptive statistics and visuals. For such a large and complex dataset, it seems that much effort went into cleaning the data which greatly aided with this portfolio project.

Skills: Python, Pandas, Numpy, Matplotlib, Seaborn, Networkx and Pyvis

## Project 2 - Rohingya and Hope

Exploring Hope in The Rohingya Survey 2019 with ML Algorithms<br/>
http://xchange.org/reports/TheRohingyaSurvey2019.html<br/>
https://microdata.unhcr.org/index.php/catalog/434/study-description<br/>
https://data.humdata.org/dataset/the-rohingya-survey-2019-march-april-2019

Xchange conducted a survey of the perceptions of new adult arrivals to Rohingya refugee camps in Cox's Bazaar, Bangladesh after the August 2017 military operations in Rakhine State, Myanmar. The goals for this analysis were to utilize Python libraries to explore real world data, generate descriptive statistics and visuals, and to use machine learning (ML) algorithms to assess which survey features were strong predictors of hope expresesed at the very end of the survey. The data were from 2019 and were downloaded on 2021-12-06 in .xlsx format from the third hyperlink above. The majority of the data were categorical with both ordinal and non-ordinal features.

The scikit-learn machine algorithms that are utilized (sklearn calls are in parenthesis): <br/>Support Vector Classifier (SVC) <br/>K-Nearest Neighbors Classifier (KNeighborsClassifier) <br/>Logistic Regression (LogisticRegression) - did not work <br/>Naive Bayes Classifier (MultinomialNB) <br/>Decision Tree Classifier (DecisionTreeClassifier) - implemented with default parameters as well as pruned leaf nodes, max depth and entropy <br/>Random Forest Classifier (RandomForestClassifier) <br/>Ada Boost Classifier (AdaBoostClassifier) <br/>Gradient Boosting Classifier (GradientBoostingClassifier)

Skills: Python; Pandas; Numpy; Matplotlib; Seaborn; Data Munging; Feature Engineering; Machine Learning Algorithms, Grid Search & Cross Validation, and Model Performance Evaluation.

## Project 3 - Rohingya and Twitter Data

This project is currently underway and will be posted upon completion.

The initial goal for this project is to conduct analyses of sentiments and trending topics of Rohingya refugees in Bangladesh. Twitter granted my developer account elevated access to the Twitter API on 2021-12-20. If elevated access allows for filtering Tweets by geolocation, I will attempt to bound my analyses to the refugee camps and potentially to surrounding areas. Alternatively, I may use key hashtag terms like #Rohingya. Scraped Tweets will be fed into Sentiment Analysis libraries (e.g. TextBlob or Vader Sentiment: https://github.com/cjhutto/vaderSentiment) and Natural Language Processing libraries (e.g. NLTK: https://www.nltk.org/). Currently, elevated access only allows searching for the past 7 days of Tweets.

Initial questions to explore: What are the current overall sentiments in the Rohingya refugee camps in Bangladesh? Are they positive or negative or neutral? What are the currently most frequently mentioned keywords or hashtags? 
Potential future questions to explore: What are the overall sentiments regarding biometric technologies (e.g. fingerprinting, iris scanning, ID cards etc)? How have they varied over time?

https://developer.twitter.com/en/docs/twitter-api/tutorials<br/>

Skills: Python; Twitter API; Tweepy; Pandas; Vader; NLTK; Matplotlib; Seaborn; Data Munging; Feature Engineering.
