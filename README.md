# Portfolio
The purpose of these bespoke projects is to showcase my growing data skills.  The analysis and results should not be used to inform any policies.

## Project 3 - Consumer Confidence and the U.S. Economy
### This project's website is running live on an AWS EC2 instance and can be found at:  
https://cloud-econ.com

The project's goal is to visually compare consumer confidence of the US economy with respect to important economic metrics from the Federal Reserve's FRED API using Dash and Plotly. Furthermore, the project showcases my knowledge of data, deployment and cloud tools.

Initial questions to explore:
What is the current consumer confidence of the economy?
How has it varied over time?
Is there a correlation between consumer confidence and economic metrics like stock market performance?

Once enough data are collected, they will be fed into machine learning models to best fit a predictive model and determine if any economic indicators have correlations with consumer confidence as the target variable.

Skills: Python; FRED API; Pandas; Docker; Github Actions; PostgreSQL; AWS - RDS, S3, ECR, ECS, EC2, Lambda, SNS, Cloudwatch, IAM, EventBridge; Plotly; Dash; pgAdmin; YAML; Cloudflare; Data Munging; Automation; Continuous Delivery

## Project 2 - Rohingya and Hope

Exploring Hope in The Rohingya Survey 2019 with ML Algorithms

Xchange conducted a survey of the perceptions of new adult arrivals to Rohingya refugee camps in Cox's Bazaar, Bangladesh after the August 2017 military operations in Rakhine State, Myanmar. The goals for this analysis were to utilize Python libraries to explore real world data, generate descriptive statistics and visuals, and to use machine learning (ML) algorithms to assess which survey features were strong predictors of hope expresesed at the very end of the survey. The data were from 2019 and were downloaded on 2021-12-06 in .xlsx format from the third hyperlink above. The majority of the data were categorical with both ordinal and non-ordinal features.

The scikit-learn machine algorithms that are utilized (sklearn calls are in parenthesis): <br/>Support Vector Classifier (SVC) <br/>K-Nearest Neighbors Classifier (KNeighborsClassifier) <br/>Logistic Regression (LogisticRegression) - did not work <br/>Naive Bayes Classifier (MultinomialNB) <br/>Decision Tree Classifier (DecisionTreeClassifier) - implemented with default parameters as well as pruned leaf nodes, max depth and entropy <br/>Random Forest Classifier (RandomForestClassifier) <br/>Ada Boost Classifier (AdaBoostClassifier) <br/>Gradient Boosting Classifier (GradientBoostingClassifier)

Skills: Python; Pandas; Numpy; Matplotlib; Seaborn; Data Munging; Feature Engineering; Machine Learning Algorithms, Grid Search & Cross Validation, and Model Performance Evaluation.

## Project 1 - Global Warming for Two U.S. Counties over 120 years

This project was completed for Coursera's University of Michigan Applied Data Science with Python course. The goal was to plot and compare average monthly temperatures for the past 120 years for Orange County, California and Washtenaw County, Michigan and assess if there is indeed a global warming trend experienced at the micro county level. Eyeballing the visual, it is clear that a warming trend is occurring for both counties when looking over this period as compared to the overall average for each county.

Skills: Python, Pandas, Matplotlib and Seaborn
