USE ironhack_final_project;

SELECT *
FROM customer AS c
JOIN behaviour AS b 
	ON c.cust_id=b.cust_id
JOIN channels AS ch 
	ON c.cust_id=ch.cust_id
JOIN cluster AS cl 
	ON c.cluster_id=cl.cluster_id
JOIN product_spend AS p 
	ON c.cust_id=p.cust_id;

SELECT *
FROM bank_customer AS bc
JOIN bank_salary AS bs 
	ON bc.job=bs.job;

SELECT 
	bank_cust_id, 
    balance, 
    campaign, 
    bc.job, 
    income
FROM bank_customer AS bc
JOIN bank_salary AS bs 
	ON bc.job=bs.job
WHERE balance <0 
	AND campaign=1
ORDER BY balance ASC;

SELECT 
	job, 
    count(campaign) AS num_converted
FROM bank_customer
GROUP BY job
ORDER BY count(campaign);

SELECT 
	cl.cluster_id, 
    cl.cluster_name, 
    count(cust_id) AS size_cluster
FROM cluster AS cl
JOIN customer AS c 
	ON cl.cluster_id = c.cluster_id
GROUP BY cl.cluster_id
ORDER BY cl.cluster_id;

SELECT 
	cust_id, 
	fruits + wines + sweets + meat + gold + fish AS total_spend
FROM product_spend;

SELECT 
	bc.job AS Job, 
    count(bank_cust_id) AS Number_Customers, 
    round(avg(income),2) AS Estimated_Income, 
	round(avg(balance),2) AS Average_Balance
FROM bank_customer AS bc
JOIN bank_salary AS bs
	ON bc.job = bs.job
GROUP BY bc.job
ORDER BY count(bank_cust_id);