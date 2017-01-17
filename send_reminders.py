import logging
import socket
import sys
import os
import pymysql
import datetime
import smtplib
from time import sleep


lock_socket = None
'''
We want to keep the socket open until the end of our script so we use a global
variable to avoid going out of scope and getting garbage collected
'''


def is_lock_free():
    '''Return true if we can acquire a lock for the process, else return false
    '''
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        # Specify unique lock id for the process
        lock_id = 'gaellebon.send-reminders'
        lock_socket.bind('\0' + lock_id)
        logging.debug("Acquired lock %r" % (lock_id,))
        return True
    except socket.error:
        # Socket is locked already, process must already be running
        logging.info("Failed to acquire lock %r" % (lock_id,))
        return False


def send_reminders(**kwargs):
    '''
    Sends the reminders from database, and updates the sent reminders.

    Arguments :
    dbhost : the database host
    db : the database name,
    dbuser : the database user,
    dbpwd : the database password

    smtphost : the smtp host
    smtpport : the smtp port
    smtpuser : the smtpuser
    smtppwd : the smtp password
    '''

    # Set the timezone to local timezone
    os.environ['TZ'] = 'Europe/Paris'

    # Connect to db
    connection = pymysql.connect(host=kwargs['dbhost'],
                                 user=kwargs['dbuser'],
                                 password=kwargs['dbpwd'],
                                 db=kwargs['db'],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Query reminders from today that have not been sent.
            query = "select id, sender_email, recipient_email, subject, body, day_to_send, time_to_send from reminder_reminder where is_sent = 0 and day_to_send = CURDATE()"
            cursor.execute(query)
            results = cursor.fetchall()

            two_minutes_from_now = (datetime.datetime.now(
            ) + datetime.timedelta(minutes=2)).time()
            twenty_two_minutes_ago = (datetime.datetime.now(
            ) + datetime.timedelta(minutes=-22)).time()

            reminders_to_send = []
            # For each reminder
            for result in results:
                # Get the time the reminder should be sent.
                tts = (datetime.datetime.min + result['time_to_send']).time()
                # Check whether we should send the reminder
                if tts < two_minutes_from_now and tts > twenty_two_minutes_ago:
                    reminder = {
                        'id': result['id'],
                        'sender': result['sender_email'],
                        'recipient': result['recipient_email'],
                        'subject': result['subject'],
                        'body': result['body'],
                    }
                    reminders_to_send.append(reminder)

            if reminders_to_send:
                # We connect to the smtp server only if we need to send
                # reminders
                try:
                    # Host:Port
                    smtpserv = smtplib.SMTP(
                        kwargs['smtphost'] + ':' + kwargs['smtpport'])

                except Exception:
                    logging.info("Could not contact smtp server")
                    pass
                else:
                    try:
                        smtpserv.login(kwargs['smtpuser'], kwargs['smtppwd'])
                        pass
                    except smtplib.SMTPAuthenticationError:
                        logging.info("Could not login to SMTP server")
                    else:
                        sent = []
                        for reminder in reminders_to_send:
                            # First we create the email content
                            fromaddr = "reminder-no-reply@gaellebon.pythonanywhere.com"
                            toaddr = reminder['recipient']
                            msg = "\r\n".join([
                                "From: " + fromaddr,
                                "To: " + toaddr,
                                "Subject: " + reminder['subject'],
                                "",
                                reminder['body'],
                                "",
                                " -------------------- ",
                                "",
                                "This email was sent to you from " +
                                reminder['sender'] +
                                "  using Visual Reminder.",
                                "",
                                "http://gaellebon.pythonanywhere.com/reminder"
                            ])
                            try:
                                smtpserv.sendmail(fromaddr, toaddr, msg)
                                # If email is sent, add its id to the sent list
                                sent.append(reminder['id'])
                            except Exception:
                                logging.info(
                                    "Could not send reminder #" +
                                    reminder['id']
                                )
                        # Close connection with smtp server once all reminders
                        # have been sent
                        smtpserv.quit()

                        # If reminders have been sent, update the database
                        # This should probably be in the sendmail try block.
                        # ¯\_(ツ)_/¯
                        if sent:
                            for i in sent:
                                with connection.cursor() as cursor:
                                    # update the reminder record
                                    query = ("update reminder_reminder set " +
                                             "is_sent = 1 where id = %s")
                                    # Execute query with argument i
                                    cursor.execute(query, i)

                            # Save the changes
                            connection.commit()
    finally:
        # Once everything is done, we close the db connection.
        connection.close()
    return True

# Exit gracefully when we can not acquire a lock
if not is_lock_free():
    sys.exit()

i = 0
keep_going = True
while keep_going:
    send_reminders(
        dbhost='gaellebon.mysql.pythonanywhere-services.com',
        db='gaellebon$website',
        dbuser='gaellebon',
        dbpwd='S8mA9Mn$6y7ngK$X',
        smtphost='mail.az-za.com',
        smtpport='25',
        smtpuser='gael.lebon@az-za.com',
        smtppwd='ST_vUtuS5aCh'
    )
    i += 1
    if i >= 5:
        keep_going = False
    sleep(300)
