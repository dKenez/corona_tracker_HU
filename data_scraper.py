import ssl
import urllib.request
import certifi
import bs4 as bs

import datetime
import time


def connect_url(url):
    source = urllib.request.urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    # print("result code: " + str(source.getcode()))
    return source


def scrape_data(source):
    data = []
    soup = bs.BeautifulSoup(source, "lxml")

    header = soup.find(id="block-block-1")
    paragraph = header.p.string
    parse_date_time(paragraph, data)

    for diagram_a in soup.find_all("div", {"class": "diagram-a"}):
        number = diagram_a.find("span", {"class": "number"})
        parse_number(number.string, data)

    return data


def parse_date_time(date_time, data):
    split = date_time.split()
    if len(split) == 5:
        data.append(split[-2])
        t = split[-1]
        split = t.split('.')
        if len(split) > 1:
            data.append(split[0] + ':' + split[1])
        else:
            data.append(t)
        return True
    else:
        return False


def parse_number(num, data):
    try:
        num = num.replace(' ', '')
        num = int(num)
        num = str(num)
        data.append(num)
        return True
    except ValueError:
        return False


def update_data(data, data_file, cache_file):
    write_data = []
    with open(cache_file, 'r') as cf:
        cached_data = cf.readline()
    cached_data_list = cached_data.split(',')
    cdl_len = len(cached_data_list)
    update = False
    for i in range(3, cdl_len):
        if cached_data_list[i] != data[i-3]:
            update = True

    if update:
        index = str(int(cached_data_list[0]) + 1)

        now = datetime.datetime.now()
        log_date = now.strftime("%Y.%m.%d.")
        log_time = now.strftime("%H:%M")

        write_data.append(index)
        write_data.append(log_date)
        write_data.append(log_time)
        for d in data:
            write_data.append(d)

        separator = ','
        write_string = separator.join(write_data)

        with open(cache_file, 'w') as cf:
            cf.write(write_string)
        with open(data_file, 'a') as df:
            df.write("\n" + write_string)

        return True

    else:
        return False


def generate_report():
    return None


URL = "https://koronavirus.gov.hu/"
DATA_FILE = "data/corona_DATA_HU.csv"
CACHE_FILE = "data/cache.csv"

while True:
    p_now = datetime.datetime.now()
    p_log_date = p_now.strftime("%Y.%m.%d.")
    p_log_time = p_now.strftime("%H:%M")
    try:
        webpage = connect_url(URL)
        data_list = scrape_data(webpage)
        success = update_data(data_list, DATA_FILE, CACHE_FILE)
        if success:
            print(p_log_date, ", ", p_log_time, ": ", "New data found, file updated successfully.")
        else:
            print(p_log_date, ", ", p_log_time, ": ", "No new data found.")

    except Exception as error:
        print(p_log_date, ", ", p_log_time, ": ", error)
    time.sleep(60 * 10)
