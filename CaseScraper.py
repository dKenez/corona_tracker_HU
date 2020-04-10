import bs4 as bs


def parse_number(number):
    try:
        number = number.replace(' ', '')
        number = int(number)
        number = str(number)
        return number
    except ValueError:
        print("something bad happened while parsing number")
        return None


class CaseScraper:
    __slots__ = ["file_cases", "src_cases", "src_deaths", "log_date", "log_time", "do_log", "date", "time", "cases",
                 "recovered", "died", "quarantined", "tested"]

    def __init__(self, file_cases, src_cases, src_deaths, log_date, log_time, do_log=True):
        self.file_cases = file_cases
        self.src_cases = src_cases
        self.src_deaths = src_deaths
        self.log_date = log_date
        self.log_time = log_time
        self.do_log = do_log

        self.date = None
        self.time = None
        self.cases = None
        self.recovered = None
        self.died = None
        self.quarantined = None
        self.tested = None

    def scrape_data(self):
        soup_cases = bs.BeautifulSoup(self.src_cases, "lxml")

        header = soup_cases.find(id="block-block-1")
        date_time_paragraph = header.p.string
        self.parse_date_time(date_time_paragraph)

        for diagram_a in soup_cases.find_all("div", {"class": "diagram-a"}):
            label = diagram_a.find("span", {"class": "label"}).string
            if label == "Fertőzött":
                number = diagram_a.find("span", {"class": "number"})
                self.cases = parse_number(number.string)

            elif label == "Gyógyult":
                number = diagram_a.find("span", {"class": "number"})
                self.recovered = parse_number(number.string)

            elif label == "Elhunytak":
                soup_deaths = bs.BeautifulSoup(self.src_deaths, "lxml")
                table_first_row = soup_deaths.find("tr", {"class", "odd views-row-first"})
                number = table_first_row.find("td", {"class", "views-field views-field-field-elhunytak-sorszam"})
                self.died = parse_number(number.string)

            elif label == "Hatósági házi karanténban":
                number = diagram_a.find("span", {"class": "number"})
                self.quarantined = parse_number(number.string)

            elif label == "Mintavétel":
                number = diagram_a.find("span", {"class": "number"})
                self.tested = parse_number(number.string)

            else:
                print("something bad happened while reading labels")

    def parse_date_time(self, date_time):
        split = date_time.split()
        if len(split) == 5:
            self.date = split[-2]
            time = split[-1]
            split = time.split('.')
            if len(split) == 1:
                self.time = split[0]
            elif len(split) == 2:
                self.time = split[0] + ':' + split[1]
            else:
                print("Something happened while parsing time")
        else:
            print("Something happened while parsing date_time string")

    def update_data(self):
        write_data = []
        data = (self.date, self.time, self.cases, self.recovered, self.died, self.quarantined, self.tested)
        with open(self.file_cases, 'r') as df:
            lines = df.read().splitlines()
            last_data = lines[-1]

        last_data_list = last_data.split(',')
        ldl_len = len(last_data_list)
        update = False
        for i in range(3, ldl_len):
            if last_data_list[i] != data[i - 3]:
                update = True

        if update:
            index = str(int(last_data_list[0]) + 1)

            write_data.append(index)
            write_data.append(self.log_date)
            write_data.append(self.log_time)
            for d in data:
                write_data.append(d)
            separator = ','
            write_string = separator.join(write_data)

            with open(self.file_cases, 'a', encoding="utf-8") as df:
                df.write("\n" + write_string)

            return True
        else:
            return False

    def run(self):
        self.scrape_data()
        success = self.update_data()
        if self.do_log:
            if success:
                print(self.log_date, ",", self.log_time, ":", "New case data found, file updated successfully.")
            else:
                print(self.log_date, ",", self.log_time, ":", "No new case data found.")
