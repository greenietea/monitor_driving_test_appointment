import re, datetime, smtplib, time, os, requests, shutil, sys 
from robobrowser import RoboBrowser 
from email.mime.text import MIMEText 
from bs4 import BeautifulSoup 

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
        continue_link_exists = browser.get_link(text="Continue") 
        if continue_link_exists: 
            browser.follow_link(continue_link_exists)
        
        recaptcha_exists = browser.find('iframe')
        if recaptcha_exists:
            recaptcha_api_link = recaptcha_exists.get('src') 
            resp = requests.get(recaptcha_api_link) 
            if resp.status_code != 200: 
                print "error: failed to get captcha link" 
                return 

            soup = BeautifulSoup(resp.text, "html.parser") 
            recaptcha_link = 'https://www.google.com/recaptcha/api/' + soup.img['src']
            image_resp = requests.get(recaptcha_link, stream=True)
            if image_resp.status_code != 200: 
                print "error: failed to get captcha image" 
                return

            with open('recaptcha.jpg', 'wb') as out_file: 
                shutil.copyfileobj(image_resp.raw, out_file)
            del image_resp
            
            captcha_solver_api_key = os.environ['CAPTCHA_SOLVER_API_KEY']
            captcha_solver_resp = requests.post('http://2captcha.com/in.php', files={'file':open('recaptcha.jpg','rb')}, data={'key':captcha_solver_api_key,'phrase':1,'method':'post'})
            if captcha_solver_resp.status_code != 200 or 'ERROR' in captcha_solver_resp.text or 'IP_BANNED' in captcha_solver_resp.text or 'OK' not in captcha_solver_resp.text:  
                print "error: failed to solve captcha because " + captcha_solver_resp.text  
                return 

            keep_trying_to_solve = True
            tried_times = 0 
            captcha_id = captcha_solver_resp.text.split('|')[1]
            while keep_trying_to_solve:
                time.sleep(5)
                tried_times += 1
                captcha_solver_resp = requests.get('http://2captcha.com/res.php?key='+captcha_solver_api_key+'&action=get&id='+captcha_id)
                if captcha_solver_resp.text != 'CAPCHA_NOT_READY' or tried_times > 100:
                    print "tried " + str(tried_times) + " times"
                    keep_trying_to_solve = False

            if 'ERROR' in captcha_solver_resp.text:
                print "error: failed to solve captcha because " + captcha_solver_resp.text 
                return 
            
            if tried_times > 100: 
                print "error: tried more than 100 times and 2captcha is basically a failure" 
                return
            
            print captcha_solver_resp.text
            solved_captcha = captcha_solver_resp.text.split('|')[1] 

        dvla_username = os.environ['DVLA_USERNAME']
        dvla_password = os.environ['DVLA_PASSWORD']
        
        login_form = browser.get_form() 

        login_form['username'].value = dvla_username
        login_form['password'].value = dvla_password
        if recaptcha_exists: 
            login_form['recaptcha_challenge_field'].value = solved_captcha 

        browser.submit_form(login_form) 

        change_date_time_link = browser.get_link("Change Date and time of test") 
        if not change_date_time_link: 
            print "error, no change_date_time_link_found"
            print browser.parsed 
            return

        browser.follow_link(change_date_time_link)

        date_form = browser.get_form() 
        date_form['testChoice'].value = 'ASAP' 
        browser.submit_form(date_form) 
        earliest_date_found = browser.find(attrs={"class":"BookingCalendar-date--bookable "}).find(attrs={"class":"BookingCalendar-dateLink "}).get("data-date")

        earliest_date = datetime.datetime.strptime(earliest_date_found, "%Y-%m-%d") 
        current_booking = datetime.datetime(2017,5,4) 

        if earliest_date < current_booking: 
            send_email("Found an earlier date on " + earliest_date_found) 
        
        print "Checked at " + datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S") + " and the earliest date found was " + earliest_date_found
    except Exception as e: 
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print (exc_type, fname, exc_tb.tb_lineno)

while True: 
    scheduled_grab()
    time.sleep(30)

