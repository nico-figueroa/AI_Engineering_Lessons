# Analyzing Recommendation System Performance Across Model Versions

- [View Solution Notebook](./solutions.html)
- [View Project Page](https://www.codecademy.com/content-items/13f970fd92fa48db8d99b770964b037e)


## Background
You're an AI Engineer at a growing e-commerce company that has been experimenting with AI-powered product recommendations. Over the past 10 months, the data science team deployed three versions of their recommendation model:

* v1.0 - The baseline model (cheapest to run)
* v1.1 - An improved version with better accuracy (moderate cost)
* v2.0 - The latest model using advanced techniques (most expensive)

Each newer version costs more to operate due to increased computational requirements, but the team hopes these investments will pay off through higher sales. Your job is to determine which model actually delivers the best return on investment.

## The Dataset
This project uses synthetically generated data that simulates real e-commerce behavior. The dataset comprises 10 months of customer interactions, featuring realistic patterns in purchasing behavior, demographic distributions, and recommendation outcomes. While the data is synthetic, it reflects the types of challenges and patterns you'd encounter in production AI systems.

### Key Metrics You'll Analyze
1. Conversion Rate: The percentage of customer interactions that result in a purchase. For example, if 100 customers view products and 8 make purchases, that's an 8% conversion rate. This is your primary success metric—did recommendations actually drive more sales?
2. ROI (Return on Investment): How much profit you generate for every dollar spent on the AI system. An ROI of 150% means for every `$1` spent running the model, you earn `$2.50` back (`$1` returned + `$1.50` profit). This tells you whether the AI investment is financially worthwhile.
3. Profit: Revenue from sales minus all costs (both product costs and AI inference costs). This is your bottom line—the actual money made after accounting for everything.

Your analysis will directly influence a major business decision: should the company stick with the cheaper v1.0, upgrade to the expensive v2.0, or adopt a smart routing strategy using different models for different customers?

Let's find out!

## Setup and Initial Data Exploration

**Task 1:** Import pandas as `pd`, numpy as `np`, and from `scipy.stats` import `chi2_contingency` for statistical testing.


```python
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
```

**Task 2:** Load the CSV file `ecommerce_recommendation_events.csv` into a DataFrame called `events`. Display the first 10 rows and print the shape to understand the dataset size.


```python
events = pd.read_csv('ecommerce_recommendation_events.csv')
print(events.head(10))
print(f"\nDataset shape: {events.shape}")
```

        timestamp  customer_id                            email            phone  \
    0  1704092618         4464    sophia.anderson4464@email.com  +1-636-599-5625   
    1  1704093226         3079    amelia.gonzalez3079@inbox.com  +1-313-997-8700   
    2  1704093327         4757        mason.davis4757@inbox.com  +1-556-615-7307   
    3  1704094155          938  isabella.rodriguez938@email.com  +1-345-911-8113   
    4  1704094174         2128        ava.jackson2128@email.com  +1-482-307-4871   
    5  1704094505         3757        ethan.moore3757@email.com  +1-654-968-2040   
    6  1704095017         1331        mason.garcia1331@mail.com  +1-580-491-7965   
    7  1704096951         3512     henry.martinez3512@inbox.com  +1-746-633-6045   
    8  1704097147         3903     alexander.davis3903@mail.com  +1-511-338-5713   
    9  1704097404          595       william.moore595@inbox.com  +1-897-735-5477   
    
       product_id event_type  recommended model_version  age region  \
    0         408   purchase            0          v1.0   25  South   
    1          51       view            0          v1.0   25  South   
    2         296       view            0          v1.0   18  North   
    3          33       view            0          v1.0   55  North   
    4         927       view            1          v1.0   25  North   
    5         414  addtocart            1          v1.0   25  North   
    6         838       view            1          v1.0   45  North   
    7         306  addtocart            0          v1.0   18   East   
    8          39       view            0          v1.0   55   East   
    9         812   purchase            1          v1.0   55  South   
    
      customer_segment product_category price_tier  revenue  product_cost  \
    0           budget      electronics       high   858.29        415.88   
    1          premium      electronics     medium     0.00          0.00   
    2          regular         clothing       high     0.00          0.00   
    3           budget           sports        low     0.00          0.00   
    4          premium           sports        low     0.00          0.00   
    5          regular         clothing        low     0.00          0.00   
    6          premium             home        low     0.00          0.00   
    7          premium             home       high     0.00          0.00   
    8          regular            books     medium     0.00          0.00   
    9          premium            books        low    18.91         10.37   
    
       inference_cost  total_cost   profit  
    0           0.000     415.880  442.410  
    1           0.000       0.000    0.000  
    2           0.000       0.000    0.000  
    3           0.000       0.000    0.000  
    4           0.003       0.003   -0.003  
    5           0.003       0.003   -0.003  
    6           0.003       0.003   -0.003  
    7           0.000       0.000    0.000  
    8           0.000       0.000    0.000  
    9           0.003      10.373    8.537  
    
    Dataset shape: (50000, 18)


**Task 3:** Display the column names and data types using `.dtypes` and print the list of all column names.


```python
print(events.dtypes)
print(f"\nColumns: {list(events.columns)}")
```

    timestamp             int64
    customer_id           int64
    email                object
    phone                object
    product_id            int64
    event_type           object
    recommended           int64
    model_version        object
    age                   int64
    region               object
    customer_segment     object
    product_category     object
    price_tier           object
    revenue             float64
    product_cost        float64
    inference_cost      float64
    total_cost          float64
    profit              float64
    dtype: object
    
    Columns: ['timestamp', 'customer_id', 'email', 'phone', 'product_id', 'event_type', 'recommended', 'model_version', 'age', 'region', 'customer_segment', 'product_category', 'price_tier', 'revenue', 'product_cost', 'inference_cost', 'total_cost', 'profit']


**Task 4:** Create a new column called `converted` that equals `True` when `event_type` is `'purchase'` and `False` otherwise. Then print the total number of events, total purchases, and overall conversion rate.


```python
events['converted'] = events['event_type'] == 'purchase'
print(f"Total events: {len(events)}")
print(f"Purchases (conversions): {events['converted'].sum()}")
print(f"Conversion rate: {events['converted'].mean():.2%}")
```

    Total events: 50000
    Purchases (conversions): 3225
    Conversion rate: 6.45%


## Financial Performance Analysis

**Task 5:** Calculate overall financial metrics from converted events only: sum of `revenue`, sum of `product_cost`, sum of `total_cost`, and sum of `profit`. Also, calculate the total `inference_cost` across ALL events. Finally, calculate the average profit per conversion.



```python
total_revenue = events[events['converted']]['revenue'].sum()
total_product_cost = events[events['converted']]['product_cost'].sum()
total_inference_cost = events['inference_cost'].sum()
total_cost = events[events['converted']]['total_cost'].sum()
total_profit = events[events['converted']]['profit'].sum()
avg_profit_per_conversion = total_profit / events['converted'].sum()

print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Total Product Cost: ${total_product_cost:,.2f}")
print(f"Total Inference Cost: ${total_inference_cost:,.2f}")
print(f"Total Cost: ${total_cost:,.2f}")
print(f"Total Profit: ${total_profit:,.2f}")
print(f"Average Profit per Conversion: ${avg_profit_per_conversion:.2f}")
```

    Total Revenue: $580,316.66
    Total Product Cost: $273,011.92
    Total Inference Cost: $106.65
    Total Cost: $273,021.99
    Total Profit: $307,294.67
    Average Profit per Conversion: $95.29


**Task 6:** Group by the `recommended` column (0 or 1) and calculate the mean of both `converted` and `profit` columns. Calculate lift for both metrics by dividing the recommended values by the non-recommended values.



```python
rec_analysis = events.groupby('recommended').agg({
    'converted': 'mean',
    'profit': 'mean'
}).reset_index()
rec_analysis.columns = ['recommended', 'conversion_rate', 'avg_profit']

conv_lift = rec_analysis[rec_analysis['recommended'] == 1]['conversion_rate'].values[0] / rec_analysis[rec_analysis['recommended'] == 0]['conversion_rate'].values[0]
profit_lift = rec_analysis[rec_analysis['recommended'] == 1]['avg_profit'].values[0] / rec_analysis[rec_analysis['recommended'] == 0]['avg_profit'].values[0]

print(rec_analysis)
print(f"\nConversion lift: {conv_lift:.2f}x")
print(f"Profit lift: {profit_lift:.2f}x")
```

       recommended  conversion_rate  avg_profit
    0            0         0.038203    3.279489
    1            1         0.093699    9.324466
    
    Conversion lift: 2.45x
    Profit lift: 2.84x


## Model Version Performance Comparison

**Task 7:** Group by `model_version` and calculate: count of events, mean of `converted`, sum of `revenue`, sum of `inference_cost`, sum of `product_cost`, and sum of `profit`. 

Then calculate two different ROI metrics to understand both the AI-specific return and overall business profitability:
1. AI ROI - Measures return on the AI investment specifically (profit / inference_cost × 100)
2. Overall ROI - Measures total business profitability, including all costs (profit / total_costs × 100)


```python
version_performance = events.groupby('model_version').agg({
    'event_type': 'count',
    'converted': 'mean',
    'revenue': 'sum',
    'inference_cost': 'sum',
    'product_cost': 'sum',
    'profit': 'sum'
}).reset_index()

version_performance.columns = ['model_version', 'num_events', 'conversion_rate', 
                                'total_revenue', 'total_inference_cost', 
                                'total_product_cost', 'total_profit']

# AI ROI: Return on the AI investment specifically
version_performance['ai_roi_percentage'] = (version_performance['total_profit'] / 
                                             version_performance['total_inference_cost']) * 100

# Overall ROI: Total business profitability including all costs
total_costs = version_performance['total_inference_cost'] + version_performance['total_product_cost']
version_performance['overall_roi_percentage'] = (version_performance['total_profit'] / total_costs) * 100

print(version_performance.sort_values('ai_roi_percentage', ascending=False))

```

      model_version  num_events  conversion_rate  total_revenue  \
    0          v1.0       14800         0.060541      158234.26   
    1          v1.1       14840         0.066712      180973.53   
    2          v2.0       20360         0.065766      241108.87   
    
       total_inference_cost  total_product_cost  total_profit  ai_roi_percentage  \
    0                20.526            75060.80     83152.934      405110.269902   
    1                29.964            85036.84     95906.726      320073.174476   
    2                56.160           112914.28    128138.430      228166.720085   
    
       overall_roi_percentage  
    0              110.750487  
    1              112.742834  
    2              113.426512  


**Task 8:** Filter events to only rows where `recommended` equals 1. Group by `model_version` and calculate the mean conversion rate and the average profit per conversion (profit only for converted events).



```python
rec_only = events[events['recommended'] == 1]
rec_version = rec_only.groupby('model_version').agg({
    'converted': 'mean',
}).reset_index()
rec_version.columns = ['model_version', 'conversion_rate_when_rec']

# Average profit per conversion for recommended items
rec_profit = events[(events['recommended'] == 1) & (events['converted'])].groupby('model_version')['profit'].mean().reset_index()
rec_profit.columns = ['model_version', 'avg_profit_per_conversion']
rec_version = rec_version.merge(rec_profit, on='model_version')

print(rec_version.sort_values('conversion_rate_when_rec', ascending=False))
```

      model_version  conversion_rate_when_rec  avg_profit_per_conversion
    1          v1.1                  0.096916                 101.308080
    2          v2.0                  0.095620                 100.426402
    0          v1.0                  0.087548                  96.143344


## Regional Bias Detection

**Task 9:** Calculate the overall recommendation rate, then group by `region` to get recommendation rates for each region. Add columns showing the difference from average and a boolean `potential_bias` column that's True when the absolute difference exceeds 0.10 (10%).



```python
overall_rec_rate = events['recommended'].mean()
region_rec_rate = events.groupby('region')['recommended'].mean().reset_index()
region_rec_rate.columns = ['region', 'recommendation_rate']
region_rec_rate['diff_from_avg'] = region_rec_rate['recommendation_rate'] - overall_rec_rate
region_rec_rate['potential_bias'] = abs(region_rec_rate['diff_from_avg']) > 0.10

print(f"Overall recommendation rate: {overall_rec_rate:.2%}")
print("\n" + str(region_rec_rate.sort_values('recommendation_rate', ascending=False)))
print(f"\nRegions with potential bias (>10% difference): {region_rec_rate['potential_bias'].sum()}")
```

    Overall recommendation rate: 47.39%
    
      region  recommendation_rate  diff_from_avg  potential_bias
    0   East             0.515009       0.041149           False
    1  North             0.514831       0.040971           False
    3   West             0.427985      -0.045875           False
    2  South             0.425563      -0.048297           False
    
    Regions with potential bias (>10% difference): 0


**Task 10:** Create a contingency table using `pd.crosstab()` with `region` as rows and `recommended` as columns. Then use `chi2_contingency()` to test for statistical significance. Print the chi-square statistic, p-value, and interpret the results (p < 0.05 indicates significant bias).



```python
contingency_table = pd.crosstab(events['region'], events['recommended'])
chi2, p_value, dof, expected = chi2_contingency(contingency_table)

print("Chi-square test for Region vs Recommended:")
print(f"Chi-square statistic: {chi2:.2f}")
print(f"P-value: {p_value:.6f}")
print(f"Degrees of freedom: {dof}")
if p_value < 0.05:
    print("\n⚠️ SIGNIFICANT: Regional bias detected (p < 0.05)")
    print("The recommendation system treats regions differently.")
else:
    print("\n✓ NOT SIGNIFICANT: No statistical evidence of regional bias (p >= 0.05)")
```

    Chi-square test for Region vs Recommended:
    Chi-square statistic: 389.35
    P-value: 0.000000
    Degrees of freedom: 3
    
    ⚠️ SIGNIFICANT: Regional bias detected (p < 0.05)
    The recommendation system treats regions differently.


**Task 11:** Group by both `region` and `recommended`, calculating the mean of `converted` and mean of `profit`. Create a pivot table to show these metrics side-by-side for recommended vs not recommended in each region.



```python
region_performance = events.groupby(['region', 'recommended']).agg({
    'converted': 'mean',
    'profit': 'mean'
}).reset_index()
region_performance.columns = ['region', 'recommended', 'conversion_rate', 'avg_profit_per_event']

region_pivot = region_performance.pivot(index='region', columns='recommended', values=['conversion_rate', 'avg_profit_per_event'])
print(region_pivot)
```

                conversion_rate           avg_profit_per_event           
    recommended               0         1                    0          1
    region                                                               
    East               0.039788  0.090258             3.021162   8.822955
    North              0.039028  0.097994             3.545364   9.279027
    South              0.038462  0.090418             3.433458   9.171132
    West               0.035151  0.095158             2.978117  10.341977


## Age Group Bias Detection

**Task 12:** Group by `age` and calculate recommendation rates. Add columns for difference from average and potential_bias (>10% difference). Sort by age to see patterns.



```python
age_rec_rate = events.groupby('age')['recommended'].mean().reset_index()
age_rec_rate.columns = ['age', 'recommendation_rate']
age_rec_rate['diff_from_avg'] = age_rec_rate['recommendation_rate'] - overall_rec_rate
age_rec_rate['potential_bias'] = abs(age_rec_rate['diff_from_avg']) > 0.10

print(age_rec_rate.sort_values('age'))
print(f"\nAge groups with potential bias: {age_rec_rate['potential_bias'].sum()}")

```

       age  recommendation_rate  diff_from_avg  potential_bias
    0   18             0.515682       0.041822           False
    1   25             0.534640       0.060780           False
    2   35             0.532656       0.058796           False
    3   45             0.406444      -0.067416           False
    4   55             0.402812      -0.071048           False
    5   65             0.404771      -0.069089           False
    
    Age groups with potential bias: 0


**Task 13:** Create a contingency table for `age` vs `recommended` and perform a chi-square test. Print the results and interpret whether age bias exists.



```python
age_contingency = pd.crosstab(events['age'], events['recommended'])
chi2_age, p_value_age, dof_age, expected_age = chi2_contingency(age_contingency)

print("Chi-square test for Age vs Recommended:")
print(f"Chi-square statistic: {chi2_age:.2f}")
print(f"P-value: {p_value_age:.6f}")
if p_value_age < 0.05:
    print("\n⚠️ SIGNIFICANT: Age bias detected (p < 0.05)")
else:
    print("\n✓ NOT SIGNIFICANT: No statistical evidence of age bias (p >= 0.05)")
```

    Chi-square test for Age vs Recommended:
    Chi-square statistic: 782.60
    P-value: 0.000000
    
    ⚠️ SIGNIFICANT: Age bias detected (p < 0.05)


**Task 14:** Filter to converted events only and group by `age` to calculate the average `profit` per conversion for each age group. Sort by profit descending.



```python
age_profit = events[events['converted']].groupby('age')['profit'].mean().reset_index()
age_profit.columns = ['age', 'avg_profit_per_conversion']
print(age_profit.sort_values('avg_profit_per_conversion', ascending=False))
```

       age  avg_profit_per_conversion
    5   65                 103.958481
    3   45                 103.294598
    1   25                  96.518496
    2   35                  94.999627
    4   55                  86.578351
    0   18                  80.184508


## Customer Segment Analysis

**Task 15:** Filter to converted events and group by `customer_segment`. Calculate the count (num_conversions), mean of `revenue`, and mean of `profit`. Sort by average profit descending.



```python
segment_analysis = events[events['converted']].groupby('customer_segment').agg({
    'converted': 'count',
    'revenue': 'mean',
    'profit': 'mean'
}).reset_index()
segment_analysis.columns = ['customer_segment', 'num_conversions', 'avg_revenue', 'avg_profit']
print(segment_analysis.sort_values('avg_profit', ascending=False))
```

      customer_segment  num_conversions  avg_revenue  avg_profit
    1          premium              621   256.829952  135.381554
    2          regular             1629   172.871240   91.380913
    0           budget              975   142.787703   76.269965


**Task 16:** Filter to converted events and group by `customer_segment` to calculate total `profit` for each segment. Add a column showing each segment's percentage of total profit.



```python
segment_total_profit = events[events['converted']].groupby('customer_segment')['profit'].sum().reset_index()
segment_total_profit.columns = ['customer_segment', 'total_profit']
segment_total_profit['profit_percentage'] = (segment_total_profit['total_profit'] / segment_total_profit['total_profit'].sum()) * 100
print(segment_total_profit.sort_values('total_profit', ascending=False))
```

      customer_segment  total_profit  profit_percentage
    2          regular    148859.508          48.441943
    1          premium     84071.945          27.358739
    0           budget     74363.216          24.199319


## Model Version Cost-Effectiveness by Segment

**Task 17:** Group by both `model_version` and `customer_segment`. Calculate sum of `inference_cost` and sum of `profit`. Add an `roi_percentage` column: (profit / inference_cost) × 100. Sort by ROI descending.



```python
version_segment = events.groupby(['model_version', 'customer_segment']).agg({
    'inference_cost': 'sum',
    'profit': 'sum'
}).reset_index()
version_segment['roi_percentage'] = (version_segment['profit'] / version_segment['inference_cost']) * 100

print(version_segment.sort_values('roi_percentage', ascending=False))

```

      model_version customer_segment  inference_cost     profit  roi_percentage
    1          v1.0          premium           4.332  22858.308   527661.772853
    2          v1.0          regular          10.050  43250.400   430352.238806
    4          v1.1          premium           6.396  23812.424   372301.813634
    7          v2.0          premium          11.640  37380.920   321141.924399
    5          v1.1          regular          14.600  45345.660   310586.712329
    3          v1.1           budget           8.968  26748.642   298267.640500
    0          v1.0           budget           6.144  17044.226   277412.532552
    8          v2.0          regular          27.660  60216.180   217701.301518
    6          v2.0           budget          16.860  30541.330   181146.678529


**Task 18:** Using the previous result, create a pivot table with `model_version` as rows and `customer_segment` as columns, showing `roi_percentage`. Then print which model has the best ROI for each segment.



```python
roi_pivot = version_segment.pivot(index='model_version', columns='customer_segment', values='roi_percentage')
print(roi_pivot)
print("\nBest model for each segment:")
for segment in roi_pivot.columns:
    best_model = roi_pivot[segment].idxmax()
    best_roi = roi_pivot[segment].max()
    print(f"{segment}: {best_model} (ROI: {best_roi:.1f}%)")

```

    customer_segment         budget        premium        regular
    model_version                                                
    v1.0              277412.532552  527661.772853  430352.238806
    v1.1              298267.640500  372301.813634  310586.712329
    v2.0              181146.678529  321141.924399  217701.301518
    
    Best model for each segment:
    budget: v1.1 (ROI: 298267.6%)
    premium: v1.0 (ROI: 527661.8%)
    regular: v1.0 (ROI: 430352.2%)


## Statistical Bias Testing Across Model Versions

**Task 19:** Filter events to v1.0 and v2.0 separately. For each, create a contingency table of `region` vs `recommended` and run chi-square tests. Compare the p-values to see if regional bias improved or worsened.



```python
v1_data = events[events['model_version'] == 'v1.0']
v2_data = events[events['model_version'] == 'v2.0']

v1_contingency = pd.crosstab(v1_data['region'], v1_data['recommended'])
v2_contingency = pd.crosstab(v2_data['region'], v2_data['recommended'])

chi2_v1, p_v1, _, _ = chi2_contingency(v1_contingency)
chi2_v2, p_v2, _, _ = chi2_contingency(v2_contingency)

print("Regional bias comparison:")
print(f"v1.0 - Chi-square: {chi2_v1:.2f}, P-value: {p_v1:.6f}")
print(f"v2.0 - Chi-square: {chi2_v2:.2f}, P-value: {p_v2:.6f}")

if p_v2 < p_v1:
    print("\n⚠️ v2.0 shows STRONGER regional bias than v1.0")
elif p_v2 > 0.05 and p_v1 < 0.05:
    print("\n✓ v2.0 IMPROVED fairness - no significant regional bias detected")
else:
    print("\nBoth models show some regional patterns")

```

    Regional bias comparison:
    v1.0 - Chi-square: 1325.85, P-value: 0.000000
    v2.0 - Chi-square: 0.28, P-value: 0.963654
    
    ✓ v2.0 IMPROVED fairness - no significant regional bias detected


**Task 20:** Similar to Task 19, test for age bias across v1.0 and v2.0 model versions. Compare p-values and calculate the percentage improvement in fairness if v2.0 is better.



```python
v1_age_contingency = pd.crosstab(v1_data['age'], v1_data['recommended'])
v2_age_contingency = pd.crosstab(v2_data['age'], v2_data['recommended'])

chi2_v1_age, p_v1_age, _, _ = chi2_contingency(v1_age_contingency)
chi2_v2_age, p_v2_age, _, _ = chi2_contingency(v2_age_contingency)

print("Age bias comparison:")
print(f"v1.0 - Chi-square: {chi2_v1_age:.2f}, P-value: {p_v1_age:.6f}")
print(f"v2.0 - Chi-square: {chi2_v2_age:.2f}, P-value: {p_v2_age:.6f}")

if p_v2_age > p_v1_age:
    improvement = ((p_v2_age - p_v1_age) / p_v1_age) * 100
    print(f"\n✓ v2.0 shows {improvement:.1f}% improvement in age fairness")
else:
    print("\n⚠️ Age fairness did not improve in v2.0")
```

    Age bias comparison:
    v1.0 - Chi-square: 3.44, P-value: 0.632756
    v2.0 - Chi-square: 1900.54, P-value: 0.000000
    
    ⚠️ Age fairness did not improve in v2.0


## Final Recommendations and Summary

**Task 21:** Create a comprehensive summary report. For all three model versions, calculate: conversion rate, ROI, total profit, region bias p-value, and age bias p-value. Add a column indicating if the model has significant bias (p < 0.05 for either region or age).



```python
# Collect bias p-values for all versions
version_bias = []
for version in ['v1.0', 'v1.1', 'v2.0']:
    version_data = events[events['model_version'] == version]
    
    region_cont = pd.crosstab(version_data['region'], version_data['recommended'])
    _, p_region, _, _ = chi2_contingency(region_cont)
    
    age_cont = pd.crosstab(version_data['age'], version_data['recommended'])
    _, p_age, _, _ = chi2_contingency(age_cont)
    
    version_bias.append({
        'model_version': version,
        'region_bias_pvalue': p_region,
        'age_bias_pvalue': p_age
    })

bias_df = pd.DataFrame(version_bias)
summary = version_performance.merge(bias_df, on='model_version')
summary['has_bias'] = (summary['region_bias_pvalue'] < 0.05) | (summary['age_bias_pvalue'] < 0.05)

print("\n" + "="*80)
print("FINAL MODEL COMPARISON SUMMARY")
print("="*80)
print(summary[['model_version', 'conversion_rate', 'overall_roi_percentage', 'ai_roi_percentage', 'total_profit', 
               'region_bias_pvalue', 'age_bias_pvalue', 'has_bias']].to_string(index=False))
print("\nBias Interpretation: p-value < 0.05 indicates statistically significant bias")

```

    
    ================================================================================
    FINAL MODEL COMPARISON SUMMARY
    ================================================================================
    model_version  conversion_rate  overall_roi_percentage  ai_roi_percentage  total_profit  region_bias_pvalue  age_bias_pvalue  has_bias
             v1.0         0.060541              110.750487      405110.269902     83152.934       3.627345e-287         0.632756      True
             v1.1         0.066712              112.742834      320073.174476     95906.726        8.731995e-01         0.234890     False
             v2.0         0.065766              113.426512      228166.720085    128138.430        9.636543e-01         0.000000      True
    
    Bias Interpretation: p-value < 0.05 indicates statistically significant bias


## Your Recommendations

Based on your analysis, consider the following questions:

1. **Which model version delivers the best ROI?** Look at Task 7 results.

2. **Are there statistically significant biases?** Check p-values from Tasks 10, 13, 19, and 20.

3. **Which customer segments are most profitable?** Review Tasks 15-16.

4. **Should you use different models for different segments?** Examine Task 18.

5. **Did fairness improve with newer models?** Compare Tasks 19 and 20.

6. **What's your deployment recommendation?** Consider:
   - Deploy one model everywhere?
   - Use smart routing (different models for different segments)?
   - Roll back to v1.0 due to bias concerns?
   - Invest in v2.1 to address identified biases?

Write a 2-3 paragraph executive summary with your recommendations.



```python

```
