# Speeding Up Web Scraping with Parallel Processing

## Introduction

TODO: add basic intro

After completing this tutorial you should be able to:

1. Scrape and crawl websites with Selenium and Beautiful Soup
1. Use command line arguments to test your python code
1. Setup Multiprocessing for a web scraper
1. Configure headless mode for Chromedriver with Selenium

## Project Setup

From the command line run the following commands:

```sh
$ git clone git@github.com:calebpollman/web-scraping-parallel-processing.git
$ pip install requirements.txt
```

Install `chromedriver` globally. You can find instructions [here](https://sites.google.com/a/chromium.org/chromedriver/).

## Basic Project Overview

The script traverses and scrapes the first 20 pages of [Hacker News](https://news.ycombinator.com/) for information about the current articles listed using [Selenium](http://www.seleniumhq.org/projects/webdriver/) to automate interaction with the site and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to parse the HTML.

### Chrome Instance

First, the browser is initialized via `get_driver()`:

```python
def get_driver():
    # initialize driver
    driver = webdriver.Chrome()
    return driver
```

From there, a `while` loop is configured to control the remainder of the program flow:

[REFACTOR]

```python
while page_number <= 20:
    if connect_to_base(browser, page_number):
        sleep(2)
        html_source = browser.page_source
        output = parse_html(html_source)
        write_to_file(output, filename)
        page_number = page_number + 1
    else:
        print('Error connecting to Hacker News')
```

The browser instance along with a page number is passed to  `connect_to_base()`, which attempts to connect to Hacker News, then uses Selenium's explicit wait functionality to ensure the element with *id='hnmain'* has loaded before continuing:

```python
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

After the waiting period, the browser grabs the HTML source, which is the passed along to `parse_html()`:

[REFACTOR]

```python
html_source = browser.page_source
output = parse_html(html_source)
```

`parse_html()` then uses Beautiful Soup to parse the HTML, generating a list of dicts with the appropriate data:

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
def write_to_file(output_list, filename):
    for row in output_list:
        with open(filename, 'a') as csvfile:
            fieldnames = ['id', 'rank', 'score', 'title']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(row)
```

Finally, the page number is incremented and the process start over again:

[REFACTOR]

```python
page_number = page_number + 1
```

> Want to test this out? Grab the full script [here](bot.py).

Got it? Great! Let's add some basic testing.

# Setup Basic Testing

To test the parsing functionality without initiating the browser and, thus, making repeated get requests to Hacker News, you can download the page html and parse it locally. This can help avoid scenarios where you may get your ip blocked for making too many requests too quickly while writing and testing your parsing function, as well as saving you time by not needing to fire up a browser every time you run the script.

Create a `test` directory:

```sh
$ mkdir test
```

Download the HTML source manually to that directory and rename the file to `test.html`:

![hn](/assets/screenshot.png "Save Screenshot")

Import the `sys` package near the top of file in *bot.py*:

```python
import sys
import csv
import datetime
from time import sleep, time
```

Then, update the main block to check for the `--test` command line argument:

```python
if __name__ == '__main__':
    start_time = time()
    browser = get_driver()
    # check for command line args
    try:
        test_flag = sys.argv[1]
    except Exception as ex:
        test_flag = 'null'
    # if test mode
    if sys.argv[1] == '--test':
        print('TEST MODE')
        html = open('test/test.html')
        output_list = parse_html(html)
        write_to_file(output_list, filename)
    else:
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
            page_number = page_number + 1
        else:
            print('Error connecting to Hacker News')
    browser.quit()
    end_time = time()
    print('Elapsed run time: {0} seconds'.format(end_time - start_time))
```

Run `python bot.py --test` from the command line and make sure you don't have any errors before moving on to the next section.

> Grab the code [here](bot-test.py)

## Configure Multiprocessing

In order to setup Multiprocessing we will go through the following steps. At the end we will add a flag to run Chrome headless to increase processing speed.

Move the call to ```get_driver()``` inside the while loop and add ```browser.quit()``` to each instance:

```python
...

if __name__ == '__main__':
    start_time = time()
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = 'output_{0}.csv'.format(output_timestamp)
    try:
        test_flag = sys.argv[1]
    except:
        test_flag = 'null'
    if sys.argv[1] == '--test':
        html = open('test/test.html')
        output_list = parse_html(html)
        write_to_file(output_list, filename)
    else:
        page_number = 1
        while page_number <= 20:
            browser = get_driver()
            if connect_to_base(browser, page_number):
                sleep(2)
                html = browser.page_source
                output_list = parse_html(html)
                write_to_file(output_list, filename)
                page_number = page_number + 1
                browser.quit()
            else:
                print('Error connecting to hackernews')
                browser.quit()

...
```

Abstract functions out of ```__main___``` by creating ```run_process(page_number)```:

```python
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
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = 'output_{0}.csv'.format(output_timestamp)
    try:
        test_flag = sys.argv[1]
    except:
        test_flag = 'null'
    if test_flag == '--test':
        html = open('test/test.html')
        output_list = parse_html(html)
        write_to_file(output_list, filename)
    else:
        page_number = 1
        while page_number <= 20:
            run_process(page_number, filename)
            page_number = page_number + 1

...
```

Add ```Pool``` and  ```cpu_count``` modules from ```multiprocessing``` package and ```repeat``` module from ```itertools``` package to imports near top of *bot.py*:

```python
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
...

if __name__ == '__main__':
    start_time = time()
    output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = 'output_{0}.csv'.format(output_timestamp)
    try:
        test_flag = sys.argv[1]
    except:
        test_flag = 'null'
    if test_flag == '--test':
        html = open('test/test.html')
        output_list = parse_html(html)
        write_to_file(output_list, filename)
    else:
        with Pool(cpu_count()-1) as p:
            p.starmap(run_process, zip(range(1, 21), repeat(filename)))
        p.close()
        p.join()

...
```


# Configure Headless Chromedriver

We can go headless with Chrome to speed up processing by adding ```ChromeOptions()``` with the ```--headless``` flag to the driver:

```python
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