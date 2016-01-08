# Customized Daily Mail

A web scraper that provides items of interest (customized) every morning at 7:00 (daily) in the form of an email (mail). 

When I'm groggy in the morning, I don't want to navigate the web in order to find things that I check every morning anyway. This script automates away that work, instead allowing me up open my inbox and see all the desired information I could want while I'm checking to see if anything else during the day needs my attention. The updates that I currently receive are: (1) What the weather looks like outsite, (2) How much snow the local resort got overnight, (3) NBA scores from the previous night, and finally, (4) scheduled NBA games for the day.

Here is a sample mail from January 7:

![Sample Mail](/images/sample-mail.png)

## Documentation

### Script
The script is a simple web parser that extracts information from curled web pages and includes this information in a string that is sent via Google's SMTP server. The script itself is my best effort at self-documenting code, and should hopefully be readable.

* NOTE: An item of interest moving forward could be making this script more usable for those that are less technically savvy. Something like a server that interested parties could email in order to sign up. This becomes difficult to scale, however, given the current structure of the program. A beneficial TODO could be to have the weather parser take a location parameter to define behavior. Ski resorts will be a bit tricker, however, given that I can't find a decent API to do that for me.

### Authentication
customized-daily-mail uses Google's SMTP server to send mail. Use a gmail address and password to get the script up and running.

### Automation
In my implementation, customized daily-mail.py is executed from /etc/crontab. My crontab reads
```
0 7 * * * root python /root/weather/weather.py
```

### TODOs
  * Unit testing for web scraping methods
    * In particular, the NBA game scraper is volatile when no games are scheduled for a given date (Both Dec. 24 and 25 failed due to the entire league having Christmas Eve off).
  * Determine whether or not a more object-oriented design would be more effective
    * Split parsing of each website to a class or file?
    * Identify any web scraping design patterns,
  * Include a helper file similar to authentication for desired 'to' address so that users aren't forced to grep through the code to find that instantiation


