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

import unittest
from unittest.mock import Mock

from hqlib.formatting import JSONFormatter, MetricsFormatter, MetaMetricsHistoryFormatter, MetaDataJSONFormatter
from hqlib import domain, metric_source, VERSION
from . import fake_report


class JSONFormatterTest(unittest.TestCase):
    """ Unit test for the dot report formatter class. """
    def setUp(self):
        self.__formatter = JSONFormatter()

    def test_process(self):
        """ Test that the report is processed correctly. """
        self.assertEqual(
            '{"date": "2012-01-01 12:00:00", "metric_id": ("15", "red", "2012-01-01 12:00:00"), '
            '"metric_id": ("15", "red", "2012-01-01 12:00:00"), }\n',
            self.__formatter.process(fake_report.Report()))

    def test_prefix_no_products(self):
        """ Test that the prefix is correct. """
        self.assertEqual('{"date": "2012-01-01 12:00:00", ', self.__formatter.prefix(fake_report.Report()))

    def test_prefix_product(self):
        """ Test that the prefix contains the version of the products that not have been released
            (i.e. the version of the trunk). """
        report = fake_report.Report([domain.Product()])
        self.assertEqual('{"Product-version": "2", "date": "2012-01-01 12:00:00", ', self.__formatter.prefix(report))

    def test_formatting_error(self):
        """ Test that formatting a non-numerical value raises a type error. """

        class BuggyMetric(object):  # pylint: disable=too-few-public-methods
            """ A metric that returns a dummy string for every method called. """
            def __getattr__(self, attr):
                return lambda *args: 'dummy'

        self.assertRaises(ValueError, self.__formatter.metric, BuggyMetric())


class MetaMetricsHistoryFormatterTest(unittest.TestCase):
    """ Unit test for the meta metrics history to JSON formatter. """
    def setUp(self):
        self.__formatter = MetaMetricsHistoryFormatter()

    def test_process(self):
        """ Test that the report is processed correctly. """
        self.assertEqual('[[[2012, 3, 5, 16, 16, 58], [0, 1, 1, 0, 0, 0, 0]]]\n',
                         self.__formatter.process(fake_report.Report()))


class MetricsFormatterTest(unittest.TestCase):
    """ Unit test for the metrics to JSON formatter. """

    def setUp(self):
        self.__formatter = MetricsFormatter()

    def test_process(self):
        """ Test that the report is processed correctly. """
        self.maxDiff = None
        self.assertEqual('''{{"report_date": [2012, 1, 1, 12, 0, 0], "report_title": "Report title", "hq_version": \
"{0}", "sections": [{{"id": "id", "title": "Section title", "subtitle": "Section subtitle", "latest_change_date": \
"2017-01-01 00:00:00"}}], "dashboard": \
{{"headers": [{{"header": "ME", "colspan": 1}}], "rows": [[{{"section_id": "ID", "section_title": "Section title", \
"bgcolor": "lightsteelblue", "colspan": 1, "rowspan": 1}}]]}}, "metrics": [{{"id_value": "id_string-01", "id_format": \
"id_string-1", "stable_metric_id": "metric_id", "name": "Metric Name", "unit": "unit of measure", \
"section": "id_string", "status": "red", "status_value": "0", "status_start_date": [2012, 1, 1, 12, 0, 0], \
"measurement": "report [<a href='http://url' target='_blank'>anchor</a>]", "norm": "norm", \
"comment": "Comment with \\\\backslash", "metric_class": "Metric", \
"extra_info": {{"headers": {{"col1": "C1", "col2": "C2"}}, "title": "Fake title", "data": [{{"col1": "yes", "col2": \
{{"href": "this", "text": "that"}}}}]}}}}, {{"id_value": "id_string-01", "id_format": "id_string-1", \
"stable_metric_id": "metric_id", "name": "Metric Name", "unit": "unit of measure", "section": \
"id_string", "status": "red", "status_value": "0", "status_start_date": [2012, 1, 1, 12, 0, 0], \
"measurement": "report [<a href='http://url' target='_blank'>anchor</a>]", "norm": "norm", \
"comment": "Comment with \\\\backslash", "metric_class": "Metric", "extra_info": {{"headers": \
{{"col1": "C1", "col2": "C2"}}, "title": "Fake title", "data": [{{"col1": "yes", "col2": \
{{"href": "this", "text": "that"}}}}]}}}}]}}\n'''.format(VERSION), self.__formatter.process(fake_report.Report()))


class MetaDataFormatterTest(unittest.TestCase):
    """ Unit tests for the meta data JSON formatter. """

    def test_process(self):
        """ Test that the report is processed correctly. """
        domain_object_instance = Mock()
        domain_object_instance.metric_sources.return_value = [metric_source.Git(url="domain_object_git")]
        project = Mock()
        project.domain_object_instances.return_value = [domain_object_instance]
        project.metric_sources.return_value = [metric_source.Git(url="project_git")]
        report = Mock()
        report.included_domain_object_classes.return_value = []
        report.included_metric_source_classes.return_value = [metric_source.Git]
        report.included_metric_classes.return_value = []
        report.domain_object_classes.return_value = [domain.Document]
        report.requirement_classes.return_value = []
        report.metric_classes.return_value = []
        report.metric_source_classes.return_value = [metric_source.Git]
        report.project.return_value = project
        self.assertEqual(
            '{"domain_objects": [{"included": false, "name": "Document", "id": "Document", "default_requirements": '
            '["Track document age"], '
            '"optional_requirements": ["Track the last security test date"]}], '
            '"requirements": [], '
            '"metrics": [], '
            '"metric_sources": [{"included": true, "name": "Git", "id": "Git", "urls": ["domain_object_git/", '
            '"project_git/"]}]}\n',
            MetaDataJSONFormatter().process(report))

