import bs4 as bs
import pandas as pd


def parse_number(number):
    try:
        number = number.replace(' ', '')
        number = int(number)
        return number
    except ValueError:
        print("something bad happened while parsing number")
        return None


def add_row(df, row):
    df.loc[-1] = row
    df.index = df.index + 1
    return df.sort_index()


def format_row_to_string(df, index_offset=0):
    return_list = []
    for index, row in df.iterrows():
        if len(row) > 0:
            formatted_row = str(index + index_offset)
            for data in row:
                formatted_row += "," + str(data)
            return_list.append(formatted_row)
    return return_list


def read_conditions(data_list):
    return_list = []
    conditions = data_list[1].split(',')
    dead_id = data_list[0]
    for condition in conditions:
        condition = condition.strip()
        if condition != "":
            return_list.append([dead_id, condition])
    return return_list


class DeathScraper:
    __slots__ = ["file_cases", "file_conditions", "src_deaths", "log_date", "log_time", "date", "time", "do_log",
                 "force_conditions_update", "prev_death_count", "table_deaths", "table_conditions"]

    def __init__(self, file_cases, file_conditions, src_deaths, log_date, log_time, date, time, do_log=True,
                 force_conditions_update=False):
        self.file_cases = file_cases
        self.file_conditions = file_conditions
        self.src_deaths = [src_deaths]
        self.log_date = log_date
        self.log_time = log_time
        self.date = date
        self.time = time
        self.do_log = do_log
        self.force_conditions_update = force_conditions_update

        self.prev_death_count = self.get_prev_death_count()
        self.table_deaths = pd.DataFrame(columns=["log_date", "log_time", "date",
                                                  "time", "dead_id", "sex", "age"])
        self.table_conditions = pd.DataFrame(columns=["dead_id", "conditions"])

    def get_page_count(self):
        soup = bs.BeautifulSoup(self.src_deaths[0], "lxml")
        list_item = soup.find("li", {"class": "pager-last"})
        link = list_item.find("a")["href"]
        page_count = link.replace('https://koronavirus.gov.hu', '')
        page_count = page_count.replace('/elhunytak?page=', '')
        return int(page_count)

    def get_prev_death_count(self):
        with open(self.file_cases, 'r') as df:
            lines = df.read().splitlines()
            last_data = lines[-1]

        last_data_list = last_data.split(',')
        return int(last_data_list[5])

    def scrape_data(self):
        read_data = True
        for src in self.src_deaths:
            soup = bs.BeautifulSoup(src, "lxml")
            table = soup.find("tbody")

            for table_row in table.find_all("tr"):

                column = 0
                deaths_data = []
                for table_data in table_row.find_all("td"):
                    data = None
                    if read_data:
                        if column <= 2:
                            if column == 0:
                                data = parse_number(table_data.string)
                                if data == self.prev_death_count:
                                    read_data = False
                                    data = None

                            elif column == 1:
                                data = table_data.string
                                if "Nő" in data:
                                    data = "Nő"
                                elif "Férfi" in data:
                                    data = "Férfi"
                                else:
                                    print("Something happened while parsing sex")
                            elif column == 2:
                                data = parse_number(table_data.string)
                            if data is not None:
                                deaths_data.append(data)

                        elif column > 3:
                            print("Something happened while parsing column index")
                    column += 1

                if read_data:
                    data_row = [self.log_date, self.log_time, self.date, self.time, *deaths_data]
                    row_series = pd.Series(data_row, index=self.table_deaths.columns)
                    self.table_deaths = self.table_deaths.append(row_series, ignore_index=True)

                column = 0
                conditions_data = []
                for table_data in table_row.find_all("td"):
                    data = None
                    if column == 0:
                        data = parse_number(table_data.string)
                    if column == 3:
                        data = table_data.string

                    elif column > 3:
                        print("Something happened while parsing column index")
                    if data is not None:
                        conditions_data.append(data)
                    column += 1

                for condition in read_conditions(conditions_data):
                    row_series = pd.Series(condition, index=self.table_conditions.columns)
                    self.table_conditions = self.table_conditions.append(row_series, ignore_index=True)

        self.table_deaths = self.table_deaths.sort_values(by=["dead_id"], ascending=True, ignore_index=True)
        self.table_conditions = self.table_conditions.sort_values(by=["dead_id"], ascending=True, ignore_index=True)

    def update_data(self):
        write_data = format_row_to_string(self.table_deaths, self.prev_death_count)
        update = False
        if len(write_data) > 0:
            update = True

        if update:
            with open(self.file_cases, 'a', encoding="utf-8") as df:
                for write_string in write_data:
                    df.write("\n" + write_string)

        if update or self.force_conditions_update:
            write_data = format_row_to_string(self.table_conditions)
            with open(self.file_conditions, 'w', encoding="utf-8") as df:
                df.write("log_date,{0}\nlog_time,{1}\ndate,{2}\ntime,{3}\n".format(self.log_date, self.log_time,
                                                                                   self.date, self.time))
                df.write("index,dead_id,condition")
                for write_string in write_data:
                    df.write("\n" + write_string)

        if update:
            return True
        else:
            return False

    def run(self):
        self.scrape_data()
        success = self.update_data()
        if self.do_log:
            if success:
                print(self.log_date, ",", self.log_time, ":", "New death data found, file updated successfully.")
            else:
                print(self.log_date, ",", self.log_time, ":", "No new death data found.")
