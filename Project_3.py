# 3rd project - Elections scraper

import csv

import requests
from bs4 import BeautifulSoup as bs


print("""
Welcome to my election app!
You can get election results of 2017 of every municipality in chosen district
downloaded into created csv file with name of your choice.

Please choose the district by the 'X' key in the column 'Výběr obce'
at this page https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ and copy the url.
""")


def get_user_input():
    while True:
        url = input("Enter the url of list of municipalities: ")
        file_name = input("""Enter name of the file without the suffix .csv,
where you want to save the data: """)
        if check_user_input(url, file_name):
            return url, file_name


def check_user_input(url, file_name):
    if ".csv" not in file_name and\
            "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=" in url and\
            "&xnumnuts=" in url:
        get_data(url)
        print("Downloading data...")
        return True
    else:
        print("Wrong url or file name. Please enter again.")
        return False


def get_data(url):
    r = requests.get(url)
    soup = bs(r.text, "html.parser")
    return soup


def get_code_and_location(tr):
    tds = tr.find_all("td")
    code = tds[0].getText()
    location = tds[1].getText()
    url_part = tds[0].find("a").get("href")
    return code, location, url_part


def make_data_dict(row):
    code, location, url_part = get_code_and_location(row)
    url1 = "https://volby.cz/pls/ps2017nss/" + url_part
    soup = get_data(url1)  # data from one district page
    tables = soup.find_all("table")
    cells = tables[0].find_all("td")  # table of district overview
    data_dict = {"code": code,
                 "location": location,
                 "registered": cells[3].getText(),
                 "envelopes": cells[6].getText(),
                 "valid": cells[7].getText()
                 }

    for table in tables[1:]:  # tables of candidate parties
        trs = table.find_all("tr")  # find all rows
        for tr in trs[2:-1]:  # first two rows are header, last row is blank
            tds = tr.find_all("td")
            candidate_party = tds[1].getText()
            votes = tds[2].getText()
            data_dict[candidate_party] = votes
    return data_dict


def get_data_list(soup):
    tables_of_districts = soup.find_all("div", {"class": "t3"})
    data_list = []
    for table in tables_of_districts:
        all_rows = table.find_all("tr")
        for row in all_rows[2:]:  # first two rows are headers
            try:
                data_list.append(make_data_dict(row))
            except AttributeError:
                break
    return data_list


def write_to_csv(data_list, file_name):
    with open(file_name + ".csv", "w", encoding="utf-8", newline="") as file:
        header = data_list[0].keys()
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(data_list)


def main():
    url, file_name = get_user_input()
    soup = get_data(url)
    data_list = get_data_list(soup)
    write_to_csv(data_list, file_name)


main()

