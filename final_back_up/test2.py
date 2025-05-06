import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col, collect_list, expr
from pyspark.ml.recommendation import ALS

# Set the environment variable for Cassandra connector
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 pyspark-shell'

# Initialize Spark session
spark = SparkSession.builder \
    .appName("RecommendationSystem") \
    .config("spark.cassandra.connection.host", "172.22.213.208") \
    .config("spark.hadoop.io.nativeio", "false") \
    .getOrCreate()

# Step 1: Load data from Cassandra and MySQL
# Cassandra - User Interactions Data
interaction_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="user_interactions1", keyspace="ecommerce") \
    .load()

# MySQL - Product Details Data
product_df = spark.read.jdbc(
    url="jdbc:mysql://127.0.0.1:3306/online_store",
    table="product_details",
    properties={"user": "root", "password": "220818", "driver": "com.mysql.cj.jdbc.Driver"}
)

# Show the data to verify
interaction_df.show(5)
product_df.show(5)

# Step 2: Prepare the data for recommendation model
interaction_df = interaction_df.select("user_id", "product_id", "action") \
    .filter(interaction_df.action == "add_to_cart") \
    .withColumn("rating", lit(1))

# Step 3: Train ALS model
als = ALS(userCol="user_id", itemCol="product_id", ratingCol="rating", nonnegative=True, implicitPrefs=True)
model = als.fit(interaction_df)
#model.write().overwrite().save("als_model")

# Step 4: Make recommendations
user_recommendations = model.recommendForAllUsers(5)

# Extract product IDs from recommendation structs into a plain list
from pyspark.sql.functions import expr

user_recommendations_flat = user_recommendations.withColumn(
    "recommended_items",
    expr("transform(recommendations, x -> x.product_id)")
).select("user_id", "recommended_items")

# Step 5: Write recommendations to Cassandra
user_recommendations_flat.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="user_recommendations", keyspace="ecommerce", **{"confirm.truncate": "true"}) \
    .mode("overwrite") \
    .save()

