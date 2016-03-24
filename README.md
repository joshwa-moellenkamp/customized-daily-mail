# Customized Daily Mail

A web scraper that provides items of interest (customized) every morning at 7:00 (daily) in the form of an email (mail).

This script automates away the navigation work I do every morning for information I'm always interested in, allowing me to open my inbox and see all the desired information I could want while I'm checking to see if anything else needs my attention. The updates that I currently receive are: (1) What the weather looks like outsite, (2) How much snow a select few resorts I care about have gotten recently, (3) NBA scores from the previous night, and finally, (4) scheduled NBA games for the day.

Here is a sample mail from March 23:

Hello, Joshwa. Here's your daily update--
It is 34.8 F (1.6 C) degrees and Partly Cloudy outside right now. The wind is blowing 0.0 mph WSW. The relative humidy is 72%.

Here's the link for the full weather: http://www.wunderground.com/us/mt/bozeman

Snow report for Bridger Bowl:
1" overnight
6" in the last 24 hours
69" settled base depth
228" seasonal snowfall

Here's the link for the full snow report: http://bridgerbowl.com/weather/snow-report

Snow Report for Eldora Mountain Resort:
New snow in the last 24 hours: 6.0 inch(es)
New snow in the last 48 hours: 6.0 inch(es)
New snow in the last 72 hours: 6.0 inch(es)
Base: 55.0 inch(es)

Here's the link for the full snow report: http://www.eldora.com/mountain.snow.php

Snow Report for Loveland Ski Area:
3" in the last 12 hours
3" in the last 24 hours
3" in the last 48 hours
3" in the last 72 hours
277" seasonal snowfall

Here's the link for the full snow report: http://skiloveland.com/snow-report/

Snow Report for Arapahoe Basin:
2" in the last 24 hours
2" in the last 72 hours
65" seasonal snowfall

Here's the link for the full snow report: http://arapahoebasin.com/ABasin/snow-conditions/default.aspx

Here are the scores for yesterday's NBA games:
CHA 105, BKN 100
MIA 113, NO 99
OKC 111, HOU 107
LAL 107, MEM 100
ATL 122, WSH 101
CLE 113, MIL 104
BOS 91, TOR 79
DET 118, ORL 102
NY 115, CHI 107
UTAH 89, HOU 87
MIN 113, SAC 104
SA 112, MIA 88
DEN 104, PHI 103
PHX 119, LAL 107
POR 109, DAL 103
GS 114, LAC 98

Here are the scheduled games for today:
NO @ IND
CLE @ BKN
CHI @ NY
UTAH @ OKC
POR @ LAC

Here is the link for the full NBA schedule: http://espn.go.com/nba/schedule/_/date/20160322

Have a great Wednesday!

## Documentation
The script is a simple web parser that extracts information from curled web pages and includes this information in a string that is sent via Google's SMTP server. The script itself is my best effort at self-documenting code, and should hopefully be readable.

* NOTE: An item of interest moving forward could be making this script more usable for those that are less technically savvy. Something like a server that interested parties could email in order to sign up. This becomes difficult to scale, however, given the current structure of the program. A beneficial TODO could be to have the weather parser take a location parameter to define behavior. Ski resorts will be a bit tricker, however, given that I can't find a decent API to do that for me.

### Authentication
customized-daily-mail uses Google's SMTP server to send mail. Use a gmail address and password to get the script up and running.

### Automation
In my implementation, customized daily-mail.py is executed from /etc/crontab. My crontab reads
```
0 7 * * * root python ~/customized-daily-mail/customized-daily-mail.py
```

### TODOs
  * Unit testing for web scraping methods
    * In particular, the NBA game scraper is volatile when no games are scheduled for a given date (Both Dec. 24 and 25 failed due to the entire league having Christmas Eve off).
  * Determine whether or not a more object-oriented design would be more effective
    * Split parsing of each website to a class or file?
    * Identify any web scraping design patterns
      * XPath could be an option for creating a reusable method for finding information from HTML source, this would remove quite a bit of duplication in the snow report methods
  * Include a helper file similar to authentication for desired 'to' address so that users aren't forced to grep through the code to find that instantiation
  * Things get weird when the script is run at night. Perhaps make the NBA script a bit smarter about using dates/times to account for this
