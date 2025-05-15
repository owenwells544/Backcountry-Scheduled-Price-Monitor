# Backcountry Scheduled Price Monitor
web scraper implemented using apscheduler and scrapy to pull product listings daily from backcountry.com

# USAGE
python scheduler.py --hour 8 --minute 0 --keywords "backpacks" 
python scheduler.py --hour 8 --minute 0 --keywords "climbing,shoes" 

HOUR ARG: integer hour (0,23) for the hour the scheduler should run the scraper

MINUTE ARG: integer minute (0,59) for the minute of the hour the scheduler should run the scraper

KEYWORDS ARG: scraper will pull all listings from the search page on backcountry.com with the provided keywords as the search term
If multiple keywords are supplied, search term will include spaces ie "climbing,shoes" -> climbing shoes

# OUTPUT
The output is in the form of a csv file, each listing includes a field for
brand, product, color, availability, price, and url.
Duplicates are handled by the scraper.

# PROBLEMS/SOLUTIONS
403 error: initially the scraper was getting denied access and given error code 403.
This was fixed by including a parameter in the custom settings field that specifies a
user agent so that the request appears to originate from a normal browser.

Duplicate Listings: initially there were duplicate listings appearing in the result csv.
This was fixed by generating a unique listing id for every listing that is meaningfully different,
and storing a set of these ids for future comparison.

Hardcoded values: initially the keyword and start time variables were hardcoded in the scripts.
In order to make interacting with the scaper more user friendly, an argparse parser object was used so that
the user can supply these values to the scheduler, which in turn supplies the spider itself with the keywords
via a kwargs argument to the runspider function.

Keyboard Interrupt: The keyboard interrupt ctrl c does not work to shut down the scheduler, due to how scrapy
spiders are implemented. Initial research has not revealed an easy fix for this problem, and the scheduler must be shut down
by killing the terminal it is running in. I attempted to use a reactor object imported from twisted.internet, but this did not solve the issue.

Finding All Listings: Initially the spider had to be supplied with a url for a specific product. In order to make the scraper more
useful I wanted to have the scraper pull all listings from a given search page. The scraper pulls all url extensions contained 
in the chakra linkboxes on the search page, and builds each product url using the urljoin library function. Thus all versions of a given
product available on the site are included in the result csv file. Additionally, the scraper checks for a "next page" link to make sure
listings on any subsequent search result pages are not lost.

