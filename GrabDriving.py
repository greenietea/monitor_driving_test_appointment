import re, datetime, smtplib, time, os 
from robobrowser import RoboBrowser 
from email.mime.text import MIMEText 

def send_email(message): 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    user_email = os.environ['GMAIL_USER_EMAIL']
    user_password = os.environ['GMAIL_USER_PASSWORD']
    to_email = os.environ['TO_EMAIL']
    from_email = os.environ['FROM_EMAIL'] 
    server.login(user_email,user_password)

    msg = MIMEText(message) 
    msg['Subject'] = "Notification from GrabDriving Script" 
    msg['From'] = from_email 
    msg['To'] = to_email
    server.sendmail(to_email,from_email,msg.as_string())
    server.close()

def scheduled_grab():
    browser = RoboBrowser(parser="html.parser",history=True) 
    browser.open('https://www.gov.uk/change-driving-test')
    
    try:
        start_link = browser.get_link(text="Start now")
        browser.follow_link(start_link)

        dvla_username = os.environ['DVLA_USERNAME']
        dvla_password = os.environ['DVLA_PASSWORD']
        
        login_form = browser.get_form() 
        login_form['username'].value = dvla_username
        login_form['password'].value = dvla_password
        browser.submit_form(login_form) 

        change_date_time_link = browser.get_link("Change Date and time of test") 
        browser.follow_link(change_date_time_link)

        date_form = browser.get_form() 
        date_form['testChoice'].value = 'ASAP' 
        browser.submit_form(date_form) 

        earliest_date_found = browser.find(attrs={"class":"BookingCalendar-date--bookable "}).find(attrs={"class":"BookingCalendar-dateLink "}).get("data-date")

        earliest_date = datetime.datetime.strptime(earliest_date_found, "%Y-%m-%d") 
        current_booking = datetime.datetime(2017,5,25) 

        if earliest_date < current_booking: 
            send_email("Found an earlier date on " + earliest_date_found) 
        
        print "Checked at " + datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S") + " and the earliest date found was " + earliest_date_found
    except: 
        print "Error setting up RoboBrowser" 

while True: 
    scheduled_grab()
    time.sleep(900)

