import requests
import datetime

# Boiler-plate HTTP headers so the web server doesn't reject us thinking we are a botnet.
HEADERS = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
"Dnt": "1",
"Host": "httpbin.org",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
}
MEMBERSHIP_URL = "http://craptocurrency.net/robosha_membership"
# Visit "membership" page to be presented the CAPTCHA.
r = requests.get(MEMBERSHIP_URL, headers=HEADERS)
print(r.content)

# Respond to the CAPTCHA correctly (do not check the box); submit form to the "join" page.
JOIN_URL = "http://craptocurrency.net/robosha_join"
timestamp_str = datetime.datetime.now().isoformat(timespec='auto')
uuid="robosha_joining_bot_%s" % timestamp_str
join_data = {"member_id": uuid}
r = requests.post(JOIN_URL, headers=HEADERS, data=join_data)
print(r.content)
