'''*****************************************************************************
Purpose: To analyze the sentiments of the reddit
This program uses Vader SentimentIntensityAnalyzer to calculate the ticker compound value. 
You can change multiple parameters to suit your needs. See below under "set program parameters."
Implementation:

Limitations: 
It depends mainly on the defined parameters for current implementation:
It completely ignores the heavily downvoted comments, and there can be a time when
the most mentioned ticker is heavily downvoted, but you can change that in upvotes variable.
-------------------------------------------------------------------
****************************************************************************'''

#   Run this line in the commmand line to get all thhe required packages! 
#   Python/python3 pip install -r requirements.txt

########################################################################################################
from datetime import date, datetime, timedelta
import time
import mysql_connector
import reddit_sentiment_analysis
import smtplib 
import mysql.connector as msql
########################################################################################################
email = " ... " 
password = " ... "
db = ' ... '
########################################################################################################

def run_sentiment(): 
    #Connecting to database 
    conn = msql.connect(
            host = " ... ",
            user = " ... ", 
            passwd = " ... ", 
            database = db         
            )
    cursor = conn.cursor()

    yesterday = datetime.today() - timedelta(days=1)
    date_string = yesterday.strftime("%Y_%m_%d")
    db_tables = ["Bearish","Neutral","Bullish","Total_Compound","Mentions"]
    #Formating string so MYSQL will acccept it 
    db_name = f"'{db}'"
    column_name = f"'{date_string}'"
    try: 
        for x in db_tables: 
            table_name = f'"{x}"'
            cursor.execute(f"SELECT * FROM information_schema.COLUMNS  WHERE table_schema = {db_name} AND table_name = {table_name} AND COLUMN_NAME = {column_name}"  )
            result = cursor.fetchall()
            if result != []: 
                return False
    except: 
        print("SOME EXCEPTION HAPPENED... a warning has been sent via e-mail")
        send_email("Some error occurred with todays reddit sentiment analysis  ")
        return False
    conn.commit()
    cursor.close( )
    return True

def send_email(message): 
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email,password)
    server.sendmail(email, email, message)
    print("A warning has been sent to your email: ", email)


if __name__ == '__main__':

    if run_sentiment() == True :    
        today = date.today()
        #Set date interval for the scrape! 
        start_date = date(today.year,today.month,today.day) #Interval in (year,month, date)
        end_date = date(today.year,today.month,today.day) #Interval in (year,month, date)
        lengthOfInterval = 86400 #One day:86400, One week:604800
        start_unix =  int(time.mktime(start_date.timetuple()) + 3600 - 86400 ) 
        end_unix =  int(time.mktime(end_date.timetuple()) + 90000 - 86400 ) 
        try: 
            for unix in range (start_unix,end_unix,lengthOfInterval): 
                reddit_sentiment_analysis.run_sentiment(unix,lengthOfInterval)
                mysql_connector.exportToMySQL(unix) 
        except: 
            print("Some error occurred!")
            send_email("Some error occurred with todays reddit sentiment analysis  ")


