import urllib
import time
import logging
import configReader
import smtplib
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler = logging.FileHandler("ping.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fileHandler.setFormatter(formatter)
logging.getLogger().addHandler(fileHandler)

config = configReader.ConfigReader()

last_answers = {}

def ping(url):
    logging.info("Ping " + url)
    data = urllib.urlopen(url).read()
    logging.info("Ans: " + data)
    return data

def notify_email(endpoint, old_ans, new_ans):
    username = config.read_email_account()
    password = config.read_email_password()

    fromaddr = username
    toaddrs = config.read_email_dest()
    msg = "\r\n".join([
      "From: " + fromaddr,
      "To: " + str(toaddrs),
      "Subject: " + "Endpoint changed: " + endpoint,
      "",
      "API answer has changed for endpoint: " + endpoint + ".\n\nOld value: " + str(old_ans['value']) + ". From: " + str(old_ans['timestamp']) + "\n\nNew value: " + str(new_ans)
      ])

    logging.info("emailing: " + str(toaddrs) + ". Message: " + msg)

    server = smtplib.SMTP(config.read_email_server())
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

    logging.info("Done emailing")

def get_endpoints():
    urls = config.read_endpoints()
    endpoints = urls.split(',')
    logging.info("got endpoints: " + str(endpoints))
    return endpoints

def main():
    global lastAnswers

    endpoints = get_endpoints()

    sleepTime = int(config.read_sleep_time())

    while True:

        for endpoint in endpoints:
            logging.info("Monitoring: " + endpoint)
            ans = ping(endpoint)

            if not endpoint in last_answers:
                logging.info("endpoint never monitored: " + endpoint)
                last_answers[endpoint] = {'value': ans, 'timestamp': datetime.datetime.now()}

            elif last_answers[endpoint]['value'] != ans:
                logging.info("endpoint changed: " + endpoint + ". New answer: " + str(ans))
                notify_email(endpoint, last_answers[endpoint], ans)
                last_answers[endpoint] = {'value': ans, 'timestamp': datetime.datetime.now()}
            else:
                logging.info("Endpoint answer not changed for: " + endpoint + " since: " + str(last_answers[endpoint]['timestamp']))

        logging.info("Going to sleep for " + str(sleepTime) + " seconds (" + str(sleepTime/60) + " mints)")
        time.sleep(sleepTime)

main()
