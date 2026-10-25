-- Count the number of electric cars by model year. Write out the answer as parquet files partitioned by year.
SELECT 
    "Model Year",
    COUNT("VIN (1-10)")
FROM electric_vehicle_population_data
GROUP BY "Model Year";