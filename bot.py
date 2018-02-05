import datetime
import csv
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
    except:
        print('Error connecting to {0}'.format(base_url))
        return False


def parse_html(html):
    # create soup object
    soup = BeautifulSoup(html, 'html.parser')
    output_list = []
    try:
        # parses soup object to get article id, rank, score, and title
        tr_blocks = soup.find_all('tr', class_='athing')
        for tr in tr_blocks:
            tr_id = tr.get('id')
            
            try:
                score = soup.find(id='score_{0}'.format(tr_id)).string
            except:
                score = '0 points'
            
            article_info = {
                'id': tr_id,
                'rank': tr.span.string,
                'score': score,
                'title': tr.find(class_='storylink').string
            }
            # appends article_info to output_list
            output_list.append(article_info)
    except:
        print('parsing error')
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
    browser = get_driver()
    page_number = 1
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = 'output_{0}.csv'.format(output_timestamp)
    while page_number <= 20:
        if connect_to_base(browser, page_number):
            sleep(2)
            html = browser.page_source
            output_list = parse_html(html)
            write_to_file(output_list, filename) 
            page_number = page_number + 1
            
        else:
            print('Error connecting to Hacker News')

    browser.quit()
    end_time = time()
    print('Elapsed run time: {0} seconds'.format(end_time - start_time))
