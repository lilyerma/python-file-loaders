DROP TABLE IF EXISTS electric_vehicle_population_data;
CREATE TABLE IF NOT EXISTS electric_vehicle_population_data (
    "VIN (1-10)" TEXT,
    "County" TEXT,
    "City" TEXT,
    "State" TEXT,
    "Postal Code" BIGINT,
    "Model Year" BIGINT,
    "Make" TEXT,
    "Model" TEXT,
    "Electric Vehicle Type" TEXT,
    "Clean Alternative Fuel Vehicle (CAFV) Eligibility" TEXT,
    "Electric Range" BIGINT,
    "Base MSRP" BIGINT,
    "Legislative District" DOUBLE PRECISION,
    "DOL Vehicle ID" BIGINT,
    "Vehicle Location" TEXT,
    "Electric Utility" TEXT,
    "2020 Census Tract" BIGINT
); -- <-- здесь добавлена закрывающая скобка и точка с запятой

INSERT INTO electric_vehicle_population_data 
SELECT * FROM read_csv('duck_db/data/Electric_Vehicle_Population_Data.csv');