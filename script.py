from time import sleep, time
import datetime

from scraper.scraper import get_driver, connect_to_base, parse_html, write_to_file


if __name__ == '__main__':
    start_time = time()
    browser = get_driver()
    page_number = 1
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = 'output_{0}.csv'.format(output_timestamp)
    while page_number <= 20:
        if connect_to_base(browser, page_number):
            sleep(2)
            html_source = browser.page_source
            output = parse_html(html_source)
            write_to_file(output, filename)
        else:
            print('Error connecting to Hacker News')
        page_number = page_number + 1
    browser.quit()
    end_time = time()
    print('Elapsed run time: {0} seconds'.format(end_time - start_time))