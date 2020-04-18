import datetime
import requests
import os

import CaseScraper
import DeathScraper
# import RegionScraper

def get_date_time():
    now = datetime.datetime.now()
    date = now.strftime("%Y.%m.%d.")
    time = now.strftime("%H:%M")
    return date, time


def connect_url(url):
    source = requests.get(url)
    return source.text


def get_abs_path(rel_path):
    project_folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(project_folder, rel_path)


URL_cases = "https://koronavirus.gov.hu/"
URL_deaths = "https://koronavirus.gov.hu/elhunytak"
URL_regions = "https://koronavirus.gov.hu/terkepek/fertozottek"

src_cases = connect_url(URL_cases)
src_deaths = connect_url(URL_deaths)
src_regions = connect_url(URL_regions)

path_cases = "data/case_DATA.csv"
path_deaths = "data/death_DATA.csv"
path_conditions = "data/conditions_DATA.csv"
path_regions = "data/region_DATA.csv"

file_cases = get_abs_path(path_cases)
file_deaths = get_abs_path(path_deaths)
file_conditions = get_abs_path(path_conditions)
file_regions = get_abs_path(path_regions)

log_date, log_time = get_date_time()


case_scraper = CaseScraper.CaseScraper(file_cases, src_cases, src_deaths, log_date, log_time)
case_scraper.run()
update_date = case_scraper.date
update_time = case_scraper.time
del case_scraper


death_scraper = DeathScraper.DeathScraper(file_deaths, file_conditions, src_deaths, log_date, log_time, update_date,
                                          update_time, force_conditions_update=True)
page_count = death_scraper.get_page_count()
for i in range(1, page_count+1):
    url_i = "https://koronavirus.gov.hu/elhunytak?page={0}".format(i)
    src_i = connect_url(url_i)
    death_scraper.add_src(src_i)
death_scraper.run()
del death_scraper


# region_scraper = RegionScraper.RegionScraper(file_regions, src_regions, log_date, log_time, 1, 1)
# region_scraper.get_image()
# del region_scraper
