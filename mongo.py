from pymongo import MongoClient
from dotenv import load_dotenv
import streamlit as st
import os
import time

def load_env():
    st.write("loading the mogno_url and database")
    # this will load the environment variable from .env file into our environment
    load_dotenv()

def get_mongo():
    mongo_url = os.getenv("MONGO_URL")
    if mongo_url:
        conn = MongoClient(mongo_url,tlsAllowInvalidCertificates=True)
        st.write("connection established...")
        return conn
    else:
        st.write("MONGO_URL NOT FOUND!!")

# accessing the database
def get_db(connect: MongoClient, db_name: str, collection_name:str):
    "creating database and a collection and returns collection"
    if connect:
        if db_name:
            if collection_name:
                st.write("database and collection found...")
                db = connect[db_name]
                collection = db[collection_name]
                st.write("database and collection created...")
                return collection
            else:
                st.write("collection_name not found...")
        else:
            st.write("db_name not found...")
    else:
        st.write("connection not found...")

# insert a document(row) into collection
def insert_doc(data,coll):
    st.write("inserting document...")
    st.write("uploading the document to the database...")
    coll.insert_many(data)
    st.success("Done uploading")

# find the document
def print_one(key,coll):
    print("finding one document...")
    result  = coll.find_one(key)
    print(result)

def mongo_upload(data,db_name="testdb",coll_name="test_coll"):
    load_env()
    connection = get_mongo()
    time.sleep(3)
    coll = get_db(connection,db_name,coll_name)
    time.sleep(3)
    insert_doc(data,coll)
    
    # print_one({"name":"apple"},coll=coll)

if __name__ == "__main__":
    mongo_upload()