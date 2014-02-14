'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib import utils
from qualitylib.metric_source import beautifulsoup
import datetime
import re
import time


class PerformanceReport(beautifulsoup.BeautifulSoupOpener):
    ''' Class representing the Performance report. '''

    COLUMN_90_PERC = 10
    
    def __init__(self, report_folder_url):
        super(PerformanceReport, self).__init__()
        self.__report_folder_url = report_folder_url
        
    def url(self):
        ''' Return the url for the folder where the reports are stored. '''
        return self.__report_folder_url
        
    def queries(self, product, version):
        ''' Return the number of performance queries. '''
        return len(self.__query_rows(product, version))
    
    def queries_violating_max_responsetime(self, product, version):
        ''' Return the number of performance queries that violate the maximum
            response time. '''
        return self.__queries_violating_response_time(product, version, 'red')

    def queries_violating_wished_reponsetime(self, product, version):
        ''' Return the number of performance queries that violate the maximum
            response time we'd like to meet. '''
        return self.__queries_violating_response_time(product, version,
                                                      'yellow')

    def __queries_violating_response_time(self, product, version, color):
        ''' Return the number of queries that are violating either the maximum
            or the desired response time. '''
        return len([row for row in self.__query_rows(product, version) \
                    if row('td')[self.COLUMN_90_PERC]['class'] == color])
    
    @utils.memoized    
    def __query_rows(self, product, version):
        ''' Return the queries for the specified product and version. '''
        rows = []
        product_query_id = product[0]
        urls = self.urls(product, version)
        for url in urls:
            soup = self.soup(url)
            for row in soup('tr'):
                query_names = row('td', attrs={'class': 'name'})
                if not query_names:
                    continue  # Header row
                query_name = query_names[0].string
                if not re.match(product_query_id, query_name):
                    continue  # Not our product
                if not row('td')[self.COLUMN_90_PERC].has_key('class'):
                    continue  # No color in 90 perc column
                rows.append(row)
        return rows

    @utils.memoized
    def date(self, product, version):
        ''' Return the date when performance was last measured. '''
        urls = self.urls(product, version)
        if urls:
            soup = self.soup(list(urls)[0])  # Any url is fine
            date_text = soup('h2')[0].string.split(' - ')[1].split(' ')[0]
            return self.__parse_date(date_text)
        else:
            return datetime.datetime.min

    def exists(self, product, version):
        ''' Return whether a performance report exists for the specified
            product and version. '''
        return bool(self.urls(product, version))

    @utils.memoized
    def urls(self, product, version):
        ''' Return the url(s) of the performance report for the specified
            product and version. '''
        soup = self.soup(self.__report_folder_url)
        urls = {0: set()}  # {test_run_number: set(of urls)}
        for list_item in soup('li'):
            filename = list_item('a')[0].string
            if not filename.endswith('.html'):
                continue
            url = self.__report_folder_url + filename
            if self.__report_covers_product_and_version(url, product, version):
                urls.setdefault(self.__test_run_number(filename), 
                                set()).add(url)
        return urls[max(urls.keys())]  # Return the latest test run

    @utils.memoized
    def __report_covers_product_and_version(self, url, product, version):
        ''' Return whether the performance report covers the specified product
            and version. '''
        product_query_id, product_long_id = product
        soup = self.soup(url)
        if not self.__report_contains_queries(soup, product_query_id):
            return False
        for table in soup('table')[:2]:  # First two tables contain products
            for cell in table('td'):
                try:
                    covered_product, covered_version = cell.string.split('-ear')
                except ValueError:
                    return False
                covered_version = covered_version.strip('-')
                if covered_product == product_long_id and \
                   version in (covered_version, ''):
                    return True
        return False
    
    @staticmethod
    def __report_contains_queries(soup, product_query_id):
        ''' Return whether the performance report contains queries with the
            specified query id. '''
        for row in soup('tr'):
            query_names = row('td', attrs={'class': 'name'})
            if not query_names:
                continue  # Header row
            query_name = query_names[0].string
            if re.match(product_query_id, query_name):
                return True
        return False
    
    @staticmethod
    def __test_run_number(filename):
        ''' Return the test run number as contained in the filename. '''
        number_part = filename.split('_')[2]
        return int(re.search('[0-9]+', number_part).group(0))
        
    @staticmethod
    def __parse_date(date_text):
        ''' Return a parsed version of the date text. '''
        year, month, day = time.strptime(date_text, '%Y-%m-%d')[:3]
        return datetime.datetime(year, month, day)