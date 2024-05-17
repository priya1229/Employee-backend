from pymongo import MongoClient
import ssl

uri = 'mongodb+srv://admin:priya@cluster0.l6dotpe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(uri)

try:
    client.server_info()  # Trigger an exception if it can't connect
    print("Connected to MongoDB Atlas")
except Exception as e:
    print(f"Connection error: {e}")
