import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pyspark.ml.recommendation import ALS

# Set the environment variables for Cassandra connector
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
# Assuming 'user_id' is the user and 'product_id' is the item to be recommended
# Create a user-item interaction matrix for ALS model
interaction_df = interaction_df.select("user_id", "product_id", "action").filter(interaction_df.action == "add_to_cart")

# Convert action to a rating (1 for interaction)
interaction_df = interaction_df.withColumn("rating", lit(1))

# Step 3: Train ALS model
als = ALS(userCol="user_id", itemCol="product_id", ratingCol="rating", nonnegative=True, implicitPrefs=True)
model = als.fit(interaction_df)
model.write().overwrite().save("als_model")



# Step 4: Make recommendations
user_recommendations = model.recommendForAllUsers(5)

# Show recommendations
user_recommendations.show(5)
