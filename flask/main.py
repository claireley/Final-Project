from flask import Flask, jsonify
import pymysql
import os
from dotenv import load_dotenv

app = Flask(__name__)


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

@app.route("/")
def index():
    return "<h1>Sci-Kitchen Luxury Foods API</h1>"

@app.route("/customer_lifetime_value/<int:customer_id>")
def customer_lifetime_value(customer_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database."}), 400

    with connection.cursor() as cursor:
        query = """
            SELECT cust_id, fruits + wines + sweets + meat + gold + fish AS Customer_Spend
            FROM product_spend
            WHERE cust_id = %s;
        """
        cursor.execute(query, (customer_id,))
        clv = cursor.fetchall()

    connection.close()
    return jsonify(clv)


@app.route("/customer_profile/<int:customer_id>")
def customer_profile(customer_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database."}), 400

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
    return jsonify(cp)


@app.route("/cluster/<int:cluster_number>")
def cluster_members(cluster_number):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database."}), 400

    with connection.cursor() as cursor:
        query = """
            SELECT cust_id, cluster_name
            FROM customer as c
            JOIN cluster as cl
                ON c.cluster_id = cl.cluster_id
            WHERE c.cluster_id = %s;
        """
        cursor.execute(query, (cluster_number,))
        clust = cursor.fetchall()

    connection.close()
    return jsonify(clust)


@app.route("/bank_job_profiles")
def bank_job_profile():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database."}), 400

    with connection.cursor() as cursor:
        query = """
            SELECT bc.job AS Job, count(bank_cust_id) as Number_Customers,
                round(avg(income),2) as Estimated_Income,
                round(avg(balance),2) as Average_Balance,
                round(AVG(conversion)*100,2) AS Conversion_Rate
            FROM bank_customer as bc
            JOIN bank_salary as bs
                ON bc.job = bs.job
            GROUP BY bc.job
            ORDER BY count(bank_cust_id) DESC;
        """
        cursor.execute(query)
        bj_prof = cursor.fetchall()

    connection.close()
    return jsonify(bj_prof)


if __name__ == "__main__":
    app.run(debug=True)