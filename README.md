# Amazon E-Commerce Analysis

Cleaning, analysis and visualization of Amazon sales data to evaluate product performance, cancellation patterns, and regional demand.

- Timeframe: between March 31st, 2022 and June 29th, 2022
- Country: India

---

## Table of Contents

#### 1. [Tree Directory](#tree-directory)

#### 2. [Data Preprocessing](#data-preprocessing)

#### 3. Analysis

3.1 [Sales Analysis](#sales-analysis)
3.2 [Top Sellers Analysis](#top-sellers-analysis)
3.3 [Sales Aggregates](#sales-aggregates)
3.4 [Cancellation Patterns](#cancellation-pattern-analysis)
3.5 [Regional Analysis](#regional-analysis)

#### 4. [License](#license)

---

## Tree Directory 

```
Amazon_ECommerce_Analysis/
├───data
│   ├───processed
│   └───raw
├───notebooks
├───outputs
│   ├───figures
│   └───tables
└───src
```

## Data Preprocessing
Prepared dataset for analysis. Full cleaning process accessible in notebooks/pandas_cleaning.ipynb and sql_cleaning.txt.  
  
Summary:
- Normalized columns and values, converted corresponding data types, dropped columns with no info, and reconciled columns with duplicate info.
- Singled out true duplicate orders vs orders with multiple parts. Dropped true duplicate orders. 
- Imputed over 30k missing/incorrect values (payment and address info) in SQL through a detailed recovery process by matching orders with same Asin or postal code.
- Ensured data distributions remained coherent and investigated high variance and outliers.
- Feature engineering for sales and cancellations analysis, as well as regional demand.


## Analysis
Analysis process accessible through notebooks/visualization.ipynb. If you would like to run the analysis code yourself, navigate to project directory in your terminal and use pip to install requirements:

```
pip install -r requirements.txt
```

Then run:

```
python src/visualization.py
```

This will regenerate outputs from processed data files. 

### Sales Analysis

#### Inventory
Let's start by inspecting inventory that generated at least one sale. How many items are there per category?

![Item Count by Category](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/item_count_by_category.png "Item Count By Category")  


#### Item Order Count and Revenue 
Sales data is highly skewed. I performed an 80/20 split to analyze top sellers separately.  

Let's start with regular sales. Over the span of three months, how many orders should we expect for each item per category? How much revenue would these items generate? Let's look at distributions.  

![Item Order Count and Revenue Distributions](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/item_distributions_by_category.png "Item Order Count and Revenue Distributions")  

Note that, in each category, 50% of regular selling items have less than 7 orders over the span of 3 months. This implies 50% of items are low selling, and most revenue and order count is driven by top 50%. This isn't necessarily a bad thing:

- It is possible that having a large variety of items drives consumers to use Amazon more often, leading to better sales for top 50% items. 
- The items might be produced in low numbers and sold over long periods of time, which would synergize with the effect above by increasing item variety.
- It also might indicate that a large variety of vendors are selling through Amazon.


#### Skewness
Let's investigate this effect further by comparing medians with means. We'll obtain a 95% confidence intervals for the mean and median of each category.

![Item Order Count Skewness](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/order_count_skewness.png "Item Order Count Skewness")

![Item Revenue Skewness](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/revenue_skewness.png "Item Revenue Skewness")

Most categories have a significant skew. Note this is bottom 80% of sales and we are not yet considering top sellers, which would further exaggerate the skew. It would be worthwhile to study this effect in more detail to determine the cause and perform the corresponding cost-benefit analysis.

- If consumers are highly selective for these categories, it would be beneficial to increase R&D spending to improve target advertising and understand consumer preferences.
- If cost of having low-selling items is low and variety drives consumers to use Amazon more frequently, it would be beneficial to test optimal levels of variety and update search results accordingly. For example, display one desirable item for every 4 low-selling items and test whether this increases sales.
- If cost is high and the above effect is not substantial enough to offset cost, it would be beneficial to look for features that distinguish high vs low selling items and decrease variety.


#### Price Distributions
Next, let's look at price distributions per category both stacked and individually. Item pricing is given by median order price. What are consumers willing to pay per category? We will also look at percentage of purchases that are discounted.

![Order Density and Discount Percentage](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/order_density_and_discount.png "Order Density and Discount Percentage")

- As seen earlier, vast majority of sales are of kurtas and sets. 
- Consumers are willing to pay higher prices for sets and western dress.
- Majority of purchases were discounted. Likely beneficial to increase an item's base price then discount to desired price.  


Let's look at the price distributions of each category separately.

![Price Distributions](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/price_distribution.png "Price Distributions")

- Note that most categories have two or more price zones, likely reflecting different levels of demand depending on item quality. This serves as a pricing guide depending on category and item quality.


### Top Sellers Analysis 
Like before, we will start by examining item order count and revenue distributions per category.

![Top Sellers Order Count and Revenue Distributions](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/topseller_distributions_by_category.png "Top Sellers Order Count and Revenue Distributions") 

Western dress, kurta, and set categories have long tail ends, which implies top selling items far exceed others in sales. This can be explained by:
- Effective discounting or advertising. Perhaps some items are advertised by influencers or are made by reputable brands.
- Simple design that appeals to a broad range of consumers.


Let's investigate these categories further for any causal insight. 

#### Western Dress Top Sellers
We will start with western dress.

![Top 20 WD Products](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/top20_WDproducts.png
 "Top 20 WD Products")

- Note western dress top sellers are heavily discounted. Considering higher prices in this category, consumers are likely more responsive to discounting. 
- Google searched top three sellers. All three are loose blue dresses with repetitive white print. A simple design appealing to a wide market with a high discount generates high sales volume. 

Example:
[Top WD Item](https://m.media-amazon.com/images/I/7137DbpKpVL._AC_SY606_.jpg "Top WD Item")

#### Kurta Top Sellers

![Top 20 Kurta Products](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/top20_Kproducts.png
 "Top 20 Kurta Products")

- Kurta top sellers are significantly less discounted. Consumers are willing to pay full price given the right item.
- Top three products are body fitting red dresses with geometric design. Again, a simple pattern appealing to a broad market. These dresses are more appropriate for going out, which explains consumers' willingness to pay higher prices.

Example:
[Top Kurta Item](https://m.media-amazon.com/images/I/81BLgL+FteL._AC_SY741_.jpg "Top Kurta Item")



#### Set Top Sellers

![Top 20 Set Products](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/top20_Set_products.png
 "Top 20 Set Products")

- Set top sellers are also significantly less discounted than western dresses, but more so than kurtas.
- Top three products have darker color and complex geometric design. These dresses are more appropriate for special occasions, which explains consumers' willingness to pay even higher prices.


Example:
[Top Set Item](https://m.media-amazon.com/images/I/91ktsnyWQ8L._AC_SY606_.jpg "Top Set Item")
  
  
#### Top Sellers Price Distributions
Like before, we will examine item pricing by category in both a stacked and individual format, along with discounting percentages. Recall item pricing is given by median order price. 

![Top Sellers Distributions](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/topseller_order_density_and_discount.png
 "Top Sellers Distributions")

![Top Sellers Pricing](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/topseller_price_distribution.png
 "Top Sellers Pricing")

- Note that regular selling items order density was dominated by kurta items, whereas top sellers' order density is dominated by sets. 
- Recall the two distribution peaks likely represent high vs low quality items. Set top sellers have a larger "high quality item" volume relative to regular selling items.
- Western dress top sellers have higher "low quality item" volume relative to regular selling items.

### Sales' Aggregates
To finish off sales analysis, we will look at sales' aggregates of top sellers and regular sellers side-by-side.

![Sales' Aggregates](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/sales_aggregates.png
 "Sales' Aggregates")

- Most revenue and order count is concentrated in top selling items, despite representing only 20% of total items.
- For regular selling items, kurta category has the highest order count and is about half the number of orders in the top selling kurta category. This can't be explained by price levels because the price distributions do not significantly differ between top and regular selling kurtas. This may indicate there is demand for variety in this category since less demand is concentrated in top selling items.

## Cancellation Pattern Analysis

We will start by looking at relative cancellation percentages against each categorical feature. It is important to note here that, due to poor data collection, we will not be able to meaningfully distinguish between cancelled and returned orders. This is due to the fact that a large proportion of returned orders were labelled by shipping services as cancelled. The main drawback here is that we won't be able to analyze return shipping costs. 

From here on, I will refer to both as "cancelled" orders to avoid redundancy. Let's look at cancellations against shipping service level.

![Ship Service Level vs Cancellation](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/cancellation_percentage_by_ship_service_level.png
 "Ship Service Level vs Cancellation")

- As expected, expedited shipping predicts fewer cancellations. Surprisingly, orders with expedited shipping are still cancelled 13.4% of the time. Orders with standard shipping are about 1.78x more likely to be cancelled.


Next, shipping fulfillment service vs cancellations.

![Fulfillment Service vs Cancellation](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/cancellation_percentage_by_fulfillment.png
 "Fulfillment Service vs Cancellation")

- Easy Ship has higher cancellation rates. It would be worthwhile to investigate if this shipping service is correlated with higher wait times or damaged items.


Sales channel vs cancellations.

![Sales Channel vs Cancellation](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/cancellation_percentage_by_sales_channel.png
 "Sales Channel vs Cancellation")

- Non-amazon sales channel has 100% cancellation rate. These orders are likely fraudulent.


Category vs cancellations.

![Category vs Cancellation](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/cancellation_percentage_by_category.png
 "Category vs Cancellation")

- Of the three predominant categories, kurtas have lowest cancellation rate. But all three are comparable.
- Cancellation percentages closely follow order patterns. This is likely because items with higher demands are more scrutinized by buyers. 


Cancellation rate of business-to-business vs business-to-customer transactions

![B2B vs Cancellation](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/cancellation_percentage_by_b2b.png
 "B2B vs Cancellation")

- As expected, B2B transactions have lower cancellation rate.


Item size vs cancellation rate

![Size vs Cancellation](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/cancellation_percentage_by_size.png
 "Size vs Cancellation")

- Smaller sizing correlates with higher cancellation percentages in a semi linear fashion. This is likely due to vanity sizing choices by consumers.


Is there a relationship between order amount or quantity and cancellation rate? Let's check correlation matrix.

|              | amount | quantity | is_cancelled |
|--------------|--------|----------|--------------|
| amount       | 1.0    |          |              |
| quantity     | 0.1631 | 1.0      |              |
| is_cancelled | -0.0142| 0.0097   | 1.0          |

- No linear correlation between total amount, quantity, and cancellation percentage.


#### Regional Analysis

Top 10 regions by order count:

[Top Ten Regions](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/tables/regional_top_categories.csv)


Which categories are in highest demand in top 10 regions?


![Category Demand by Region](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/regional_orders_by_category.png
 "Category Demand by Region")

Top states' top categories:
- Note top 2 states have even split between sets and kurtas
- Significant preference for kurtas in Tamil Nadu
- Significant preference for sets in Uttar Pradesh and Delhi


Let's look at percentages so we can cross-reference demand levels more easily


![Category Demand Percentage by Region](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/regional_order_percentages_by_category.png
 "Category Demand Percentage by Region")


- Largely similar demand levels to global data patterns. We can cross reference this list for ad targeting. 


#### Regional Cancellation Patterns

Let's look at cancellation patterns by region and order density. Darker colors correspond to higher order density

![Category Demand by Region](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/cancellation_percentage_by_state.png
 "Cancellation Percentage by State")

- Top states have similar cancellation percentage of about 15%
- 33 orders with unknown address have unusually high cancellation rate. Error or evidence of fraudulent orders?

Zoom in on top 10 states/territories to see if any states have high cancellation rate.

![Category Demand by Region](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/cancellation_rate_heatmap.png
 "Cancellation Percentage by State Top 10")

- Kerala has high cancellation rates
- Uttar Pradesh and Andhra Pradesh have high western dress cancellation rates


It seems worthwhile to highlight deviations in cancellation rates for top 10 states by category

![Category Demand by Region](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/cancellation_rate_deviation.png
 "Cancellation Percentage Deviations")

- Note that Maharashtra has low cancellation rate for western dress.

### License
MIT license