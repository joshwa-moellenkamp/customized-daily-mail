import logging
import sys
import smtplib
import datetime
import subprocess
import re
import json
import traceback

# Hold mailing authentication information
import authentication

months   = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
           }

weekdays = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
           }

# Specify two desired URL's for the formatted email message.
weather_url     = "http://www.wunderground.com/us/mt/bozeman"
snow_report_url = "http://bridgerbowl.com/weather/snow-report"

# Mail addresses.
from_addr       = "jmolecavalier@gmail.com"
to_addrs        = ("joshwa.moellenkamp@gmail.com", )

def find_between(string, preceeding_pattern, trailing_pattern):
    """
    For a given string, return the substring located
    between preceeding_pattern and trailing_pattern.

    Keyword arguments:
    string - The string to parse
    preceeding_pattern - The initial pattern to recognize
    trailing_pattern - The pattern trailing the desired string

    return - The desired substring
    """
    try:
        start = string.index(preceeding_pattern) + len(preceeding_pattern)
        end = string.index(trailing_pattern, start)
        return string[start:end]
    except ValueError:
        return ""

def construct_time_variables(today):
    """
    Using a provided datetime.datetime object representing the 
    current date, construct an assortment of values used by this script.

    Keyword arguments:
    today - A datetime.datetime representing the current object.

    return - (day_of_week, # Sunday, Monday, etc.
              tomorrow,    # Monday, Tuesday, etc.
              int_month,   # 1, 2, ..., 12
              str_month,   # January, February, etc.
              day,         # Day of the month
              year)        # Year
    """
    day_of_week = weekdays.get(today.weekday())
    tomorrow    = weekdays.get(today.weekday() + 1)
    int_month   = today.month
    str_month   = months.get(today.month)
    day         = today.day
    if 4 <= day % 100 <= 20:
        str_day = str(day) + "th"
    else:
        str_day = str(day) + {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    year        = today.year

    return day_of_week, tomorrow, int_month, str_month, day, year

def print_formatting():
    logging.info("-----------------------------------------------------------")
    logging.info("Running script on %s-%s at %s:%s" % (
            datetime.datetime.now().month,
            datetime.datetime.now().day,
            datetime.datetime.now().hour,
            datetime.datetime.now().minute))

def bridger_bowl_snow_report():
    """
    Curl Bridger Bowl's snow report page. Parse for desired information.

    return - constructed snow report string
    """
    logging.debug("Entering bridger_bowl_snow_report method.")

    page = subprocess.call([
            "curl",
            "http://bridgerbowl.com/weather/snow-report", "-o",
            "snow-results.txt"])

    # Read in the text file to a string.
    with open("snow-results.txt", "r") as results_file:
        results = results_file.read()

    # Parse the webpage for information about snowfall.
    # 'new-snow-and-base-info' is a simple enough substring to split on.
    result = re.split("new-snow-and-base-info", str(results))

    # Gather the available fields relating to snowfall.
    new_snow = find_between(result[1], ":20px;\">", "<span")
    if new_snow != "Trace":
        new_snow = new_snow + "\""
    daily_snow = find_between(result[2], ":20px;\">", "<span")
    if daily_snow != "Trace":
        daily_snow = daily_snow + "\""
    settled_depth = find_between(result[3], ":20px;\">", "<span") + "\""
    seasonal_snowfall = find_between(result[4], ":20px;\">", "<span") + "\""

    logging.debug("Exiting bridger_bowl_snow_report method.")

    return ("Snow report for Bridger Bowl:\n"
            "%s overnight\n"
            "%s in the last 24 hours\n"
            "%s settled base depth\n"
            "%s seasonal snowfall\n\n"
            "Here's the link for the full snow report: %s\n\n") % (
                new_snow, daily_snow, settled_depth, 
                seasonal_snowfall, snow_report_url)

def bozeman_weather_report():
    """
    Return wunderground's API page for Bozeman. Parse for desired information.

    return - constructed weather report string
    """
    logging.debug("Entering bozeman_weather_report method.")

    weather = subprocess.call([
            "curl",
            ("http://api.wunderground.com/api/"
             "761d35dd561f55a0/conditions/q/MT/bozeman.json"),
            "-o",
            "weather-results.json"])

    with open("weather-results.json", "r") as results_file:
        results = json.load(results_file)

    # Grab desired values from the json object.
    temp       = results["current_observation"]["temperature_string"]
    weather    = results["current_observation"]["weather"]
    humid      = results["current_observation"]["relative_humidity"]
    wind_dir   = results["current_observation"]["wind_dir"]
    wind_speed = results["current_observation"]["wind_mph"]

    logging.debug("Exiting bozeman_weather_report method.")

    return ("It is %s degrees and %s outside right now. "
            "The wind is blowing %s mph %s. "
            "The relative humidy is %s.\n\n"
            "Here's the link for the full weather: %s\n\n") % (
                temp, weather, wind_speed, wind_dir, humid, weather_url)

def espn_nba_report(date_string, tomorrow):
    """
    Return the scores from last night's games and the scheduled games for today.

    return - (scores,         # Scores from the previous date
              upcoming_games) # Scheduled games for the current date
    """
    logging.debug("Entering espn_nba_report method.")

    games = subprocess.call([
            "curl",
            "http://espn.go.com/nba/schedule/_/date/%s" % date_string,
            "-o",
            "nba-schedule.txt"])

    with open("nba-schedule.txt", "r") as nba_results_file:
        nba_results = nba_results_file.read()

    result  = re.split("&lpos=nba:schedule:score", nba_results)

    scores = []

    # Scrape meaningful information (game results) from the list.
    iteration = 0
    for substring in result:
        if iteration > 0:
            scores.append(find_between(substring, ">", "<"))
        iteration = iteration + 1

    # Scrape the upcoming schedule from the last element of the previous split.
    upcoming_games = re.split("&lpos=nba:schedule:team", 
                              result[len(result) - 1])

    # Toss away the first two elements. Then, toss away odd indeces after that.
    # The split string is used for the team names along with the team's logos.
    # upcoming_games[0] is the initial unwanted information, then [1] is the 
    # logo. [2] is where we start receiving desired information, along with 
    # every other index after that.

    if len(upcoming_games) >= 2 \
    and tomorrow not in (upcoming_games[0], upcoming_games[1]):
        upcoming_games.pop(0)
        upcoming_games.pop(0)

    index_to_pop = 1
    while index_to_pop < len(upcoming_games):
        upcoming_games.pop(index_to_pop)
        index_to_pop = index_to_pop + 1

    teams = []
    for upcoming_game in upcoming_games:
        teams.append(find_between(
                        find_between(upcoming_game, "abbr title", "/abbr>"),
                        ">",
                        "<"))

        if tomorrow in upcoming_game:
            break

    scheduled_games = []

    index = 0
    while index + 1 < len(teams):
        scheduled_games.append(teams[index] + " @ " + teams[index + 1])
        index = index + 2

    message = ""

    if len(scores) > 0:
        message += "Here are the scores for yesterday's NBA games:\n"

        for game in scores:
            message += str(game)
            message += "\n"

    if len(scheduled_games) > 0:
        message += "\nHere are the scheduled games for today:\n"

        for game in scheduled_games:
            print "Scheduled game: %s" % str(game)
            message += game
            message += "\n"

    message += "\nHere is the link for the full NBA schedule: %s" % \
            ("http://espn.go.com/nba/schedule/_/date/" + date_string + "\n\n")

    logging.debug("Exiting espn_nba_report method.")

    return message

def date_string(int_month, day, year):
    """
    Using the month, day, and year, determine a string that will be used to 
    access a specific page on ESPN with all desired information.

    Keyword arguments:
    int_month - The month represented as a 1-12 integer
    day - The day of the month

    return - Formatted date string
    """
    logging.debug("Entering date_string method.")


    date_string_month = "0" + str(int_month) if int_month < 10 \
                                             else str(int_month)
    date_string_day   = "0" + str(day - 1)   if day       < 10 \
                                             else str(day - 1) 

    logging.debug("Exiting date_string method.")

    return "%s%s%s" % (year, date_string_month, date_string_day)

def send_email(message, to_addrs = to_addrs, from_addr = from_addr):
    """
    Send an SMTP formatted email message to the specified to and from addresses.

    Keyword arguments:
    message - the SMTP formatted message
    to - The list of addresses who will recieve the mail
    from - The author of the message
    """
    logging.debug("Entering send_email method.")

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(authentication.mail_name, authentication.mail_pwd)
    server.sendmail(from_addr, to_addrs, message)
    server.quit()

    logging.debug("Exiting send_email method.")

def main():
    try:
        day_of_week, tomorrow, int_month, str_month, day, year = \
                construct_time_variables(datetime.datetime.today())

        message = ("Subject: Update for %s, %s %s\n\nHello, Joshwa. Here's "
                   "your daily update--\r") % (day_of_week, str_month, day)
    except Exception as e:
        logging.error("Exception occured while setting up message:",
                     exc_info=1)
        send_mail(("Subject: Customized Daily Mail failure.\n\n"
                "Good morning, Joshwa. I'm sorry to report that something "
                "went wrong while attempting to prepare your update for today."
                " Rest assured, the log files hold the answers. Have a great "
                "day!"))
        system.exit()

    try:
        message += bozeman_weather_report()
        logging.info("Successfully included weather report.")
    except Exception as e:
        logging.error("Exception occured while processing weather:",
                     exc_info=1)

    try:
        message += bridger_bowl_snow_report()
        logging.info("Successfully included snow report.")
    except Exception as e:
        logging.error("Exception occured while processing snow report:", 
                     exc_info=1)

    try:
        schedule_date = date_string(int_month, day, year)
        message += espn_nba_report(schedule_date, tomorrow)
        logging.info("Successfully included NBA report.")
    except Exception as e:
        logging.error("Exception occured while processing NBA report:",
                     exc_info=1)

    # No need for protection here, it is already guaranteed by the first try.
    message += "Have a great %s!" % day_of_week

    try:
        send_email(message)
        logging.info("Script executed successfully. Mail sent.")
    except Exception as e:
        logging.error("Exception occurred while attempting to send mail",
                     exc_info=1)

if __name__ == '__main__':
    try:
        # Turn on logging.
        logging.basicConfig(filename = "/var/log/customized-daily-mail.log",
                            level = logging.INFO)

        # Set up a handler to write to the console as well.
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
                "%(name)-12s: %(levelname)-8s %(message)s")
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        print_formatting()

        main()
    except Exception as e:
        print "ERROR!"
        print str(e)
        logging.error("Unidentified exception detected during execution:",
                     exc_info=1)
