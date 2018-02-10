# Speeding Up Web Scraping with Parallel Processing

## Introduction

TODO: add basic intro

After completing this tutorial you should be able to:

1. Scrape and crawl websites with Selenium and Beautiful Soup
1. Set up unittest to test the scraping and parsing functionalities
1. Set up multiprocessing to execute the web scraper in parallel
1. Configure headless mode for Chromedriver with Selenium

## Project Setup

Clone down the repo if you'd like to follow along. From the command line run the following commands:

```sh
$ git clone git@github.com:calebpollman/web-scraping-parallel-processing.git
$ cd web-scraping-parallel-processing
$ python3 -m venv env
(env)$ pip install -r requirements.txt
```

Install `chromedriver` globally. You can find instructions [here](https://sites.google.com/a/chromium.org/chromedriver/).

## Basic Project Overview

The script traverses and scrapes the first 20 pages of [Hacker News](https://news.ycombinator.com/) for information about the current articles listed using [Selenium](http://www.seleniumhq.org/projects/webdriver/) to automate interaction with the site and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to parse the HTML.

### The Scraper

First, within *script.py* a `while` loop is configured to control the flow of the overall scraper:

```python
if __name__ == '__main__':
    start_time = time()
    current_page = 1
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f'output_{output_timestamp}.csv'
    while current_page <= 20:
        run_process(current_page, output_filename) # here
        current_page = current_page + 1
    end_time = time()
    elapsed_time = end_time - start_time
    print(f'Elapsed run time: {elapsed_time} seconds')
```

It calls `run_process()`, which houses our connection and scraping functions:

```python
def run_process(page_number, filename):
    browser = get_driver() # here
    if connect_to_base(browser, page_number):
        sleep(2)
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename)
        browser.quit()
    else:
        print('Error connecting to hackernews')
        browser.quit()
```

In `run_process()`, the browser is initialized via `get_driver()` from *scraper/scraper.py*:

```python
def get_driver():
    # initialize driver
    driver = webdriver.Chrome()
    return driver
```

The browser instance along with a page number are passed to `connect_to_base()`:

```python
def run_process(page_number, filename):
    browser = get_driver()
    if connect_to_base(browser, page_number): # here
        sleep(2)
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename)
        browser.quit()
    else:
        print('Error connecting to hackernews')
        browser.quit()
```

This function attempts to connect to Hacker News and then uses Selenium's explicit wait functionality to ensure the element with `id='hnmain'` has loaded before continuing:

```python
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
```

> Review the Selenium [docs](http://selenium-python.readthedocs.io/waits.html#explicit-waits) for more information on explicit wait.

To emulate a human user, `sleep(2)` is called after the browser has connected to Hacker News:

```python
def run_process(page_number, filename):
    browser = get_driver()
    if connect_to_base(browser, page_number):
        sleep(2) # here
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename)
        browser.quit()
    else:
        print('Error connecting to hackernews')
        browser.quit()
```

Once the page has loaded and `sleep(2)` has executed, the browser grabs the HTML source, which is then passed to `parse_html()`:

```python
def run_process(page_number, filename):
    browser = get_driver()
    if connect_to_base(browser, page_number):
        sleep(2)
        html = browser.page_source # here
        output_list = parse_html(html) # and here
        write_to_file(output_list, filename)
        browser.quit()
    else:
        print('Error connecting to hackernews')
        browser.quit()
```

`parse_html()` uses Beautiful Soup to parse the HTML, generating a list of dicts with the appropriate data:

```python
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
```

The output is added to a CSV file:

```python
def run_process(page_number, filename):
    browser = get_driver()
    if connect_to_base(browser, page_number):
        sleep(2)
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename) # here
        browser.quit()
    else:
        print('Error connecting to hackernews')
        browser.quit()
```

`write_to_file()`:

```python
def write_to_file(output_list, filename):
    for row in output_list:
        with open(filename, 'a') as csvfile:
            fieldnames = ['id', 'rank', 'score', 'title']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(row)
```

Finally, back in the `while` loop, the `page_number` is incremented and the process starts over again:

```python
if __name__ == '__main__':
    start_time = time()
    current_page = 1
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f'output_{output_timestamp}.csv'
    while current_page <= 20:
        run_process(current_page, output_filename)
        current_page = current_page + 1 # here
    end_time = time()
    elapsed_time = end_time - start_time
    print(f'Elapsed run time: {elapsed_time} seconds')
```

> Want to test this out? Grab the full script [here](script.py).

It should take about 93 seconds to run:

```sh
$ python script.py
Elapsed run time: 93.19852066040039 seconds
```

Got it? Great! Let's add some basic testing.

## Testing

To test the parsing functionality without initiating the browser and, thus, making repeated get requests to Hacker News, you can download the page HTML and parse it locally. This can help avoid scenarios where you may get your IP blocked for making too many requests too quickly while writing and testing your parsing function, as well as saving you time by not needing to fire up a browser every time you run the script.

*scraper/scraper.py*:

```python
import unittest

from scraper.scraper import parse_html


class TestParseFunction(unittest.TestCase):

    def setUp(self):
        with open('test/test.html', encoding='utf-8') as f:
            html = f.read()
            self.output = parse_html(html)

    def tearDown(self):
        self.output = []

    def test_output_is_not_none(self):
        self.assertIsNotNone(self.output)

    def test_output_is_a_list(self):
        empty_list = []
        self.assertIs(type(self.output), type(empty_list))

    def test_output_is_a_list_of_dicts(self):
        empty_dict = {}
        self.assertIs(type(self.output[0]), type(empty_dict))


if __name__ == '__main__':
    unittest.main()
```

Ensure all is well:

```sh
$ python test/test_scraper.py
...
----------------------------------------------------------------------
Ran 3 tests in 0.573s

OK
```

## Configure Multiprocessing

Now comes up the fun part! By making just a few changes to the script, we speed things up using the `multiprocessing` library:

```python
import datetime
from itertools import repeat
from time import sleep, time
from multiprocessing import Pool, cpu_count

from scraper.scraper import get_driver, connect_to_base, \
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
    with Pool(cpu_count()-1) as p:
        p.starmap(run_process, zip(range(1, 21), repeat(output_filename)))
    p.close()
    p.join()
    end_time = time()
    elapsed_time = end_time - start_time
    print(f'Elapsed run time: {elapsed_time} seconds')
```

`Pool` is used to spawn a number of subprocesses based on the number of CPUs available on the system.

> This script is tested on a i7 Macbook Pro that has [8 cores](https://superuser.com/a/1101314).

Run:

```python
$ python script_parallel.py
Elapsed run time: 20.769462823867798 seconds
```

> Check out the completed script [here](script_parallel.py)

# Configure Headless Chromedriver

To speed things up even further we can run Chrome in headless mode by simply updating `get_driver()` in *scraper/scraper.py*:

```python
def get_driver():
    # initialize options
    options = webdriver.ChromeOptions()
    # pass in headless argument to options
    options.add_argument('--headless')
    # initialize driver
    driver = webdriver.Chrome(chrome_options=options)
    return driver
```

This should take around 19 seconds to complete:

```sh
$ python script_parallel.py
Elapsed run time: 19.63220715522766 seconds
```

# Conclusion/After Analysis

With a small amount of code, we were able to take 
