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

    return - (new_snow,          # Overnight snow
              daily_snow,        # Snow in the last 24 hours
              settled_depth,     # Settled base depth 
              seasonal_snowfall) # Snow since the beginning of the season
    """
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
    daily_snow = find_between(result[2], ":20px;\">", "<span")
    settled_depth = find_between(result[3], ":20px;\">", "<span")
    seasonal_snowfall = find_between(result[4], ":20px;\">", "<span")

    return new_snow, daily_snow, settled_depth, seasonal_snowfall

def bozeman_weather_report():
    """
    Return wunderground's API page for Bozeman. Parse for desired information.

    return - (temp,
              weather,
              humid,
              wind_dir,
              wind_speed)
    """
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

    return temp, weather, humid, wind_dir, wind_speed

def espn_nba_report(date_string, tomorrow):
    """
    Return the scores from last night's games and the scheduled games for today.

    return - (scores,         # Scores from the previous date
              upcoming_games) # Scheduled games for the current date
    """
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

    # Scrape the upcoming schedule for from the last element of the previous split.
    upcoming_games = re.split("&lpos=nba:schedule:team", result[len(result) - 1])

    # Toss away the first two elements. Then, toss away odd indeces after that.
    # The split string is used for the team names along with the team's logos.
    # upcoming_games[0] is the initial unwanted information, then [1] is the logo.
    # [2] is where we start receiving desired information, along with every other
    # index after that.

    if len(upcoming_games) >= 2 and tomorrow not in (upcoming_games[0], upcoming_games[1]):
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
        print "Processing team: ", (find_between(
                        find_between(upcoming_game, "abbr title", "/abbr>"),
                        ">",
                        "<"))

        if tomorrow in upcoming_game:
            break

    scheduled_games = []

    index = 0
    while index + 1 < len(teams):
        print "appending teams %s and %s" % (teams[index], teams[index + 1])
        scheduled_games.append(teams[index] + " @ " + teams[index + 1])
        index = index + 2

    return scores, scheduled_games

def date_string(int_month, day, year):
    """
    Using the month, day, and year, determine a string that will be used to access
    a specific page on ESPN with all desired information.

    Keyword arguments:
    int_month - The month represented as a 1-12 integer
    day - The day of the month

    return - Formatted date string
    """
    date_string_month = "0" + str(int_month) if int_month < 10 else str(int_month)
    date_string_day   = "0" + str(day - 1)   if day       < 10 else str(day - 1)

    return "%s%s%s" % (year, date_string_month, date_string_day)

def send_email(message, to_addrs = to_addrs, from_addr = from_addr):
    """
    Send an SMTP formatted email message to the specified to and from addresses.

    Keyword arguments:
    message - the SMTP formatted message
    to - The list of addresses who will recieve the mail
    from - The author of the message
    """
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(authentication.mail_name, authentication.mail_pwd)
    server.sendmail(from_addr, to_addrs, message)
    server.quit()

def main():
    logging.basicConfig(filename = "/var/log/customized-daily-mail.log",
                        level = logging.DEBUG)

    logging.info("Info")
    logging.debug("Debug")


    print_formatting()

    day_of_week, tomorrow, int_month, str_month, day, year = \
            construct_time_variables(datetime.datetime.today())

    new_snow, daily_snow, settled_depth, seasonal_snowfall = \
            bridger_bowl_snow_report()

    temp, weather, humid, wind_dir, wind_speed = \
            bozeman_weather_report()

    sched_date = date_string(int_month, day, year)
    scores, scheduled_games = espn_nba_report(sched_date, tomorrow)

    # Message to send.
    message = (
            "Subject: Update for %s, %s %s\n\n"
	    "Hello, Joshwa. Here's your daily update--\r"
    	    "It is %s degrees and %s outside right now. "
            "The wind is blowing %s mph %s. The "
	    "relative humidy is %s.\r\r"
            "Here's the link for the full weather: %s\n\n"
	    "Snow report for Bridger Bowl:\r"
            "%s\" overnight\n"
	    "%s\" in the last 24 hours\n"
            "%s\" settled base depth\n"
            "%s\" seasonal snowfall\n\n"
	    "Here's the link for the full snow report: %s\n"
              ) % (day_of_week, str_month, day,
                   temp, weather, wind_speed, wind_dir, humid, weather_url,
                   new_snow, daily_snow, settled_depth, seasonal_snowfall,
                   snow_report_url)

    if len(scores) > 0:
        message += "\nHere are the scores for yesterday's NBA games:\n"

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
            ("http://espn.go.com/nba/schedule/_/date/" + sched_date)

    message += "\n\nHave a great %s!" % day_of_week

    send_email(message)
    print "Script executed successfully. Mail sent."

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        traceback.print_exc()
