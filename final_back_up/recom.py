# from flask import Flask, jsonify, request
# from pyspark.sql import SparkSession
# from pyspark.ml.recommendation import ALS
# from pyspark.sql.functions import col

# # Initialize Flask app
# app = Flask(__name__)

# spark = SparkSession.builder \
#     .appName("RecommendationSystemAPI") \
#     .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem") \
#     .config("spark.executor.extraJavaOptions", "-Djava.library.path=") \
#     .config("spark.cassandra.connection.host", "172.22.213.208") \
#     .getOrCreate()

# # Load the pre-trained ALS model
# model = ALS.load(r"C:\Users\srina\OneDrive\Desktop\backup_folder\final_back_up\als_model")

# # Dummy product data for demonstration (you can replace this with data from MySQL)
# product_data = spark.read.format("jdbc").option("url", "jdbc:mysql://127.0.0.1:3306/online_store").option("dbtable", "product_details").load()

# @app.route('/recommendations', methods=['GET'])
# def get_recommendations():
#     # Get the user_id from the query parameters
#     user_id = request.args.get('user_id', type=int)
    
#     # Generate top 5 recommendations for the user
#     recommendations = model.recommendForAllUsers(5)
    
#     # Filter recommendations for the requested user_id
#     user_recommendations = recommendations.filter(col("user_id") == user_id)
    
#     # Retrieve the product IDs from recommendations
#     recommended_products = user_recommendations.select("recommendations.product_id").collect()
    
#     # If recommendations are found, get product details
#     if recommended_products:
#         # Get the product details for the recommended product IDs
#         product_ids = [row["product_id"] for row in recommended_products[0]["recommendations"]]
#         recommended_products_details = product_data.filter(col("product_id").isin(product_ids)).collect()
        
#         # Convert product details to a list of dictionaries
#         product_list = [
#             {
#                 "product_id": row["product_id"],
#                 "product_name": row["product_name"],
#                 "price": row["price"]
#             }
#             for row in recommended_products_details
#         ]
        
#         return jsonify({"user_id": user_id, "recommendations": product_list})
#     else:
#         return jsonify({"error": "No recommendations found for this user."})

# if __name__ == '__main__':
#     app.run(debug=True)
