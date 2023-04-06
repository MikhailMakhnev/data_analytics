---
SELECT COUNT(status)
FROM company
WHERE status = 'closed';

---
SELECT funding_total
FROM company
WHERE category_code = 'news'
AND country_code = 'USA'
ORDER BY 1 DESC;

---
SELECT SUM(price_amount)
FROM acquisition
WHERE  EXTRACT (YEAR FROM CAST (acquired_at AS timestamp)) IN ('2011','2012','2013')
AND term_code = 'cash';

---
SELECT first_name,
       last_name,
       twitter_username
FROM people
WHERE twitter_username LIKE 'Silver%';

---
SELECT *
FROM people
WHERE twitter_username LIKE '%money%'
AND last_name LIKE 'K%';

---
SELECT country_code,
       SUM(funding_total)
FROM company
GROUP BY 1
ORDER BY 2 DESC;

---
SELECT funded_at,
       MIN(raised_amount),
       MAX(raised_amount)
FROM funding_round
GROUP BY 1
HAVING MIN(raised_amount) <> 0
AND MIN(raised_amount) <> MAX(raised_amount);

---
SELECT *,
    CASE
           WHEN invested_companies >= 100 THEN 'high_activity'
           WHEN invested_companies >= 20 AND invested_companies < 100 THEN 'middle_activity'
           WHEN invested_companies < 20 THEN 'low_activity'
    END
FROM fund;

---
SELECT
       CASE
           WHEN invested_companies>=100 THEN 'high_activity'
           WHEN invested_companies>=20 THEN 'middle_activity'
           ELSE 'low_activity'
       END AS activity,
       ROUND(avg(investment_rounds))
FROM fund
GROUP BY activity
ORDER BY 2;

---
SELECT country_code,
       MIN(invested_companies),
       MAX(invested_companies),
       AVG(invested_companies)
FROM fund
WHERE EXTRACT (YEAR  FROM CAST (founded_at AS timestamp)) IN ('2010', '2011', '2012')
GROUP BY 1
HAVING MIN(invested_companies) <> 0
ORDER BY 4 DESC, 1
LIMIT 10;

---
SELECT first_name,
       last_name,
       instituition
FROM people as pe
LEFT OUTER JOIN education as ed ON pe.id=ed.person_id;

---
SELECT com.name,
       COUNT(DISTINCT ed.instituition)
FROM people as pe
JOIN education as ed ON pe.id=ed.person_id
JOIN company as com ON pe.company_id=com.id
GROUP BY 1
ORDER BY 2 DESC
LIMIT 5;

---
SELECT DISTINCT com.name                
FROM company AS com
WHERE com.status = 'closed' 
AND id IN (SELECT company_id
            FROM funding_round
            WHERE is_first_round = 1
            AND is_last_round = 1);

---
WITH
comp AS (SELECT DISTINCT com.id AS ms                 
                    FROM company AS com
                    WHERE com.status = 'closed' 
                    AND id IN (SELECT company_id
                                FROM funding_round
                                WHERE is_first_round = 1
                                AND is_last_round = 1))


SELECT DISTINCT id
FROM people as pl
JOIN comp on pl.company_id=comp.ms
WHERE pl.company_id = comp.ms;

---
WITH
comp AS (SELECT DISTINCT com.id AS ms                 
                    FROM company AS com
                    WHERE com.status = 'closed' 
                    AND id IN (SELECT company_id
                                FROM funding_round
                                WHERE is_first_round = 1
                                AND is_last_round = 1))


SELECT DISTINCT pl.id,
       ed.instituition
FROM people as pl
JOIN comp on pl.company_id=comp.ms
JOIN education as ed ON pl.id=ed.person_id
WHERE pl.company_id = comp.ms;

---
WITH
comp AS (SELECT DISTINCT com.id AS ms                 
                    FROM company AS com
                    WHERE com.status = 'closed' 
                    AND id IN (SELECT company_id
                                FROM funding_round
                                WHERE is_first_round = 1
                                AND is_last_round = 1))


SELECT pl.id,
       count(ed.instituition)
FROM people as pl
JOIN comp on pl.company_id=comp.ms
JOIN education as ed ON pl.id=ed.person_id
WHERE pl.company_id = comp.ms
group by 1;

---
WITH
comp AS (SELECT DISTINCT com.id AS ms                 
                    FROM company AS com
                    WHERE com.status = 'closed' 
                    AND id IN (SELECT company_id
                                FROM funding_round
                                WHERE is_first_round = 1
                                AND is_last_round = 1)),


 sel AS      (SELECT pl.id,
               count(ed.instituition) as co
        FROM people as pl
        JOIN comp on pl.company_id=comp.ms
        JOIN education as ed ON pl.id=ed.person_id
        WHERE pl.company_id = comp.ms
        group by 1)
SELECT avg(sel.co)
FROM sel;

---
WITH
comp AS (SELECT DISTINCT com.id AS ms                 
                    FROM company AS com
                    WHERE com.name = 'Facebook'),
         
         
 sel AS      (SELECT pl.id,
               count(ed.instituition) as co
        FROM people as pl
        JOIN comp on pl.company_id=comp.ms
        JOIN education as ed ON pl.id=ed.person_id
        WHERE pl.company_id = comp.ms
        group by 1)
SELECT avg(sel.co)
FROM sel;

---
SELECT f.name AS name_of_fund, 
       C.name AS name_of_company, 
       fr.raised_amount AS amount
FROM investment AS i
JOIN company AS c ON i.company_id=c.id
JOIN fund AS f ON i.fund_id=f.id
JOIN funding_round AS fr ON i.funding_round_id = fr.id
WHERE EXTRACT(YEAR FROM fr.funded_at) BETWEEN 2012 AND 2013
   AND c.milestones > 6;

---
WITH
 ac AS (SELECT c.name AS acquired_company,
               c.funding_total,
               tab1.acquiring_company_id,
               tab1.price_amount
        FROM company AS c
        RIGHT JOIN (
                    SELECT acquiring_company_id,
                           acquired_company_id,
                           price_amount
                    FROM acquisition
                    WHERE price_amount > 0
                   ) AS tab1 ON c.id = tab1.acquired_company_id)
 
SELECT company.name AS acquiring_company,
       ac.price_amount,
       ac.acquired_company,
       ac.funding_total,
       ROUND(ac.price_amount / ac.funding_total)

FROM ac
LEFT JOIN company ON company.id  = ac.acquiring_company_id
WHERE ac.funding_total > 0
ORDER BY  ac.price_amount DESC, ac.acquired_company
LIMIT 10;

---
SELECT c.name,
       tab.month
FROM company as c
RIGHT JOIN ( SELECT company_id,
             EXTRACT(MONTH FROM funded_at) AS month
             FROM funding_round
             WHERE EXTRACT(YEAR FROM funded_at) BETWEEN 2010 AND 2013
             and raised_amount <> 0
            ) AS tab ON c.id = tab.company_id
WHERE c.category_code LIKE 'social';

---
WITH
tb1 AS (SELECT EXTRACT(MONTH FROM funded_at) AS month,
                id AS funding_round_id
                FROM funding_round
         WHERE EXTRACT(YEAR FROM funded_at) BETWEEN 2010 AND 2013
         ),

tb2 AS (SELECT EXTRACT(MONTH FROM acquired_at) AS month,
                COUNT(acquired_company_id) AS count_acquired,
                SUM(price_amount) AS total_amount
         FROM acquisition
         WHERE EXTRACT(YEAR FROM acquired_at) BETWEEN 2010 AND 2013
         GROUP BY EXTRACT(MONTH FROM acquired_at)
        ),

tb3 AS (SELECT i.funding_round_id,
                f.name
        FROM investment AS i
        JOIN fund AS f ON f.id = i.fund_id
        WHERE fund_id IN (SELECT id
                          FROM fund
                          WHERE country_code LIKE 'USA')
        ),

tb4 AS (SELECT month,
                COUNT(DISTINCT name) AS count_USA
         FROM tb1 
         LEFT JOIN tb3 ON tb1.funding_round_id = tb3.funding_round_id
         GROUP BY month)
         
SELECT tb4.month,
       tb4.count_USA,
       tb2.count_acquired,
       tb2.total_amount
FROM tb4 
LEFT JOIN tb2 ON tb4.month = tb2.month;

---
WITH

t_11 AS (SELECT country_code AS cd,
       AVG(funding_total)   AS total
FROM company
WHERE  EXTRACT (YEAR FROM CAST (founded_at AS timestamp)) = '2011'             
GROUP BY 1),

t_12 AS (SELECT country_code AS cd,
       AVG(funding_total)   AS total
FROM company
WHERE  EXTRACT (YEAR FROM CAST (founded_at AS timestamp)) = '2012'

         GROUP BY 1),

t_13 AS (SELECT country_code AS cd,
       AVG(funding_total)   AS total
FROM company
WHERE  EXTRACT (YEAR FROM CAST (founded_at AS timestamp)) = '2013'

         GROUP BY 1)



SELECT t_11.cd,
       t_11.total as "2011",
       t_12.total as "2012",
       t_13.total as "2013"
FROM t_11
JOIN t_12 ON t_11.cd=t_12.cd
JOIN t_13 ON t_12.cd=t_13.cd
ORDER BY 2 DESC;


