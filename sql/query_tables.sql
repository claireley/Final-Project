USE ironhack_final_project;

SELECT *
FROM customer as c
JOIN behaviour as b on c.cust_id=b.cust_id
JOIN channels as ch on c.cust_id=ch.cust_id
JOIN cluster as cl on c.cluster_id=cl.cluster_id
JOIN product_spend as p on c.cust_id=p.cust_id;

SELECT *
FROM bank_customer as bc
JOIN bank_salary as bs on bc.job=bs.job;

SELECT bank_cust_id, balance, campaign, bc.job, income
FROM bank_customer as bc
JOIN bank_salary as bs on bc.job=bs.job
WHERE balance <0 AND campaign=1
ORDER BY balance ASC;

SELECT job, count(campaign) as num_converted
FROM bank_customer
GROUP BY job
ORDER BY count(campaign);

SELECT cl.cluster_id, cl.cluster_name, count(cust_id) as size_cluster
FROM cluster as cl
JOIN customer as c ON cl.cluster_id = c.cluster_id
GROUP BY cl.cluster_id
ORDER BY cl.cluster_id;