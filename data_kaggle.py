import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

dataset_path = "/home/codespace/.cache/kagglehub/datasets/promptcloud/amazon-home-furnishings-dataset/versions/1/marketing_sample_for_amazon_com-amazon_home_improvement_data__20200101_20200331__5k_data.ldjson"


data = []
with open(dataset_path, "r", encoding="utf-8") as file:
    for line in file:
        data.append(json.loads(line))  # Each line is a JSON object


df = pd.DataFrame(data)

columns_to_keep = [
    "product_name", "brand", "sales_price", "discount_percentage", "rating",
    "no__of_reviews", "amazon_prime__y_or_n", "best_seller_tag__y_or_n"
]
df = df[columns_to_keep]


df["sales_price"] = pd.to_numeric(df["sales_price"], errors="coerce")


df["discount_percentage"] = df["discount_percentage"].str.replace("%", "").astype(float) / 100

df["rating"] = pd.to_numeric(df["rating"], errors="coerce")


df["no__of_reviews"] = pd.to_numeric(df["no__of_reviews"], errors="coerce")

df.fillna({
    "sales_price": df["sales_price"].median(),
    "discount_percentage": 0,
    "rating": df["rating"].median(),
    "no__of_reviews": 0
}, inplace=True)


brand_analysis = df.groupby("brand")[["discount_percentage", "rating"]].mean()


high_discount_good_rating = brand_analysis[
    (brand_analysis["discount_percentage"] > 0.3) & 
    (brand_analysis["rating"] > 4.0)
]


print("Brands with High Discounts and Good Ratings:")
print(high_discount_good_rating)

plt.figure(figsize=(12, 6))
sns.barplot(
    x=high_discount_good_rating.index, 
    y=high_discount_good_rating["discount_percentage"], 
    label="Average Discount Percentage", color="orange"
)
sns.barplot(
    x=high_discount_good_rating.index, 
    y=high_discount_good_rating["rating"], 
    label="Average Rating", color="blue", alpha=0.5
)
plt.xticks(rotation=45)
plt.title("Brands with High Discounts and Good Ratings")
plt.legend()
plt.savefig("High_Discount_Good_Rating_Brands.png")
plt.show()


price_bins = [0, 50, 100, 200, 500, 1000, df["sales_price"].max()]
price_labels = ["0-50", "50-100", "100-200", "200-500", "500-1000", "1000+"]
df["price_range"] = pd.cut(df["sales_price"], bins=price_bins, labels=price_labels)

reviews_by_price_range = df.groupby("price_range")["no__of_reviews"].sum()


plt.figure(figsize=(10, 6))
sns.barplot(x=reviews_by_price_range.index, y=reviews_by_price_range.values, palette="viridis")
plt.title("Number of Reviews by Price Range")
plt.xlabel("Price Range")
plt.ylabel("Number of Reviews")
plt.savefig("Reviews_By_Price_Range.png")
plt.show()

correlation_matrix = df[["sales_price", "discount_percentage", "rating", "no__of_reviews"]].corr()


plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
plt.title("Correlation Matrix of Key Factors")
plt.savefig("Correlation_Matrix.png")
plt.show()

plt.figure(figsize=(8, 6))
sns.scatterplot(x=df["sales_price"], y=df["rating"])
plt.title("Sales Price vs Ratings")
plt.xlabel("Sales Price")
plt.ylabel("Rating")
plt.savefig("Sales_Price_vs_Ratings.png")
plt.show()

plt.figure(figsize=(8, 6))
sns.scatterplot(x=df["sales_price"], y=df["no__of_reviews"])
plt.title("Sales Price vs Number of Reviews")
plt.xlabel("Sales Price")
plt.ylabel("Number of Reviews")
plt.savefig("Sales_Price_vs_Reviews.png")
plt.show()

high_rated_low_price = df[
    (df["rating"] >= 4.5) & 
    (df["sales_price"] < df["sales_price"].median())
]

plt.figure(figsize=(8, 6))
sns.scatterplot(
    x=high_rated_low_price["sales_price"], 
    y=high_rated_low_price["rating"]
)
plt.title("High-Rated, Low-Priced Products")
plt.xlabel("Sales Price")
plt.ylabel("Rating")
plt.savefig("High_Rated_Low_Priced_Products.png")
plt.show()
