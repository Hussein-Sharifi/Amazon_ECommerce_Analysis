# Amazon E-Commerce Analysis

Cleaning, analysis and visualization of Amazon sales data to evaluate product performance, cancellation patterns, regional demand, and revenue.

- Timeframe: between March 31st, 2022 and June 29th, 2022
- Country: India

### Tree Directory 

```
Amazon_ECommerce_Analysis/
├───data
│   ├───processed
│   └───raw
├───notebooks
├───outputs
│   ├───figures
│   ├───models
│   └───tables
└───scripts
```

## Data Preprocessing
Prepared dataset for analysis. Full cleaning process accessible in notebooks/pandas_cleaning.ipynb and sql_cleaning.txt.  
  
Summary:
- Normalized columns and values, converted corresponding data types, dropped columns with no info, and reconciled columns with duplicate info.
- Singled out true duplicate orders vs orders with multiple parts. Dropped true duplicate orders. 
- Imputed over 30k missing/incorrect values (payment and address info) in SQL through a detailed recovery process by matching orders with same Asin or postal code.
- Ensured data distributions remained consistent and investigated high variance and outliers.
- Feature engineering for sales and cancellations analysis, as well as regional demand and revenue.


## Analysis
Analysis process accessible through notebooks/visualization.ipnyb, or, if you would like to run the analysis code yourself, src/visualization.py.

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
- It also might indicate that a large variety of vendors are selling through Amazon, regardless of profitability level.


#### Skewness
Let's investigate this effect further by looking at data skewness. We'll obtain a 95% confidence intervals for the mean and median of each category.

![Item Order Count Skewness](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/order_count_skewness.png "Item Order Count Skewness")

![Item Revenue Skewness](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/revenue_skewness.png "Item Revenue Skewness")

Kurtas, sets, blouses, and tops have a pronounced right skew. Note this is bottom 80% of sales and we are not yet considering top sellers, which would further exaggerate the skew. It would be worthwhile to study this effect in more detail to determine the cause and perform the corresponding cost-benefit analysis.

- If consumers are highly selective for these categories, it would be beneficial to increase R&R spending to improve target advertising and understand consumer preferences.
- If cost of having low-selling items is low and variety drives consumers to use Amazon more frequently, it would be beneficial to test optimal levels of variety and update search results accordingly. For example, display one desirable item for every 4 low-selling items and test whether this increases sales.
- If cost is high and the above effect is not substantial enough to offset cost, it would be beneficial to look for features that distinguish high vs low selling items and decrease variety.


#### Price Distributions
Next, let's look at price distributions. We will look at median price for each item. What are consumers willing to pay per category? We will also look at percentage of purchases that are discounted.

![Order Density and Discount Percentage](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/order_density_and_discount.png "Order Density and Discount Percentage")

- As seen earlier, vast majority of sales are of kurtas and sets. 
- Consumers are willing to pay higher prices for sets and western dress.
- Majority of purchases were discounted. Discounting drives higher sales, and it is beneficial to increase an item's base price then discount to the desirable price. 


We will zoom in and look at price distributions of each category separately.

![Price Distributions](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/price_distribution.png "Price Distributions")

- Note that most categories have two price zones, likely reflecting low vs high quality items. This serves as a pricing guide depending on category and item quality.


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
- Top three products are body fitting red dresses with geometric design. Again, a simple pattern appealing to a broad market. These dresses are more appropriate for special occasions, which explains consumers' willingness to pay higher prices.

Example:
[Top Kurta Item](https://m.media-amazon.com/images/I/81BLgL+FteL._AC_SY741_.jpg "Top Kurta Item")



#### Set Top Sellers

![Top 20 Set Products](https://github.com/Hussein-Sharifi/Amazon_ECommerce_Analysis/blob/master/outputs/figures/top20_Set_products.png
 "Top 20 Set Products")

- Set top sellers are also significantly less discounted than western dresses, but more so than kurtas.
- Top three products have darker color and complex geometric design. Likely reflects consumers' willingness to pay higher prices for set items.

Example:
[Top Set Item](https://m.media-amazon.com/images/I/91ktsnyWQ8L._AC_SY606_.jpg "Top Set Item")



### License
MIT license