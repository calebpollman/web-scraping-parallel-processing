# Speeding Up Web Scraping with Parallel Processing

## Introduction

This is a quick post that looks at how to speed up a simple, Python-based web scraping and crawling script with parallel processing via the multiprocessing library. We'll also break down the script itself and show how to test the parsing functionality.

TODO: add image

After completing this tutorial you should be able to:

1. Scrape and crawl websites with Selenium and parse HTML with Beautiful Soup
1. Set up unittest to test the scraping and parsing functionalities
1. Set up multiprocessing to execute the web scraper in parallel
1. Configure headless mode for ChromeDriver with Selenium

## Project Setup

Clone down the repo if you'd like to follow along. From the command line run the following commands:

```sh
$ git clone git@github.com:calebpollman/web-scraping-parallel-processing.git
$ cd web-scraping-parallel-processing
$ python3 -m venv env
(env)$ pip install -r requirements.txt
```

Install [ChromeDriver](https://sites.google.com/a/chromium.org/ChromeDriver/) globally. (We're using version [2.3.5](https://chromedriver.storage.googleapis.com/index.html?path=2.35/)).

## Script Overview

The script traverses and scrapes the first 20 pages of [Hacker News](https://news.ycombinator.com/) for information about the current articles listed using [Selenium](http://www.seleniumhq.org/projects/webdriver/) to automate interaction with the site and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to parse the HTML.

*script.py*:

```python
import datetime
from time import sleep, time

from scrapers.scraper import get_driver, connect_to_base, \
    parse_html, write_to_file


def run_process(page_number, filename, browser):
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
    while current_page <= 20:
        print(f'Scraping page #{current_page}...')
        run_process(current_page, output_filename, browser)
        current_page = current_page + 1
    browser.quit()
    end_time = time()
    elapsed_time = end_time - start_time
    print(f'Elapsed run time: {elapsed_time} seconds')
```

Let's start with the main-conditon block. After setting a few variables, the browser is initialized via `get_driver()` from *scrapers/scraper.py*.

```python
if __name__ == '__main__':
    # set variables
    start_time = time()
    current_page = 1
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f'output_{output_timestamp}.csv'
    browser = get_driver() # <--- here
    # scrape and crawl
    while current_page <= 20:
        print(f'Scraping page #{current_page}...')
        run_process(current_page, output_filename, browser)
        current_page = current_page + 1
    # exit
    browser.quit()
    end_time = time()
    elapsed_time = end_time - start_time
    print(f'Elapsed run time: {elapsed_time} seconds')
```

A `while` loop is then configured to control the flow of the overall scraper.

```python
if __name__ == '__main__':
    # set variables
    start_time = time()
    current_page = 1
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f'output_{output_timestamp}.csv'
    browser = get_driver()
    # scrape and crawl
    while current_page <= 20: # <--- here
        print(f'Scraping page #{current_page}...')
        run_process(current_page, output_filename, browser)
        current_page = current_page + 1
    # exit
    browser.quit()
    end_time = time()
    elapsed_time = end_time - start_time
    print(f'Elapsed run time: {elapsed_time} seconds')
```

Within the loop, `run_process()` is called, which houses the connection and scraping functions.

```python
def run_process(page_number, filename, browser):
    if connect_to_base(browser, page_number):
        sleep(2)
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename)
    else:
        print('Error connecting to hackernews')
```

In `run_process()`, the browser instance and a page number are passed to `connect_to_base()`.

```python
def run_process(page_number, filename, browser):
    if connect_to_base(browser, page_number): # <--- here
        sleep(2)
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename)
    else:
        print('Error connecting to hackernews')
```

This function attempts to connect to Hacker News and then uses Selenium's explicit wait functionality to ensure the element with `id='hnmain'` has loaded before continuing.

```python
def connect_to_base(browser, page_number):
    base_url = f'https://news.ycombinator.com/news?p={page_number}'
    connection_attempts = 0
    while connection_attempts < 3:
        try:
            browser.get(base_url)
            # wait for table element with id = 'hnmain' to load
            # before returning True
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, 'hnmain'))
            )
            return True
        except Exception as ex:
            connection_attempts += 1
            print(f'Error connecting to {base_url}.')
            print(f'Attempt #{connection_attempts}.')
    return False
```

> Review the Selenium [docs](http://selenium-python.readthedocs.io/waits.html#explicit-waits) for more information on explicit wait.

To emulate a human user, `sleep(2)` is called after the browser has connected to Hacker News.

```python
def run_process(page_number, filename, browser):
    if connect_to_base(browser, page_number):
        sleep(2) # <--- here
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename)
    else:
        print('Error connecting to hackernews')
```

Once the page has loaded and `sleep(2)` has executed, the browser grabs the HTML source, which is then passed to `parse_html()`.

```python
def run_process(page_number, filename, browser):
    if connect_to_base(browser, page_number):
        sleep(2)
        html = browser.page_source # <--- here
        output_list = parse_html(html) # <--- here
        write_to_file(output_list, filename)
    else:
        print('Error connecting to hackernews')
```

`parse_html()` uses Beautiful Soup to parse the HTML, generating a list of dicts with the appropriate data.

```python
def parse_html(html):
    # create soup object
    soup = BeautifulSoup(html, 'html.parser')
    output_list = []
    # parse soup object to get article id, rank, score, and title
    tr_blocks = soup.find_all('tr', class_='athing')
    article = 0
    for tr in tr_blocks:
        article_id = tr.get('id')
        article_url = tr.find_all('a')[1]['href']
        # check if article is a hacker news article
        if 'item?id=' in article_url:
            article_url = f'https://news.ycombinator.com/{article_url}'
        load_time = get_load_time(article_url)
        try:
            score = soup.find(id=f'score_{article_id}').string
        except Exception as ex:
            score = '0 points'
        article_info = {
            'id': article_id,
            'load_time': load_time,
            'rank': tr.span.string,
            'score': score,
            'title': tr.find(class_='storylink').string,
            'url': article_url
        }
        # appends article_info to output_list
        output_list.append(article_info)
        article += 1
    return output_list
```

This function also passes the article URL to `get_load_time()`, which loads the URL and records the subsequent load time.

```python
def get_load_time(article_url):
    try:
        # set headers
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        # make get request to article_url
        response = requests.get(
            article_url, headers=headers, stream=True, timeout=3.000)
        # get page load time
        load_time = response.elapsed.total_seconds()
    except Exception as ex:
        load_time = 'Loading Error'
    return load_time
```

The output is added to a CSV file.

```python
def run_process(page_number, filename, browser):
    if connect_to_base(browser, page_number):
        sleep(2)
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename) # <--- here
    else:
        print('Error connecting to hackernews')
```

`write_to_file()`:

```python
def write_to_file(output_list, filename):
    for row in output_list:
        with open(filename, 'a') as csvfile:
            fieldnames = ['id', 'load_time', 'rank', 'score', 'title', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(row)
```

Finally, back in the `while` loop, the `page_number` is incremented and the process starts over again.

```python
if __name__ == '__main__':
    # set variables
    start_time = time()
    current_page = 1
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f'output_{output_timestamp}.csv'
    browser = get_driver()
    # scrape and crawl
    while current_page <= 20:
        print(f'Scraping page #{current_page}...')
        run_process(current_page, output_filename, browser)
        current_page = current_page + 1 # <--- here
    # exit
    browser.quit()
    end_time = time()
    elapsed_time = end_time - start_time
    print(f'Elapsed run time: {elapsed_time} seconds')
```

> Want to test this out? Grab the full script [here](script.py).

It took about 272 seconds (a little over 4.5 minutes) to run:

```sh
$ python script.py
Scraping page #1...
Scraping page #2...
Scraping page #3...
Scraping page #4...
Scraping page #5...
Scraping page #6...
Scraping page #7...
Scraping page #8...
Scraping page #9...
Scraping page #10...
Scraping page #11...
Scraping page #12...
Scraping page #13...
Scraping page #14...
Scraping page #15...
Scraping page #16...
Scraping page #17...
Scraping page #18...
Scraping page #19...
Scraping page #20...
Elapsed run time: 272.2812077999115 seconds
```

Got it? Great! Let's add some basic testing.

## Testing

To test the parsing functionality without initiating the browser and, thus, making repeated GET requests to Hacker News, you can download the page HTML and parse it locally. This can help avoid scenarios where you may get your IP blocked for making too many requests too quickly while writing and testing your parsing function, as well as saving you time by not needing to fire up a browser every time you run the script.

*test/test_scraper.py*:

```python
import unittest

from scrapers.scraper import parse_html


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
        self.assertTrue(isinstance(self.output, list))

    def test_output_is_a_list_of_dicts(self):
        self.assertTrue(all(isinstance(elem, dict) for elem in self.output))


if __name__ == '__main__':
    unittest.main()
```

Ensure all is well:

```sh
$ python test/test_scraper.py
...
----------------------------------------------------------------------
Ran 3 tests in 69.877s

OK
```

Want to mock `get_load_time()` to bypass the GET request?

```python
import unittest
from unittest.mock import patch

from scrapers.scraper import parse_html


class TestParseFunction(unittest.TestCase):

    @patch('scrapers.scraper.get_load_time')
    def setUp(self, mock_get_load_time):
        mock_get_load_time.return_value = 'mocked!'
        with open('test/test.html', encoding='utf-8') as f:
            html = f.read()
            self.output = parse_html(html)

    def tearDown(self):
        self.output = []

    def test_output_is_not_none(self):
        self.assertIsNotNone(self.output)

    def test_output_is_a_list(self):
        self.assertTrue(isinstance(self.output, list))

    def test_output_is_a_list_of_dicts(self):
        self.assertTrue(all(isinstance(elem, dict) for elem in self.output))


if __name__ == '__main__':
    unittest.main()
```

## Configure Multiprocessing

Now comes up the fun part! By making just a few changes to the script, we can speed things up:

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

With the `multiprocessing` library, `Pool` is used to spawn a number of subprocesses based on the number of CPUs available on the system (minus one since the system processes take up a core).


> This script is tested on a i7 Macbook Pro that has [8 cores](https://superuser.com/a/1101314).

Run:

```sh
$ python script_parallel.py
Elapsed run time: 62.95027780532837 seconds
```

> Check out the completed script [here](script_parallel.py).

# Configure Headless ChromeDriver

To speed things up even further we can run Chrome in headless mode by simply updating `get_driver()` in *scrapers/scraper.py*:

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

Run:

```sh
$ python script_parallel.py
Elapsed run time: 58.14033889770508 seconds
```

# Conclusion/After Analysis

TODO: finish conclusion

With a small amount of code, we were able to take
