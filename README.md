# Customized Daily Mail

A web scraper that provides items of interest.

* Script
  * Documentation here

* Authentication
  * customized-daily-mail uses Google's SMTP server to send mail. Use a gmail address and password to get the script up and running.

* Automation
  * In my implementation, customized daily-mail.py is executed from /etc/crontab. My crontab reads
```
0 7 * * * root python /root/weather/weather.py >> /var/log/customized-daily-mail.log 2&>1
```

* TODOs
  * Unit testing for web scraping methods
    * In particular, the NBA game scraper is volatile when no games are scheduled for a given date (Both Dec. 24 and 25 failed due to the entire league having Christmas Eve off)
  * Ability to ignore failing components of the mail while still including working components (would be especially relevant given the above note)
  * Determine whether or not a more object-oriented design would be more effective
    * Split parsing of each website to a class or file?
    * Identify any web scraping design patterns
  * Implement logging system rather than using 2&>1 in crontab (probably doesn't make a difference for personal use. But this is matter of principle).


