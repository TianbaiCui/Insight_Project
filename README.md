# SmartDeal: *Know when to buy*
A web app to help consumers to predict the next sales event

Link: [https://insight-smartdeal.herokuapp.com](https://insight-smartdeal.herokuapp.com)



# Table of Contents #

* [Goal](README.md#goal)
* [Approach](README.md#approach)
* [Run](README.md#run)

# Goal #

When shopping online, it is very time-consuming to find the best time to make a purchase in order to get the best discount. Sales events are typically related to holidays, but exceptions are also very common nowadays, for instance large department stores usually have anniversary or semi-annual sales events. Moreover, the discount amounts for different sales events also varies. Therefore, a tool that can help consumers to predict the next sales event as well as the discount amount is desirable. 



This leads to the specific goal of this project: make predictions on the probability of having a storewide sales event within one week or two week time windows for particular brands. It will be formulated as a multi-class classification problem, with one of the class being "No discount" and others being the specific type of sales events, e.g. Extra 20% off and Extra 30% off.

# Approach #

## 1. Collect the Data

The historical sales event data is collected from the [Dealmoon](https://www.dealmoon.com) website. I scraped the website using Selenium. The Jupyter notebook for this part of work is called `Web_Scraper.ipynb`.  The collected data is saved in the folder `Datasets`.

## 2. Data Preprocessing ##

* **Filter out the advertisements:**  
  Besides deals, Dealmoon also poses advertisements on its website. Real deals have end dates while advertisements do not. I used the information of the end date to filter out the advertisements. 
* **Extract the discount information:**
  The amount of discount of a particular deal is written in the deal description. I extracted this information using regular expression. 
* **Save the cleaned data:**
  The preprocessed data is saved under the folder `Datasets` with the suffix `_clean`.

The Jupyter notebook for the work of data preprocessing  is called `Data_cleaning+EDA.ipynb`.

## 3. Feature Engineering ##

Generated 18 new features:

* **Seasonality features:**
  Month, day of week, day of year, week of month and the distance to the nearest holiday.
* **Autocorrelation features:**
  Lag 1 to 7 of whether there was a sales event.
* **Statistical features:**
  Number of sales events within the last 15 and 30 days
  Maximum discount within the last 15 and 30 days
  Average discount within the last 15 and 30 days

## 4. Model Selection and Model Validation ##

* Applied forward-chaining cross validation
* Used XGBoost as the final model as it had the highest micro-averaged F1 score
* Save the trained model for the front-end

The Jupyter notebook for the work of part 3 and 4 is called `Feature_Engineering+Modeling.ipynb`.

## 5. Develop the front-end using Dash and Heroku

The web app was built using Dash and deployed on the Heroku cloud platform. This part of the work can be found under the folder `Web_app`.

# Run #

All codes were written in Python 3.

Need to install XGBoost. Install using `pip`:

```bash
$ pip install xgboost
```

For more information on installation of XGBoost: [https://xgboost.readthedocs.io/en/latest/build.html](https://xgboost.readthedocs.io/en/latest/build.html)

