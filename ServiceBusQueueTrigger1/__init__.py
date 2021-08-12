import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
#from azure.servicebus import ServiceBusClient, ServiceBusMessage
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: {}'.format(notification_id))

    # TODO: Get connection to database
    POSTGRES_URL="project3pg.postgres.database.azure.com"  #TODO: Update value
    POSTGRES_USER="batursql@project3pg" #TODO: Update value
    POSTGRES_PW=""   #TODO: Update value
    POSTGRES_DB="techconfdb"   #TODO: Update value
    #DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
    connection = psycopg2.connect(host=POSTGRES_URL, dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PW)
    #connection=psycopg2.connect(DB_URL)
    cursor=connection.cursor()
    try:
        # TODO: Get notification message and subject from database using the notification_id
        cursor.execute("SELECT message, subject FROM notification WHERE id = {}".format(notification_id))
        message=cursor.fetchone()
        # TODO: Get attendees email and name
        cursor.execute("SELECT first_name, email FROM attendee;")
        attendees=cursor.fetchall()
        nr_of_attendees=len(attendees)
        # TODO: Loop through each attendee and send an email with a personalized subject
        '''sg = SendGridAPIClient('')
        for attendee in attendees:
            notify = Mail(
            from_email="info@techconf.com",
            to_emails=attendee[1],
            subject=message[1],
            plain_text_content=message[0])
            sg.send(notify)'''
        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        nowtime=datetime.utcnow()
        cursor.execute('''UPDATE notification 
                          SET completed_date = %s, status = 'Notified %s attendees'
                          WHERE id = %s;''', (nowtime, nr_of_attendees, notification_id))
        connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        connection.close()
