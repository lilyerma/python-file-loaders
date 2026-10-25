-- Count the number of electric cars per city.
SELECT 
    City,
    County,
    State,
    Count("VIN (1-10)") AS total_evs
FROM
     electric_vehicle_population_data
GROUP BY  City, County, State;

