from time import sleep, time
import datetime
from itertools import repeat

from scraper.scraper import get_driver, connect_to_base, parse_html, write_to_file
from multiprocessing import Pool, cpu_count


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
    filename = 'output_{0}.csv'.format(output_timestamp)
    with Pool(cpu_count()-1) as p:
        p.starmap(run_process, zip(range(1, 21), repeat(filename)))
    p.close()
    p.join()
    
    end_time = time()
    print('Elapsed run time: {0} seconds'.format(end_time - start_time))