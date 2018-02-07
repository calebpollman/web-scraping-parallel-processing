# Speeding Up Web Scraping with Parallel Processing

## Introduction

TODO: add basic intro

After completing this tutorial you should be able to:

1. Scrape and crawl websites with Selenium and Beautiful Soup
1. Setup unittest for the scraping function
1. Setup Multiprocessing for a web scraper
1. Configure headless mode for Chromedriver with Selenium

## Project Setup

From the command line run the following commands:

```sh
$ git clone git@github.com:calebpollman/web-scraping-parallel-processing.git
$ pip install -r requirements.txt
```

Install `chromedriver` globally. You can find instructions [here](https://sites.google.com/a/chromium.org/chromedriver/).

## Basic Project Overview

The script traverses and scrapes the first 20 pages of [Hacker News](https://news.ycombinator.com/) for information about the current articles listed using [Selenium](http://www.seleniumhq.org/projects/webdriver/) to automate interaction with the site and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to parse the HTML.

### Chrome Instance

First, a `while` loop is configured to control the remainder of the program flow. It calls `run_process(` which houses our connection and scraping functions, and increments `page_number`:

```python
# script.py
...

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
    page_number = 1
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = 'output_{0}.csv'.format(output_timestamp)
    while page_number <= 20:
        run_process(page_number, filename)
        page_number = page_number + 1
    
    end_time = time()
    print('Elapsed run time: {0} seconds'.format(end_time - start_time))
```

In `run_process()` , the browser is initialized via `get_driver()`:

```python
# scraper/scraper.py

def get_driver():
    # initialize driver
    driver = webdriver.Chrome()
    return driver
```

The browser instance along with a page number is passed to `connect_to_base()`, which attempts to connect to Hacker News, then uses Selenium's explicit wait functionality to ensure the element with *id='hnmain'* has loaded before continuing:

```python
# scraper/scraper.py

def connect_to_base(browser, page_number):
    base_url = 'https://news.ycombinator.com/news?p={0}'.format(page_number)
    connection_attempts = 0
    while connection_attempts < 3:
        try:
            browser.get(base_url)
            # wait for table element with id = hnmain to load before returning True
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, 'hnmain'))
            )
            return True
        except Exception as ex:
            print('Error connecting to {0}'.format(base_url))
            connection_attempts += 1   
    return False
```

> More information on explicit wait in the Selenium docs [here](http://selenium-python.readthedocs.io/waits.html#explicit-waits).

After the browser has connected to Hacker News, ```sleep(2)``` is called. The reason for this is to emulate a human user.

```python
# script.py
...
if connect_to_base(browser, page_number):
        sleep(2)
        html = browser.page_source
...
```

Once the page has loaded and ```sleep(2)``` has executed, the browser grabs the HTML source, which is the passed to `parse_html()`:

```python
# script.py

html_source = browser.page_source
output = parse_html(html_source)
```

`parse_html()` then uses Beautiful Soup to parse the HTML, generating a list of dicts with the appropriate data:

```python
# scraper/scraper.py

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
            # append article_info to output_list
            output_list.append(article_info)
    except Exception as ex:
        print('Parsing Error')
    # returns output_list
    return output_list
```

The output is added to a CSV file via `write_to_file()`:

```python
# scraper/scraper.py

def write_to_file(output_list, filename):
    for row in output_list:
        with open(filename, 'a') as csvfile:
            fieldnames = ['id', 'rank', 'score', 'title']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(row)
```

Finally, `page_number` increments and the process starts over again:

```python
# script.py

page_number = page_number + 1
```

> Want to test this out? Grab the full script [here](script.py).

Got it? Great! Let's add some basic testing.

## Setup Basic Testing

To test the parsing functionality without initiating the browser and, thus, making repeated get requests to Hacker News, you can download the page html and parse it locally. This can help avoid scenarios where you may get your ip blocked for making too many requests too quickly while writing and testing your parsing function, as well as saving you time by not needing to fire up a browser every time you run the script.

Create a `test` directory from the command line:

```sh
$ mkdir test
```

Download the HTML source manually to that directory and rename the file to `test.html`:

![hn](/assets/screenshot.png "Save Screenshot")

Create the *test_scraper.py* file in the *test* directory:

```sh
$ touch test/test_scraper.py
```

Start by importing the scraper functions to be tested along with the `unittest` module at the top of *test/test_scraper.py*:

```python
# test/test_scraper.py

from scraper.scraper import parse_html

import unittest
```

Next, define a class for testing `parse_html()` with a `test_function()` and add the `__main__` block below:

> Note: when writing tests with `unittest`, you need to start the name of each test with `test`, otherwise `unittest` will not run the function.

```python
# test/test_scraper.py
...
import unittest


class testParseFunction(unittest.TestCase):

    def test_function(self):
        output = 1 + 2
        self.assertEqual(output, 3)


if __name__ == '__main__':
    unittest.main()        
```

Run `$ pytest` from the command line, your sample test should pass!

> Note: You may run verbose tests by passing in the verbose flag: `$ pytest -v`

We will now remove the `test_function()` and write our first test, `test_output_is_not_none()`. This test will need to read from *test/test.html* for the html, and pass the result to `parse_html()`:

```python
# test/test_scraper.py
...
class testParseFunction(unittest.TestCase):

    def test_output_is_not_none(self):
        with open('test/test.html', encoding='utf-8') as f:
            html = f.read()
            output = parse_html(html)
        self.assertIsNotNone(output)
```
Run `$ pytest` from the command line and make sure your test passes before moving on.

### Refactor with `setUp()` and `tearDown()`:

When writing tests with the `unittest` module, you can save yourself time, and keep things DRY, by taking advantage of the built-in `setUp()` and `tearDown()` methods. These methods will run before and after each test respectively.

Let's go ahead and refactor our current test to use `setUp()` and `tearDown()`:

```python
# test/test_scraper_py
...
class testParseFunction(unittest.TestCase):

    def setUp(self):
        with open('test/test.html', encoding='utf-8') as f:
            html = f.read()
            self.output = parse_html(html)
    
    def tearDown(self):
        self.output = []

    def test_output_is_not_none(self):
        self.assertIsNotNone(self.output)
...
```
Again, run `4 pytest` before moving on.

Before moving to the next section, let's add a couple type checks for `self.output`:

```python
...
    def test_output_is_not_none(self):
        self.assertIsNotNone(self.output)

    def test_output_is_a_list(self):
        empty_list = []
        self.assertIs(type(self.output), type(empty_list))

    def test_output_is_a_list_of_dicts(self):
        empty_dict = {}
        self.assertIs(type(self.output[0]), type(empty_dict))
...
```

Run `$ pytest` from the command line and if everything passes move on to the next section!

> Grab the code [here](test/test_scraper.py)

## Configure Multiprocessing

In order to setup Multiprocessing we will go through the following steps. At the end we will add a flag to run Chrome headless to increase processing speed.

Add ```Pool``` and  ```cpu_count``` modules from ```multiprocessing``` package and ```repeat``` module from ```itertools``` package to imports near top of *script.py*:

```python
# script.py
...

from time import sleep, time
from itertools import repeat

from selenium import webdriver
from bs4 import BeautifulSoup
from multiprocessing import Pool, cpu_count

...
```

Refactor ```__main__``` to use ```Pool()``` in place of ```while``` loop and remove ```page_number``` variable:

```python
# script.py
...

if __name__ == '__main__':
    start_time = time()
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = 'output_{0}.csv'.format(output_timestamp)
    with Pool(cpu_count()-1) as p:
        p.starmap(run_process, zip(range(1, 21), repeat(filename)))
    p.close()
    p.join()

...
```

> Check out the completed script [here](script_parallel.py)

# Configure Headless Chromedriver

We can go headless with Chrome to speed up processing by adding ```ChromeOptions()``` with the ```--headless``` flag to `get_driver()` in *scraper/scraper.py*:

```python
# scraper/scraper.py
...

def get_driver():
    # initialize options
    options = webdriver.ChromeOptions()
    # pass in headless argument to options
    options.add_argument('--headless')
    # initialize driver
    driver = webdriver.Chrome(chrome_options=options)
    return driver

...
```

# Conclusion/After Analysis

TODO: Write a conclusion