# Creating DB and storing the fetched license plate data.
# Creates plate_fetch_db database and stores the data on platedata table.

import sys
import mysql.connector


class DBManager:
   """The DB Manager"""
   def __init__(self, host:str, port:int, user:str, password:str) -> None:
       self.host = host
       self.port = port
       self.user = user
       self.password = password

   def connectToInstance(self) -> None:
       """Connects to the DB host"""
       try:
           DB = mysql.connector.connect(
               host=self.host,
               port=self.port,
               user=self.user,
               password=self.password
           )
           self.DB = DB

       except Exception as e:
          print(e)
          sys.exit(1)

   def createDB(self) -> None:
       """Create the platefetch DB"""
       try:
          db_name = "plate_fetch_db"
          mycursor = self.DB.cursor()
          creatdb = f"CREATE DATABASE {db_name}"
          mycursor.execute(creatdb)
          self.DB.commit()

       except Exception as e:
          print(e)

   def createTable(self) -> None:
       """Creates the table for the plate_fetch_db"""
       try:
          mycursor = self.DB.cursor()
          createtable = """
                        CREATE TABLE plate_fetch_db.platedata(
                        Reg_number VARCHAR(20),
                        Make VARCHAR(25),
                        Model VARCHAR(150),
                        DES VARCHAR(150),
                        Eng_Number VARCHAR(20),
                        Eng_Size VARCHAR(8),
                        Fitness VARCHAR(20),
                        Fuel_Type VARCHAR(20),
                        URL VARCHAR(150),
                        Insurance VARCHAR(20),
                        Location VARCHAR(150),
                        M_DESC VARCHAR(150),
                        Seats VARCHAR(3),
                        Owner VARCHAR(150),
                        PUCC VARCHAR(20),
                        Reg_Date VARCHAR(20),
                        Reg_Year VARCHAR(20),
                        VIN VARCHAR(30),
                        Variant VARCHAR(20),
                        Type VARCHAR(20)
                        );
                        """
          mycursor.execute(createtable)
          #logging.info(" Table created!")

          self.DB.commit()

       except Exception as e:
          print(e)

   def insertData(self, reg_number: str, data: str) -> None:
       """Insert data to DB"""
       try:
            inmycursor = self.DB.cursor()

            insertdata = """
                INSERT INTO plate_fetch_db.platedata(
                    Reg_number, Make, Model, DES, Eng_Number,
                    Eng_Size, Fitness, Fuel_Type, URL, Insurance,
                    Location, M_DESC, Seats, Owner, PUCC,
                    Reg_Date, Reg_Year, VIN, Variant, Type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                          %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                reg_number, data["Car Make"], data["Car Model"], data["Description"],
                data["Engine Number"], data["Engine Size"], data["Fitness"], data["Fuel Type"],
                data["Image URL"], data["Insurance"], data["Location"], data["Model Description"],
                data["Number of Seats"], data["Owner"], data["PUCC"], data["Registration Date"],
                data["Registration Year"], data["VIN"], data["Variant"], data["Vehicle Type"]
            )

            inmycursor.execute(insertdata, values)
            self.DB.commit()

       except Exception as e:
           print(e)
           raise RuntimeError("INSERT_DATA_FAILURE")
