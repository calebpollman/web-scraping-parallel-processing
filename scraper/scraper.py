import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


# def get_driver():
#     # initialize driver
#     driver = webdriver.Chrome()
#     return driver


def get_driver():
    # initialize options
    options = webdriver.ChromeOptions()
    # pass in headless argument to options
    options.add_argument('--headless')
    # initialize driver
    driver = webdriver.Chrome(chrome_options=options)
    return driver


def connect_to_base(browser, page_number):
    base_url = f'https://news.ycombinator.com/news?p={page_number}'
    connection_attempts = 0
    while connection_attempts < 3:
        try:
            browser.get(base_url)
            # wait for table element with id = 'hnmain' to load
            # before returning True
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, 'hnmain'))
            )
            return True
        except Exception as ex:
            print(f'Error connecting to {base_url}')
            connection_attempts += 1
    return False


def parse_html(html):
    # create soup object
    soup = BeautifulSoup(html, 'html.parser')
    output_list = []
    try:
        # parse soup object to get article id, rank, score, and title
        tr_blocks = soup.find_all('tr', class_='athing')
        for tr in tr_blocks:
            tr_id = tr.get('id')
            try:
                score = soup.find(id=f'score_{tr_id}').string
            except Exception as ex:
                score = '0 points'
            article_info = {
                'id': tr_id,
                'rank': tr.span.string,
                'score': score,
                'title': tr.find(class_='storylink').string
            }
            # appends article_info to output_list
            output_list.append(article_info)
    except Exception as ex:
        print('Parsing Error')
    # returns output_list
    return output_list


def write_to_file(output_list, filename):
    for row in output_list:
        with open(filename, 'a') as csvfile:
            fieldnames = ['id', 'rank', 'score', 'title']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(row)
