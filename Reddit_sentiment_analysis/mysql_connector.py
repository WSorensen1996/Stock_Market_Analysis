import mysql.connector as msql
import pandas as pd
from datetime import date, datetime

def exportToMySQL(unix): 
    #For timestamping
    date_today = datetime.utcfromtimestamp(unix).strftime('%Y_%m_%d')

    #Connecting to database 
    conn = msql.connect(
            host = " ... ",
            user = " ... ", 
            passwd = " ... ", 
            database = "REDDIT_SENTIMENT"          
            )
    cursor = conn.cursor()

    print ( "Importing the file")
    #Reading csv_file: 
    df = pd.read_csv('Output_Sentiment.csv') 
    #Creating new coloumns in each table
    db_tables = ["Bearish","Neutral","Bullish","Total_Compound","Mentions"]
    for k in range (5):
        cursor.execute("ALTER TABLE " + db_tables[k] +  " ADD %s float;" %(date_today))

    for i in range(len(df)):
        #Seperation of values 
        tickercode = str(df.values[i][0][:5])
        bearish = float(df.values[i][0][7:13])
        neutral = float(df.values[i][0][15:21])
        bullis = float(df.values[i][0][23:28]) 
        total_compaund = float(df.values[i][0][-10:-4])
        mt = float(df.values[i][0][-1])
        
        #Saves..:  
        for k in range (5): 
            values = [bearish, neutral,bullis,total_compaund,mt]
            Tickerformat = '{:5}'.format(tickercode)

            fullstring = "SELECT COUNT(*) FROM " + db_tables[k] +  " WHERE Ticker = '" + Tickerformat + "' "
            cursor.execute(fullstring)
            result = cursor.fetchall()
            if result[0][0] != (0): 
                updatequery = "UPDATE " + db_tables[k] +  " SET " + date_today + " = %s WHERE Ticker = %s"
                updateValues = (values[k],Tickerformat)
                cursor.execute(updatequery,updateValues)

            # check if empty then export them to MYSQL
            if result[0][0] == 0:
                sql = ("INSERT INTO " + db_tables[k] +  " (Ticker, %s)" %(date_today)) + (" VALUES (%s, %s)")
                values_k = [tickercode, values[k]] 
                cursor.execute(sql,values_k)  
    conn.commit()
    cursor.close( )
    print ("Done")


