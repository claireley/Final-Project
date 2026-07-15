from flask import Flask, jsonify, request
from flasgger import Swagger
import pymysql
import os
from dotenv import load_dotenv

app = Flask(__name__)
swagger = Swagger(app)  # renders docs at /apidocs


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
    """
    Get a customer's total spend across all product categories
    ---
    parameters:
      - name: customer_id
        in: path
        type: integer
        required: true
        description: The customer's unique ID
    responses:
      200:
        description: Customer ID and total spend (sum of fruits, wines, sweets, meat, gold, fish)
    """
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
    """
    Get the full customer profile
    ---
    parameters:
      - name: customer_id
        in: path
        type: integer
        required: true
        description: The customer's unique ID
    responses:
      200:
        description: Complete customer profile joining customer, behaviour, channels, cluster, and product_spend tables
    """
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
    """
    Get customers belonging to a given cluster (paginated)
    ---
    parameters:
      - name: cluster_number
        in: path
        type: integer
        required: true
        description: The cluster ID to filter by
      - name: page
        in: query
        type: integer
        required: false
        default: 1
      - name: page_size
        in: query
        type: integer
        required: false
        default: 20
    responses:
      200:
        description: Paginated list of customers in the specified cluster
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database."}), 400

    # Pagination params, e.g. /cluster/1?page=2&page_size=10
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    offset = (page - 1) * page_size

    with connection.cursor() as cursor:
        query = """
            SELECT cust_id, cluster_name
            FROM customer as c
            JOIN cluster as cl
                ON c.cluster_id = cl.cluster_id
            WHERE c.cluster_id = %s
            LIMIT %s OFFSET %s;
        """
        cursor.execute(query, (cluster_number, page_size, offset))
        clust = cursor.fetchall()

        # total count for this cluster, so the response can say how many pages exist
        count_query = """
            SELECT COUNT(*) as total
            FROM customer
            WHERE cluster_id = %s;
        """
        cursor.execute(count_query, (cluster_number,))
        total = cursor.fetchone()['total']

    connection.close()

    return jsonify({
        "page": page,
        "page_size": page_size,
        "total_results": total,
        "total_pages": (total + page_size - 1) // page_size,
        "results": clust
    })


@app.route("/bank_job_profiles")
def bank_job_profile():
    """
    Get aggregated statistics per occupation from the Bank Marketing dataset
    ---
    responses:
      200:
        description: For each job, the number of customers, estimated income, average balance, and conversion rate
    """
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