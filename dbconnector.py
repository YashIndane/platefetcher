"""
Creating DB and storing the fetched license plate data.
Creates plate_fetch_db database and stores the data on platedata table.
"""

import logging
import mysql.connector

#Setting logging config
logging.basicConfig(level=logging.NOTSET)

class DB_INSTANCE:
    def __init__(self, host:str, port:str, user:str, password:str) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    #Connecting to DB-instance
    def connectToInstance(self) -> None:
       try:
          DB = mysql.connector.connect(
               host=self.host,
               port=self.port,
               user=self.user,
               password=self.password
          )

          self.DB = DB
          logging.info("Connected to DB!")

       except Exception as e:
            logging.error(e)
    
    #Creating database
    def createDB(self) -> None:
       try:
          db_name = "plate_fetch_db"
          mycursor = self.DB.cursor()
          creatdb = f"CREATE DATABASE {db_name}"
          mycursor.execute(creatdb)
          logging.info("DB created!")

          self.DB.commit()

       except Exception as e:
          logging.error(e)


    #Creating table
    def createTable(self) -> None:
       try:
          mycursor = self.DB.cursor()
          createtable = """
                        CREATE TABLE plate_fetch_db.platedata(
                        Plate_number VARCHAR(20),
                        Model VARCHAR(150),
                        Reg_year VARCHAR(20),
                        Engine_size VARCHAR(20),
                        seats VARCHAR(20),
                        Vehicle_ID VARCHAR(100),
                        Engine_number VARCHAR(100),
                        Fuel VARCHAR(30),
                        Reg_date VARCHAR(100),
                        Reg_location VARCHAR(100)
                        );
          """
          mycursor.execute(createtable)
          logging.info("Table created!")

          self.DB.commit()

       except Exception as e:
          logging.error(e)

    #Inserting data
    def insertData(self, data:str) -> None:
        try:
           
           inmycursor = self.DB.cursor()

           insertdata = """
                        INSERT INTO plate_fetch_db.platedata(
                        Plate_number,
                        Model,
                        Reg_year,
                        Engine_size,
                        seats,
                        Vehicle_ID,
                        Engine_number,
                        Fuel,
                        Reg_date,
                        Reg_location) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
           """

           plate_details = [
               tuple(data.split(" ")),
           ]
        
           inmycursor.executemany(insertdata, plate_details)
           logging.info("Data saved on DB!")

           self.DB.commit()

        except Exception as e:
           logging.error(e)