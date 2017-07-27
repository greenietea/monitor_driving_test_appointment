# Find an earlier driving test appointment

Run this script to find an earlier driving test appointment - works only if you have already booked a driving test and it will only look at the same test centre. 

Start with 
```
git clone
cd monitor_driving_test_appointment
virtualenv env 
source env/bin/activate
pip install -r requirements.txt 
```

You will need to provide the following environment variables. 
Explanation: 
- GMAIL_USER_EMAIL and GMAIL_USER_PASSWORD, TO_EMAIL, FROM_EMAIL are only for sending notification emails to yourself when there's an earlier available appointment time
- DVLA_USERNAME is your driving licence number 
- DVLA_PASSWORD is your test booking number 
- CAPTCHA_SOLVER_API_KEY is the 2captcha service for overriding the captcha check 
- CURRENT_BOOKING is the current booked date in the format of YYYY-MM-DD and it will only send notification emails if it finds any available appointments before this date
```
export GMAIL_USER_EMAIL="your own email address"
export GMAIL_USER_PASSWORD="your own email password"
export TO_EMAIL=""
export FROM_EMAIL=""
export DVLA_USERNAME="lastname plus numbers"
export DVLA_PASSWORD="test booking number"
export CAPTCHA_SOLVER_API_KEY=""
export CURRENT_BOOKING=""

