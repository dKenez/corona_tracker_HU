import datetime
import ssl
import urllib.request
import certifi

import CaseScraper
import DeathScraper


def get_date_time():
    now = datetime.datetime.now()
    date = now.strftime("%Y.%m.%d.")
    time = now.strftime("%H:%M")
    return date, time


def connect_url(url):
    source = urllib.request.urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    # print("result code: " + str(source.getcode()))
    return source.read()


URL_cases = "https://koronavirus.gov.hu/"
URL_deaths = "https://koronavirus.gov.hu/elhunytak"
URL_regions = "https://koronavirus.gov.hu/terkepek/fertozottek"

src_cases = connect_url(URL_cases)
src_deaths = connect_url(URL_deaths)
src_regions = connect_url(URL_regions)

file_cases = "data/case_DATA.csv"
file_deaths = "data/death_DATA.csv"
file_conditions = "data/conditions_DATA.csv"
file_regions = "data/region_DATA.csv"

log_date, log_time = get_date_time()

case_scraper = CaseScraper.CaseScraper(file_cases, src_cases, src_deaths, log_date, log_time)
case_scraper.run()
update_date = case_scraper.date
update_time = case_scraper.time


death_scraper = DeathScraper.DeathScraper(file_deaths, file_conditions, src_deaths, log_date, log_time, update_date,
                                          update_time, force_conditions_update=False)
page_count = death_scraper.get_page_count()
for i in range(1, page_count+1):
    url_i = "https://koronavirus.gov.hu/elhunytak?page={0}".format(i)
    src_i = connect_url(url_i)
    death_scraper.src_deaths.append(src_i)
death_scraper.run()
