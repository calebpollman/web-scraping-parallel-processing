import sys
import csv
import datetime
from time import sleep, time

from selenium import webdriver
from bs4 import BeautifulSoup


def get_driver():
    # initialize driver
    driver = webdriver.Chrome()
    return driver


def connect_to_base(browser, page_number):
    base_url = 'https://news.ycombinator.com/news?p={0}'.format(page_number)
    try:
        browser.get(base_url)
        return True
    except Exception as ex:
        print('Error connecting to {0}'.format(base_url))
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
                score = soup.find(id='score_{0}'.format(tr_id)).string
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
        print('Parsing error')
    # returns output_list
    return output_list


def write_to_file(output_list, filename):
    for row in output_list:
        with open(filename, 'a') as csvfile:
            fieldnames = ['id', 'rank', 'score', 'title']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(row)


if __name__ == '__main__':
    start_time = time()
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = 'output_{0}.csv'.format(output_timestamp)
    # check for command line args
    try:
        test_flag = sys.argv[1]
    except Exception as ex:
        test_flag = 'null'
    if sys.argv[1] == '--test':
        # test mode
        print('TEST MODE')
        html = open('test/test.html')
        output_list = parse_html(html)
        write_to_file(output_list, filename)
    else:
        # regular mode
        browser = get_driver()
        page_number = 1
        while page_number <= 20:
            if connect_to_base(browser, page_number):
                sleep(2)
                html_source = browser.page_source
                output = parse_html(html_source)
                write_to_file(output, filename)
                page_number = page_number + 1
            else:
                print('Error connecting to Hacker News')
        browser.quit()
        end_time = time()
        print('Elapsed run time: {0} seconds'.format(end_time - start_time))
