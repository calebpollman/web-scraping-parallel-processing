import datetime
from time import sleep, time

from scraper.scraper import get_driver, connect_to_base, \
    parse_html, write_to_file


def run_process(page_number, filename, browser):
    # browser = get_driver()
    if connect_to_base(browser, page_number):
        sleep(2)
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename)
    else:
        print('Error connecting to hackernews')


if __name__ == '__main__':
    start_time = time()
    current_page = 1
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f'output_{output_timestamp}.csv'
    browser = get_driver()
    while current_page <= 3:
        run_process(current_page, output_filename, browser)
        current_page = current_page + 1
    browser.quit()
    end_time = time()
    elapsed_time = end_time - start_time
    print(f'Elapsed run time: {elapsed_time} seconds')
