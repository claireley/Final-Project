import uvicorn
from fastapi import FastAPI
import pymysql
import os
from dotenv import load_dotenv

# Create an app with an instance of the class FastAPI
app = FastAPI()

def get_db_connection():
    
    load_dotenv()
    username = os.getenv('db_username')
    password = os.getenv('db_password')

    try:
        connection = pymysql.connect(
            host='localhost',
            user=username,
            password=password,
            database='ironhack_final_project',              
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


@app.get("/")
def hello():
    return "Hello world!"    

@app.get("/customer_lifetime_value/{customer_id}")
def customer_lifetime_value(customer_id: int):
    if not customer_id:
        return {"error": "Cust_id is required."}, 400

    connection = get_db_connection()
    if not connection:
        return {"error": "Failed to connect to database."}, 400

    with connection.cursor() as cursor:
        query = """
            SELECT cust_id, fruits + wines + sweets + meat + gold + fish AS Customer_Spend
            FROM product_spend
            WHERE cust_id = %s;
        """
        cursor.execute(query, (customer_id,))
        clv = cursor.fetchall()

    connection.close()
    return clv

@app.get("/customer_profile/{customer_id}")
def customer_profile(customer_id: int):
    if not customer_id:
        return {"error": "Cust_id is required."}, 400

    connection = get_db_connection()
    if not connection:
        return {"error": "Failed to connect to database."}, 400

    with connection.cursor() as cursor:
        query = """
            SELECT *
            FROM customer as c
            JOIN behaviour as b on c.cust_id=b.cust_id
            JOIN channels as ch on c.cust_id=ch.cust_id
            JOIN cluster as cl on c.cluster_id=cl.cluster_id
            JOIN product_spend as p on c.cust_id=p.cust_id
            WHERE c.cust_id = %s;
        """
        cursor.execute(query, (customer_id,))
        cp = cursor.fetchall()

    connection.close()
    return cp


@app.get("/cluster/{cluster_number}")
def cluster_members(cluster_number: int):
    if not cluster_number:
        return {"error": "Cluster Number is required."}, 400

    connection = get_db_connection()
    if not connection:
        return {"error": "Failed to connect to database."}, 400

    with connection.cursor() as cursor:
        query = """
            SELECT cust_id, cluster_name
            FROM customer as c
            JOIN cluster as cl
                ON c.cluster_id = cl.cluster_id
            WHERE c.cluster_id = %s;
        """
        cursor.execute(query, (f"%{cluster_number}%",))
        clust = cursor.fetchall()

    connection.close()
    return clust


@app.get("/bank_job_profiles")
def bank_job_profile():
    connection = get_db_connection()
    if not connection:
        return {"error": "Failed to connect to database."}, 400

    with connection.cursor() as cursor:
        query = """SELECT bc.job AS Job, count(bank_cust_id) as Number_Customers, round(avg(income),2) as Estimated_Income,
        round(avg(balance),2) as Average_Balance, round(AVG(conversion)*100,2) AS Conversion_Rate
        FROM bank_customer as bc
        JOIN bank_salary as bs
        ON bc.job = bs.job
        GROUP BY bc.job
        ORDER BY count(bank_cust_id) DESC; """
        cursor.execute(query)
        bj_prof = cursor.fetchall()

    connection.close()
    return bj_prof



if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
