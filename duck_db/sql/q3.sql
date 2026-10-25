-- Find the most popular electric vehicle in each postal code.

WITH ranked_vehicles AS (
    SELECT
        "Postal Code",
        Model,
        RANK() OVER (PARTITION BY "Postal Code" ORDER BY COUNT("VIN (1-10)") DESC) as rnk
    FROM electric_vehicle_population_data
    GROUP BY "Postal Code", Model
)
SELECT
    "Postal Code",
    Model
FROM ranked_vehicles
WHERE rnk = 1;
