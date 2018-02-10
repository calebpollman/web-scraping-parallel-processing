import datetime
from itertools import repeat
from time import sleep, time
from multiprocessing import Pool, cpu_count

from scrapers.scraper import get_driver, connect_to_base, \
    parse_html, write_to_file


def run_process(page_number, filename):
    browser = get_driver()
    if connect_to_base(browser, page_number):
        sleep(2)
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename)
        browser.quit()
    else:
        print('Error connecting to hackernews')
        browser.quit()


if __name__ == '__main__':
    start_time = time()
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f'output_{output_timestamp}.csv'
    browser = get_driver()
    with Pool(cpu_count()-1) as p:
        p.starmap(run_process, zip(range(1, 21), repeat(output_filename)))
    p.close()
    p.join()
    end_time = time()
    elapsed_time = end_time - start_time
    print(f'Elapsed run time: {elapsed_time} seconds')
