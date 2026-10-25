--Find the top 3 most popular electric vehicles.
-- Find the top 3 most popular electric vehicles.
SELECT 
    Model,
    COUNT("VIN (1-10)") AS number_of_vehicles
FROM
    electric_vehicle_population_data
GROUP BY 
    Model
ORDER BY 
    number_of_vehicles DESC
LIMIT 3;