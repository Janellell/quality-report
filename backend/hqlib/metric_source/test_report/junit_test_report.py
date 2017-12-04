"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import datetime
import logging
import re
import xml.etree.cElementTree
from xml.etree.ElementTree import Element
from typing import List, Sequence

from ..abstract import test_report
from ..url_opener import UrlOpener
from ... import utils
from ...typing import DateTime, TimeDelta


class JunitTestReport(test_report.TestReport):
    """ Class representing Junit test reports. """

    metric_source_name = 'Junit test report'

    def metric_source_urls(self, *report_urls: str) -> List[str]:
        return [re.sub(r'junit/junit\.xml$', 'html/htmlReport.html', report_url) for report_url in report_urls]

    def _passed_tests(self, metric_source_id: str) -> int:
        """ Return the number of passed tests. """
        failed = self._failed_tests(metric_source_id)
        skipped = self._skipped_tests(metric_source_id)
        total = self.__test_count(metric_source_id, 'tests')
        return -1 if -1 in (failed, skipped, total) else total - (skipped + failed)

    def _failed_tests(self, metric_source_id: str) -> int:
        """ Return the number of failed tests. """
        failed = self.__failure_count(metric_source_id)
        errors = self.__test_count(metric_source_id, 'errors')
        return -1 if -1 in (failed, errors) else failed + errors

    def _skipped_tests(self, metric_source_id: str) -> int:
        """ Return the number of skipped tests. """
        skipped = self.__test_count(metric_source_id, 'skipped')
        disabled = self.__test_count(metric_source_id, 'disabled')
        return -1 if -1 in (skipped, disabled) else skipped + disabled

    def _report_datetime(self, metric_source_id: str) -> DateTime:
        """ Return the date and time of the report. """
        timestamps = self.__time_stamps(metric_source_id)
        if timestamps:
            return min(timestamps)
        else:
            logging.error("Couldn't find timestamps in test suites in: %s", report_url)
            return datetime.datetime.min

    def duration(self, *metric_source_ids: str) -> TimeDelta:
        """ Return the duration of the report. """
        timestamps = self.__time_stamps(*metric_source_ids)
        if timestamps:
            return max(timestamps) - min(timestamps)
        else:
            logging.error("Couldn't find test suites in: %s", report_urls)
            return datetime.timedelta.max

    def __time_stamps(self, *metric_source_ids: str) -> Sequence[DateTime]:
        """ Return the time stamps in the suites. """
        timestamps = []
        for report_url in metric_source_ids:
            for test_suite in self.__test_suites(report_url):
                timestamp_str, time_str = test_suite.get('timestamp'), test_suite.get('time')
                if None in (timestamp_str, time_str):
                    return []  # One or both of the needed attributes are missing
                timestamp = utils.parse_iso_datetime(timestamp_str + 'Z')
                timedelta = datetime.timedelta(seconds=float(time_str))
                timestamps.extend([timestamp, timestamp + timedelta])
        return timestamps

    def __test_count(self, report_url: str, result_type: str) -> int:
        """ Return the number of tests with the specified result in the test report. """
        test_suites = self.__test_suites(report_url)
        if test_suites:
            return sum(int(test_suite.get(result_type, 0)) for test_suite in test_suites)
        else:
            logging.error("Couldn't find test suites in: %s", report_url)
            return -1

    def __failure_count(self, report_url: str) -> int:
        """ Return the number of test cases that have failures (failed assertions). """
        try:
            root = self.__element_tree(report_url)
        except UrlOpener.url_open_exceptions:
            return -1
        except xml.etree.cElementTree.ParseError:
            return -1
        return len(root.findall('.//testcase[failure]'))

    def __test_suites(self, report_url: str) -> Sequence[Element]:
        """ Return the test suites in the report. """
        try:
            root = self.__element_tree(report_url)
        except UrlOpener.url_open_exceptions:
            return []
        except xml.etree.cElementTree.ParseError:
            return []
        return [root] if root.tag == 'testsuite' else root.findall('testsuite')

    def __element_tree(self, report_url: str) -> Element:
        """ Return the report contents as ElementTree. """
        contents = self._url_read(report_url)
        try:
            return xml.etree.cElementTree.fromstring(contents)
        except xml.etree.cElementTree.ParseError as reason:
            logging.error("Couldn't parse report at %s: %s", report_url, reason)
            raise
