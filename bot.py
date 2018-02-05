import datetime
import csv
from time import sleep, time

from selenium import webdriver
from bs4 import BeautifulSoup


def get_driver():
    driver = webdriver.Chrome()
    return driver


def connect_to_base(browser, page_count):
    base_url = 'https://news.ycombinator.com/news?p={0}'.format(page_count)
    try:
        browser.get(base_url)
        return True
    except:
        print('Error connecting to {0}'.format(BASE_URL))
        return False


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    output_list = []
    try:
        tr_blocks = soup.find_all('tr', class_ = 'athing')
        for tr in tr_blocks:
            a_elements = tr.find_all('a')
            tr_id = tr.get('id')
            
            try:
                score = soup.find(id='score_{0}'.format(tr_id)).string
            except:
                score = 'null'
            
            article_info = {
                'id': tr_id,
                'rank': tr.span.string,
                'score': score,
                'title': a_elements[1].string
            }
            output_list.append(article_info)
    except:
        print('parsing error')

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
    page_count = 1
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = 'output_{0}.csv'.format(output_timestamp)
    while page_count <= 20:
        if connect_to_base(browser, page_count):
            sleep(2)
            html = browser.page_source
            output_list = parse_html(html)
            write_to_file(output_list, filename) 
            page_count = page_count + 1
            
        else:
            print('Error connecting to Hacker News')

    browser.quit()
    end_time = time()
    print('Elapsed run time: {0} seconds'.format(end_time - start_time))
