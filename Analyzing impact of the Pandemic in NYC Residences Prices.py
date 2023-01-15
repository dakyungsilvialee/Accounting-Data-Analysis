# -*- coding: utf-8 -*-
"""Act499r Final Group Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12gQppxa62WRzmkkrkF9CnSeBw3tqasIN

# Analyzing impact of the Pandemic in NYC Residences Prices

### Data Cleaning for NYC Real Estate dataset

We pulled the data from three boroughs (Manhattan, Brooklyn and Queens) over four years 2018-2021.

The variables are:

|Variable|Definition|
|:---------|:-----------|
|Borough|Number representing the borough in which the sale took place <br>
||1 = Manhattan <br>
||3 = Brooklyn <br>
||4 = Queens |
|Neighborhood| Name of neighborhood in which the sale took place|
|Building Class Category| Broad category of building class (eg. one family, multi family)|
|BLOCK| A tax block is a subdivision of the borough|
|Lot| A tax lot is a subdivision of a tax block. Distinguishes condos in the same building|
|ADDRESS| Street address of the property|
|APARTMENTNUMBER| Apartment number of the property if applicable|
|ZIPCODE| Property's postal code|
|RESIDENTIALUNITS| Number of residential units at the listed property|
|COMMERCIALUNITS| The number of commercial units at the listed property|
|TOTALUNITS| The total number of units at the listed property|
|LANDSQUAREFEET| The land area of the property list in square feet|
|GROSSSQUAREFEET| The total area of all the floors of a building as measured from the exterior surfaces of the outside walls of the building, including the land area and space within any building or structure on the property. |
|YEARBUILT| Year the structure on the property was built|
|TAXCLASSATTIMEOFSALE| - Class 1: Includes most residential property of up to three units, vacant land that is zoned for residential use, and most condominiums that are not more than three stories. <br>
||- Class 2: Includes all other property that is primarily residential, such as cooperatives and condominiums. <br>
||- Class 3: Includes property with equipment owned by a gas, telephone or electric company. <br>
||- Class 4: Includes all other properties not included in class 1,2, and 3, such as offices, factories, warehouses, garage buildings, etc.  |
|BUILDINGCLASSATTIMEOFSALE|The Building Classification is used to describe a property’s constructive use.<br>
||The Letter describes a general class of properties (for example “A” signifies one-family homes, “O” signifies office buildings. “R” signifies condominiums).<br>
||The Number adds more specific information about the property’s use or construction style (using our previous examples “A0” is a Cape Cod style one family home, “O4” is a tower type office building and “R5” is a commercial condominium unit). <br>
||https://www1.nyc.gov/assets/finance/jump/hlpbldgcode.html|
|SALEPRICE| Price paid for the property|
|SALEDATE| Date the property sold|

### Overarching Question:

We hypothesize that the housing factors that are relevant to residential buildings are mostly impacted by the pandemic due to families having to look homes to quarantine long periods, therefore we want to...

Analyze the highest average (mean) sale price of each borough (Manhattan, Brooklyn, Queens) pre Covid (2018-219) and post Covid (2020-2022) in order to identify residential relevant housing factors such as:


*   gross square feet
*   building class category (e.g one family, multi family, etc)
*   tax class at time sale: class '2' (residential property)
*   building class at time of sale 'A' (one-family home) 
*   market cap (dollar amount volume of the transaction's sale price)

that effect the housing market from the mandatory Covid quarantine policy.



Overall, did Covid changed people's preference regarding these certain housing factors, due to the inevitable quarantine lifestyle?
"""

# Import necessary libraries
import pandas as pd 
import numpy as np

# Import plotting libraries
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

import warnings
warnings.filterwarnings('ignore')
pd.options.display.float_format = '{:,.2f}'.format

import statsmodels.formula.api as smf

# Create loop to process the datasets

# Defining lists of years and boroughs
years = [2018, 2019, 2020, 2021]
boroughs = ['manhattan', 'brooklyn', 'queens']

# Defining the list of columns we want to keep in our final database
columns_to_keep = ['BOROUGH', 'NEIGHBORHOOD', 'BUILDINGCLASSCATEGORY', 'BLOCK', 'LOT', 'EASE-MENT',
                    'ADDRESS', 'APARTMENTNUMBER', 'ZIPCODE', 'RESIDENTIALUNITS', 'COMMERCIALUNITS', 
                   'TOTALUNITS', 'LANDSQUAREFEET', 'GROSSSQUAREFEET', 'YEARBUILT', 'TAXCLASSATTIMEOFSALE', 
                   'BUILDINGCLASSATTIMEOFSALE', 'SALEPRICE', 'SALEDATE']

# Creating a dictionary to store the clean databases
dict_df = {}

# LOOP

for year in years :
    for borough in boroughs :

        # Importing the database
        filename = str(year) + '_' + borough + '.xlsx'

        # Load year 2018 and 2019 
        if year == 2018 or year == 2019 :
            database = pd.read_excel(filename, header = 4)
        # Load year 2020 and 2021
        elif year == 2020 or year == 2021 :
            database = pd.read_excel(filename, header = 6)
        
        # Deleting '\n's and empty spaces from column names
        database.columns = database.columns.str.replace(pat = '\n', repl = '')
        database.columns = database.columns.str.replace(pat = ' ', repl = '')
        
        # Only keeping useful columns in the db
        database = database[columns_to_keep]
        
        # Storing clean database into the dictionary
        dict_df[filename[:-5]] = database

# Concatenating all clean databases into one big DB
nyc_db = pd.concat(dict_df, ignore_index = True)

# Dropping "EASE-MENT" column
nyc_db = nyc_db.drop('EASE-MENT', axis = 1)

# Putting all the right column types

nyc_db['BOROUGH'] = nyc_db['BOROUGH'].astype(str)
nyc_db['BLOCK'] = nyc_db['BLOCK'].astype(str)
nyc_db['LOT'] = nyc_db['LOT'].astype(str)
nyc_db['ZIPCODE'] = nyc_db['ZIPCODE'].astype(str)
nyc_db['TAXCLASSATTIMEOFSALE'] =nyc_db['TAXCLASSATTIMEOFSALE'].astype(str)
nyc_db['YEARBUILT'] = nyc_db['YEARBUILT'].astype(str)

# Converting the 'YEAR BUILT' column to datetime format

nyc_db['YEARBUILT'] = nyc_db['YEARBUILT'].str[0:4]
nyc_db['YEARBUILT'] = pd.to_datetime(nyc_db['YEARBUILT'], format = '%Y', errors='coerce')

# Drop rows where we do not have information on gross feet squarage and sale price
nyc_db.dropna(subset = ['SALEPRICE'], inplace = True)
nyc_db.dropna(subset = ['GROSSSQUAREFEET'], inplace = True)

# Create column with the sale year
nyc_db['saleyear'] = nyc_db['SALEDATE'].dt.year

nyc_db_subset = nyc_db.copy()

# Map 2018-2019 and 2020-2021 to pre and post-Covid
nyc_db_subset['Pre/Post Covid'] = nyc_db_subset['saleyear'].map({2018 : 'Pre Covid', 2019 : 'Pre Covid', 2020 : 'Post Covid', 2021 : 'Post Covid'})

# Map Borough numbers to Boroughs names
nyc_db_subset['BOROUGH'] = nyc_db_subset['BOROUGH'].map({'1.0' : 'Manhattan', 
                                                         '3.0' : 'Brooklyn', 
                                                         '4.0' : 'Queens'})
# Cleaning NaN values from Apartment number column

nyc_db_subset.dropna(subset = ['APARTMENTNUMBER', 'BOROUGH', 'YEARBUILT'], axis = 0, inplace = True)
nyc_db_subset.drop(nyc_db_subset[nyc_db_subset['SALEPRICE'] == 0].index, inplace = True)

nyc_db_subset

"""### Descriptive Question #1: 

Since we assume that sale price fluctuation would happen from residential units that are affected by the quarantine rule, we decided to use tax class type 2 under the residential transaction variable. 


What percentage of the total residential transactions (Tax Class Type Two) occured before and after the pandemic? How does this vary across the different boroughs?




"""

# Create Data Frame for Tax Class 2 Properties
class2 = nyc_db_subset.loc[nyc_db_subset['TAXCLASSATTIMEOFSALE'] == '2.0']
#Include Pre Covid Variables
class2.pre = class2.loc[class2['Pre/Post Covid'] == 'Pre Covid']

# Find number of transactions for each borough
class2.pre.manhattan = class2.pre.loc[class2.pre['BOROUGH'] == 'Manhattan']
class2.pre.brooklyn = class2.pre.loc[class2.pre['BOROUGH'] == 'Brooklyn']
class2.pre.queens = class2.pre.loc[class2.pre['BOROUGH'] == 'Queens']

#Include Post Covid Variables
class2.post = class2.loc[class2['Pre/Post Covid'] == 'Post Covid']

# Find number of transactions for each borough
class2.post.manhattan = class2.post.loc[class2.post['BOROUGH'] == 'Manhattan']
class2.post.brooklyn = class2.post.loc[class2.post['BOROUGH'] == 'Brooklyn']
class2.post.queens = class2.post.loc[class2.post['BOROUGH'] == 'Queens']



preman = class2.pre.manhattan.BOROUGH.count()/class2.BOROUGH.count()
prebro = class2.pre.brooklyn.BOROUGH.count()/class2.BOROUGH.count()
preque = class2.pre.queens.BOROUGH.count()/class2.BOROUGH.count()
postman = class2.post.manhattan.BOROUGH.count()/class2.BOROUGH.count()
postbro = class2.post.brooklyn.BOROUGH.count()/class2.BOROUGH.count()
postque = class2.post.queens.BOROUGH.count()/class2.BOROUGH.count()

totalprecov = preman + prebro + preque
totalpostcov = postman + postbro + postque
totalman = preman + postman
totalbro = prebro + postbro
totalque = preque + postque
total = totalprecov + totalpostcov

percov = pd.DataFrame({'Borough': ['Manhattan', 'Brooklyn', 'Queens', 'Total'],
                       'Pre Covid': [preman, prebro, preque, totalprecov],
                       'Post Covid': [postman, postbro, postque, totalpostcov],
                       'Total': [totalman, totalbro, totalque, total]})

percov

# percov['Percent Change'] =

"""### Analysis:

The contingency table shows that Manhattan was the borough with the highest percentage of transactions, both before and after the pandemic, followed by Brooklyn and then Queens. Furthermore, we can see that all the Borough's experienced a substantial decrease in sales after the pandemic, as pre-covid sales represented 71% of all sales, while post-covid were only 29% (over the same 2-year period). In absolute value, Manhattan experienced a a 23% decrease in sales, Brooklyn a 13% decrease and Queens a 5% decrease.

##Descriptive Question #2:

Does the year when the property was built affect the sale price before and after Covid? 

Additionally, show the distribution of the year when the roperty was built and its correlation to sale price.
"""

yearbuilt_sp = nyc_db_subset.groupby(['YEARBUILT', 'saleyear', 'Pre/Post Covid', 'BOROUGH'])['SALEPRICE'].describe()
yearbuilt_sp.dropna()
yearbuilt_sp.head(100)

dis = sns.displot(data = yearbuilt_sp, x="YEARBUILT", y="saleyear", hue="BOROUGH", aspect = 1)
dis.set_xticklabels(['1880','1900','1920','1940','1960','1980','2000','2022'])


dis

"""This heatmap demonstrates the building year preferences across each of the different sale years and Boroughs. From it, we can infer that during 2018, there was a strong demand for pre-1900s buildings in Manhattan, and for newer (post 1920s) Apartments in Queens. However, in 2019, we can infer a slight shift in preference for older Brooklyn Apartments, with a steady demand for Queen's newer apartments. The demands trends and preferences remained similar for apartments sold in 2020, but thee was a major shift in preferences for 2021. During this year, the demand was mostly for newer Manhattan apartments, while the overall demand for apartments in Brooklyn and Queens declined."""

dis1 = sns.displot(data = class2, x="YEARBUILT", y="SALEPRICE", hue="BOROUGH", height = 4, aspect = 3)





dis1

"""### Analysis:

From our analysis, we are able to understand the relationship between the year a residence was built and its sale price. As it can be seen, there is an overall positive correlation, implying that newer buildings are more expensive. However, the trend is not clear, as the sale price can be considered to be mostly steady from 1900 to 2000. However, there is a significant impact on residences built before 1900, as they were substantially cheaper, and the inverse impact with post-2000 residences, as they are substantially more expensive, across all boroughs.

### Descriptive Question #3:

The previous descriptive questions yielded insights that Manhattan had higher frequency of having transactions compared to Brooklyn and Queens. 

To dive deeper, what is the average sale price per square feet in each of the borough's? Is there any difference between before and after the pandemic?
"""

class2 = nyc_db_subset.loc[nyc_db_subset['TAXCLASSATTIMEOFSALE'] == '2.0']
class2.dropna(subset = ['SALEPRICE'], inplace = True)
class2.drop(class2[class2['SALEPRICE'] == 0].index, inplace = True)
class2.dropna(subset = ['GROSSSQUAREFEET'], inplace = True)
class2.drop(class2[class2['GROSSSQUAREFEET'] == 0].index, inplace = True)



# Average Price Manhattan
class2['PRICEPERSQFT'] = class2['SALEPRICE']/class2['GROSSSQUAREFEET']
class2.dropna(subset = ['PRICEPERSQFT'], inplace = True)

class2.man = class2.loc[class2['BOROUGH'] == 'Manhattan']

class2.man.pre = class2.man.loc[class2['Pre/Post Covid'] == 'Pre Covid']
class2.man.post = class2.man.loc[class2['Pre/Post Covid'] == 'Post Covid']




manpre = class2.man.pre.PRICEPERSQFT.mean()
manpost = class2.man.post.PRICEPERSQFT.mean()

#Average Price Brooklyn
class2.bro = class2.loc[class2['BOROUGH'] == 'Brooklyn']

class2.bro.pre = class2.bro.loc[class2['Pre/Post Covid'] == 'Pre Covid']
class2.bro.post = class2.bro.loc[class2['Pre/Post Covid'] == 'Post Covid']

bropre = class2.bro.pre.PRICEPERSQFT.mean()
bropost = class2.bro.post.PRICEPERSQFT.mean()

#Average Price Queens
class2.que = class2.loc[class2['BOROUGH'] == 'Queens']

class2.que.pre = class2.que.loc[class2['Pre/Post Covid'] == 'Pre Covid']
class2.que.post = class2.que.loc[class2['Pre/Post Covid'] == 'Post Covid']

quepre = class2.que.pre.PRICEPERSQFT.mean()
quepost = class2.que.post.PRICEPERSQFT.mean()


pre = [manpre, bropre, quepre]
post = [manpost, bropost, quepost]
labels = ['Manhattan', 'Brooklyn', 'Queens']



x = np.arange(len(labels))
width=0.35
fig, ax = plt.subplots()
rects1 = ax.bar(labels, pre, width, label='Pre Covid')
rects2 = ax.bar(labels, post, width, label='Post Covid')

ax.set_ylabel('Average Price')
ax.set_xlabel('Borough')
ax.set_title('Average Sale Price per Square Feet in Each Boroughs')
ax.set_xticks(x, labels)
ax.legend()

fig.tight_layout()

plt.show()

"""### Analysis:

As is seen, Manhattan has the highest average sale price per square feet, followed by Brooklyn and then Queens. Moreover, the pandemic had a significant impact on the average sale price of residences in all the boroughs. Manhattan had the lowest proportional decrease, while properties in Brooklyn and Queens had a significant decrease in their prices due to the pandemic. Therefore, Brooklyn and Queens are more sensitive in pricing due to the economic impact of Covid-19.

###Descriptive Question #4:

What is the average sale price for each of the building class categories? How does this change before/after the pandemic? 

How has the demand for NYC properties been affected by the pandemic? How has the market cap (volume of sale price) for each of the building class categories been impacted by the pandemic?
"""

# See distinct building class category with its corresponding average sale price and borough during pre/post covid
buildingclass_category = nyc_db_subset.groupby(['BUILDINGCLASSCATEGORY', 'Pre/Post Covid', 'BOROUGH'])['SALEPRICE'].mean()
buildingclass_category = buildingclass_category.to_frame()
buildingclass_category.head(30)

"""As it can be seen, there is a wide spread over the sale prices across the different boroughs. As it was previously discussed, the average sell price was overall higher pre-covid, and those average prices decreased with the pandemic. Furthermore,it can be seen that throughout the spread, Manhattan had -in most cases- the highest average sale price, but this differs across different building categories. For instance, the Rental- Walkup Apartments had a higher average sale price in Brooklyn than Manhattan post-covid, but before the pandemic, Manhattan was signifanctly more expensive than Brooklyn. """

# Market Cap for Each Borough
buildingclass_category = nyc_db_subset.groupby(['BOROUGH'])['SALEPRICE'].sum()
buildingclass_category = buildingclass_category.to_frame()
buildingclass_category.rename(columns = {'SALEPRICE':'MARKETCAP'}, inplace = True)
buildingclass_category.head(30)

"""As it can be seen, Manhattan has the highest market cap, for which we can assume it was the Borough that the most money transacted during the period of analysis, followed by Brooklyn and finally Queens. However, has the pandemic had any impact on the market cap in each of the boroughs?"""

# Find Market Cap for each Borough pre/post Covid
buildingclass_category = nyc_db_subset.groupby(['BOROUGH', 'Pre/Post Covid'])['SALEPRICE'].sum()
buildingclass_category = buildingclass_category.to_frame()
buildingclass_category.rename(columns = {'SALEPRICE':'MARKETCAP'}, inplace = True)
# buildingclass_category['MARKETCAP']= buildingclass_category['MARKETCAP'].astype("string")
# buildingclass_category['MARKETCAP'] = buildingclass_category['MARKETCAP'].str.rstrip("%").astype(float)/100
# buildingclass_category['MARKETCAP'].pct_change()

# look at pct change again
buildingclass_category

"""As it can be seen, the pandemic had an immense impact of the market cap. However, each borough was affected to a different extent. In absolute value, Manhattan was the most affected by the pandemic, followed by Brooklyn and finally Queens. However, in the percent change, Brooklyn was the most affected, followed by Manhattan and then Queens. """

# See distinct building class category with its corresponding market cap and borough during pre/post covid
buildingclass_category = nyc_db_subset.groupby(['BUILDINGCLASSCATEGORY', 'Pre/Post Covid', 'BOROUGH'])['SALEPRICE'].sum()
buildingclass_category = buildingclass_category.to_frame()
buildingclass_category.rename(columns = {'SALEPRICE':'MARKETCAP'}, inplace = True)
buildingclass_category.head(30)

"""We decided that for our analysis, it would also be relevant to understand the market cap in each of the boroughs. To identify it, we added all the transacion prices by building category across each borough, and then distinguished between pre and post covid. Therefore, the values represent the sum of the total sale prices, to understand the different patterns of demand. In this case, we can see that Brooklyn had the most market movements, as more money was transacted in that Borough. \"""

# See the residential building class at time of sale 'A' with its borough during both pre/post Covid

buildingclass_ts = nyc_db_subset[nyc_db_subset['BUILDINGCLASSATTIMEOFSALE'].str.startswith('A')]
buildingclass_ts = buildingclass_ts.groupby(['BOROUGH', 'BUILDINGCLASSATTIMEOFSALE', 'Pre/Post Covid'])['SALEPRICE'].nunique()
buildingclass_ts = buildingclass_ts.to_frame()
buildingclass_ts.rename(columns = {'SALEPRICE':'# of Transactions'}, inplace = True)
buildingclass_ts.head(94)

"""### Analysis:

Finally, it would be relevant to understand how the number of transactions vary across building classes and the impact of the pandemic. In this case, we are more concerned about the amount of sales, rather than the sale price, since we can have a better perspective of the market movements.

###**Regression Analysis**

As part of our analysis, we try to identify which of the variables from the dataset has the greatest impact on the sales price. Therefore, we will run a multivariate regression, including jousing factors such as 


*   gross square feet
*   building class category (e.g one family, multi family, etc)
*   tax class at time sale: class '2' (residential property)
*   building class at time of sale 'A' (one-family home) 
* Borough





We would like to understand how each of those variables change across Boroughs and the impact of the pandemic.
"""

# Run regression for Pre-Covid Variables

regpre = nyc_db_subset[nyc_db_subset['BUILDINGCLASSATTIMEOFSALE'].str.startswith('A')]
regpre = nyc_db_subset[nyc_db_subset['TAXCLASSATTIMEOFSALE'] == '2.0']
regpre = nyc_db_subset[nyc_db_subset['Pre/Post Covid'] == 'Pre Covid']
regspre = smf.ols(data= regpre, formula='SALEPRICE ~ GROSSSQUAREFEET + BOROUGH+ BUILDINGCLASSATTIMEOFSALE').fit()
regspre.summary()

"""When running the regression for the impact the variables had on the sales price before the pandemic, the overall correlation was low, at 0.119. Individually, each of the variables, had a low correlation -possibly due to the amount of variables included, but all which are highly relevant for our analysis. Furthemore, the correlation coefficients for most of the buildings categories is negative, except for A7, D3, D9, R5, RA, RB, RH and RK, most of which are Condos. Based on the p-values (lower than 0.05), we can see that building classes C4 and C5, which are both Walk Up Apartments, are the only ones significant. As expected, Borough and Gross Square Feet had a much higher correlation with Sale Price, as an increase of one unit in Gross Square Feet, would represent a $606 increase in sale price. On the other hand, Borough didn't seem to have such a strong correlation either, possibly due to the range of prices or high amount of variables being explored. """

# Test Regression for Post-Covid Variables
regpost = nyc_db_subset[nyc_db_subset['BUILDINGCLASSATTIMEOFSALE'].str.startswith('A')]
regpost = nyc_db_subset[nyc_db_subset['TAXCLASSATTIMEOFSALE'] == '2.0']
regpost = nyc_db_subset[nyc_db_subset['Pre/Post Covid'] == 'Post Covid']
regspost = smf.ols(data= regpost, formula='SALEPRICE ~ GROSSSQUAREFEET + BOROUGH + BUILDINGCLASSCATEGORY').fit()
regspost.summary()

"""However, when analyzing the impact that the pandemic had on influecing the variables that impact sale price, the results were very similar. The overall correlation, although a bit higher at 0.138. Nevertheless, based on the p-values, none of the variables are statistically significant, which is once again likely due to the high amount of "x" variables that we chose in the regression. Possibly the main difference of the regression is the impact that gross square feet had in the prices. In this case, the correlation coefficient is negative, indicating an inverse relationship.

**Correlation between Sale Price and Gross Square Feet**
"""

# Correlation Before Pandemic
sns.lmplot(x="GROSSSQUAREFEET",
           y="SALEPRICE", 
           data=regpre);

"""As it was previously discussed, before the pandemic, a higher gross square feet was relevant when determining the sale price, as it can be seen by the graph."""

# Correlation Before Pandemic
sns.lmplot(x="GROSSSQUAREFEET",
           y="SALEPRICE", 
           data=regpost);

"""On the other hand, after the pandemic, the correlation diminishes, and gross square feet is no longer a significant determinant. """



"""# **Supervised Learning**

### Visualization is a great place to start: 
###plot each of the variables to understand how they change over time and relate to each other
"""

plt.figure(figsize=(15, 10))

plt.plot(nyc_db_subset['BUILDINGCLASSATTIMEOFSALE'], marker='o', color='black', label = 'Building Class at Time of Sale (A)')
plt.plot(nyc_db_subset['TAXCLASSATTIMEOFSALE'], marker='o', color='blue', label = 'Tax Class at Time of Sale (2.0)')
plt.plot(nyc_db_subset['GROSSSQUAREFEET'], marker='o', color='yellow', label = 'Gross Square Feet')
plt.plot(nyc_db_subset['SALEPRICE'], marker='o', color='red', label = 'Sale Price')

plt.legend()

"""### Forecasting from Supervised Learning Method"""

# 
nyc_db_subset.tail()

# add into final dataframe
extra = nyc_db_subset = pd.Dataframe({'saleyear :  [2023, 2024, 2025]'})
extra = nyc_db_subset.append(extra, ignore_index = True)
extra.tail()

# Create OLS based forecast
# use model.predict() to calculate prediced Y values

extra['SALEPRICE'] = model.predict(extra['saleyear'])

# plot the outsample forecast

plt.figure(figsize=(15, 6))
plt.plot(cokeq[variable], marker='o', color='black', label = 'Actual Demand')
plt.plot(cokeq['ols_prediction'], marker='o', color='orange', label = 'OLS Prediction')

plt.legend()
plt.ylabel(variable)
plt.xlabel('Time Period')

"""### Forecasting Analysis:

### Overarching Question & Overall Analysis

Overall, the purpose of our analysis was to determine the impact that the pandemic had on the preferences, trends and sale price of NYC residences. In order to do so, our analysis consisted of 4 descriptive questions, each that provided insight for our overall conclusion. The first question attempted to understand the distribution of demand across the boroughs, and the impact that the pandemic had on it. As it was previously commented, Manhattan absorped most of the demand overall, followed by Brooklyn and Queens. In addition, it was also evident that the overall demand fell substantially, from 71% of transactions occurring before the pandemic, and 29% after it.

In our second question, we tried to identify the relationship between year built, demand and sale price. Our analysis revealed when were the residences built in each Borough, as well as which types of buildings (new or old) were preferred in each borough in each year. Furthermore, we identified the impact that the variable "YEARBUILT" has on price, and the results have been previously discussed.

We continued our analysis by trying to understand the impact of the pandemic on the average price per square foot, where we were able to identify not only which borough had the highest average, but also which one was the most impacted by the pandemic. 

Finally, we focused on the building class category of the NYC residences, and how each of their prices varies across borough and pre/post covid. We then calculated the market cap, to understand the demand each of the building class categories had, and how many transactions had been made pre/post covid to potentially analyze any shifts in demand. To have a clearer idea about any potential shifts in demand, we also calculated the # of transactions in each Borough for each building class category.

For our regression analysis, we ran a regression with the previously identified variables and sale price. Our result yielded that most variables weren't statistically significant, for which we chose to run a separate regression just for Gross Square Feet. By doing so, we were able to understand that before the pandemic, gross square feet had much stronger relationship with sale price than after the pandemic.
"""