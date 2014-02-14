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

from qualitylib import domain
from unittests.domain.measurement.fake import FakeWiki, FakeHistory, \
    FakeTasks, FakeSubject
import datetime
import unittest


class MetricUnderTest(domain.Metric):  
    # pylint: disable=too-many-public-methods, W0223
    ''' Override Metric to implement abstract methods that are needed for
        running the unit tests. '''
    def __init__(self, *args, **kwargs):
        self.date = None
        super(MetricUnderTest, self).__init__(*args, **kwargs)
        
    def value(self):
        return 0
    
    def _date(self):
        if self.date:
            return self.date
        else:   
            return super(MetricUnderTest, self)._date()  # pylint: disable=protected-access, line-too-long
    
    
class MetricTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    ''' Test case for the Metric domain class. '''
    
    def setUp(self):  # pylint: disable=C0103
        self.__subject = FakeSubject()
        self.__fake_tasks = FakeTasks()
        self.__metric = MetricUnderTest(self.__subject, wiki=FakeWiki(), 
                                        history=FakeHistory(), 
                                        tasks=self.__fake_tasks)
    
    def test_stable_id(self):
        ''' Test that the metric has a stable id. '''
        self.assertEqual('MetricUnderTestFakeSubject', 
                         self.__metric.stable_id())
        
    def test_stable_id_mutable_subject(self):
        ''' Test that the stable id doesn't include the subject if the 
            subject is a list. '''
        self.assertEqual('Metric', 
                         domain.Metric([], wiki=None, history=None).stable_id())
        
    def test_set_id_string(self):
        ''' Test that the id string can be changed. '''
        self.__metric.set_id_string('id string')
        self.assertEqual('id string', self.__metric.id_string())
        
    def test_default_status(self):
        ''' Test that the default status is green. '''
        self.assertEqual('green', self.__metric.status())
        
    def test_yellow_when_never_measured(self):
        ''' Test that the status is yellow when the metric has never been
            measured. '''
        self.__metric.old_age = datetime.timedelta(days=1)
        self.assertEqual('yellow', self.__metric.status())
        
    def test_yellow_when_old(self):
        ''' Test that the status is yellow when the last measurement was
            too long ago. '''
        self.__metric.old_age = datetime.timedelta(days=1)
        self.__metric.date = datetime.datetime.now() - \
                             datetime.timedelta(hours=25)
        self.assertEqual('yellow', self.__metric.status())

    def test_red_when_never_measured(self):
        ''' Test that the status is red when the metric has never been 
            measured. '''
        self.__metric.max_old_age = datetime.timedelta(days=1)
        self.assertEqual('red', self.__metric.status())
        
    def test_red_when_old(self):
        ''' Test that the status is red when the last measurement was too long
            ago. '''
        self.__metric.max_old_age = datetime.timedelta(days=1)
        self.__metric.date = datetime.datetime.now() - \
                             datetime.timedelta(hours=25)
        self.assertEqual('red', self.__metric.status())
        
    def test_perfect_status(self):
        ''' Test that the status is perfect when the value equals the perfect
            target. '''
        self.__metric.perfect_value = 0
        self.assertEqual('perfect', self.__metric.status())
        
    def test_default_report(self):
        ''' Test the default report. '''
        self.assertEqual('Subclass responsibility', self.__metric.report())
        
    def test_report_with_long_subject(self):
        ''' Test that the subject is abbreviated when long. '''
        self.assertEqual('Subclass responsibility', 
                         self.__metric.report(max_subject_length=1))
        
    def test_default_norm(self):
        ''' Test the default norm. '''
        self.assertEqual('Subclass responsibility', self.__metric.norm())

    def test_default_url(self):
        ''' Test that the metric has no default url. '''
        self.failIf(self.__metric.url())
        
    def test_default_url_label(self):
        ''' Test that the metric has no default url label. '''
        self.failIf(self.__metric.url_label())
        
    def test_default_tasks(self):
        ''' Test that the metric has no tasks by default. '''
        self.failIf(self.__metric.has_tasks())
        
    def test_recent_history(self):
        ''' Test that the metric has no history by default. '''
        self.failIf(self.__metric.recent_history())

    def test_default_y_axis_range(self):
        ''' Test that the default y axis range is 0-100. '''
        self.assertEqual((0, 100), self.__metric.y_axis_range())
        
    def test_y_axis_range(self):
        ''' Test that the y axis range depends on the history. '''
        FakeHistory.values = [1, 4, 5, 2]
        self.assertEqual((0, 5), self.__metric.y_axis_range())
        
    def test_y_axis_range_negatives(self):
        '''' Test that the y axis range is 0-100 when the maximum historic
             value is zero or lower. '''
        FakeHistory.values = [0]
        self.assertEqual((0, 100), self.__metric.y_axis_range())
        
    def test_default_target(self):
        ''' Test that the default target is a subclass responsibility. '''
        self.assertEqual('Subclass responsibility', self.__metric.target())

    def test_subject_target(self):
        ''' Test that the metric gets the target value from the subject if it 
            has one. '''
        # pylint: disable=attribute-defined-outside-init
        self.__subject.target = lambda subject: 'Subject specific target'
        self.assertEqual('Subject specific target', self.__metric.target())

    def test_default_low_target(self):
        ''' Test that the default low target is a subclass responsibility. '''
        self.assertEqual('Subclass responsibility', self.__metric.low_target())
        
    def test_subject_low_target(self):
        ''' Test that the metric gets the low target value from the subject if
            it has one. '''
        # pylint: disable=attribute-defined-outside-init
        self.__subject.low_target = lambda metric: 'Subject specific target'
        self.assertEqual('Subject specific target', self.__metric.low_target())

    def test_default_responsible_teams(self):
        ''' Test that the metric has no responsible teams by default. '''
        self.failIf(self.__metric.responsible_teams())

    def test_passed_responsible_teams(self):
        ''' Test that the metric can be initialized with responsible teams. '''
        self.assertEqual('Teams', MetricUnderTest(wiki=None, 
            history=None, responsible_teams='Teams').responsible_teams())
        
    def test_subject_responsible_teams(self):
        ''' Test that the responsible teams for the metric equal those of the
            subject if it has responsible teams. '''
        # pylint: disable=attribute-defined-outside-init
        subject = FakeSubject()
        subject.responsible_teams = lambda metric: 'Teams'
        self.assertEqual('Teams', MetricUnderTest(subject, wiki=None, 
                         history=None).responsible_teams())

    def test_default_comment(self):
        ''' Test that the metric has no comment by default. '''
        self.assertEqual('', self.__metric.comment())
        
    def test_default_comment_urls(self):
        ''' Test that the metric has no comment urls by default. '''
        self.assertEqual({}, self.__metric.comment_urls())
        
    def test_default_comment_url_label(self):
        ''' Test that the metric has no comment url label by default. '''
        self.failIf(self.__metric.comment_url_label())
        
    def test_comment_technical_debt(self):
        ''' Test that the metric gets the comment from the subject when the
            subject has a reduced technical debt target. '''
        # pylint: disable=attribute-defined-outside-init
        self.__subject.technical_debt_target = lambda metric: \
            domain.TechnicalDebtTarget(10, 'Comment')
        self.assertEqual('De op dit moment geaccepteerde technische schuld ' \
                         'is 10. Comment', self.__metric.comment())

    def test_comment_technical_debt_url(self):
        ''' Test that the metric has no comment url when the subject has a 
            reduced technical debt target because the reduced technical debt
            target is specified in the project definition. '''
        # pylint: disable=attribute-defined-outside-init
        self.__subject.technical_debt_target = lambda metric: \
            domain.TechnicalDebtTarget(10, 'Comment')
        self.failIf(self.__metric.comment_urls())
        
    def test_comment_from_wiki_url(self):
        ''' Test that the comment urls include a link to the Wiki if the Wiki
            has a comment on the metric. '''
        wiki = FakeWiki('Comment')
        metric = MetricUnderTest(self.__subject, wiki=wiki, 
                                 history=FakeHistory())
        self.assertEqual(dict(Wiki=wiki.comment_url()), metric.comment_urls())

    def test_numerical_value(self):
        ''' Test that the numerical value is the value by default. '''
        self.assertEqual(self.__metric.numerical_value(), 
                         self.__metric.value())
        
    def test_status_start_date(self):
        ''' Test that the metric gets the start date of the status from the 
            history. '''
        self.assertEqual(datetime.datetime(2013, 1, 1, 10, 0, 0), 
                         self.__metric.status_start_date())

    def test_product_version_type(self):
        ''' Test that the product version type is no_product when the metric
            subject is not a product. '''
        self.assertEqual('no_product', self.__metric.product_version_type())

    def test_no_task_urls_without_issue_manager(self):
        ''' Test that the metric has no task urls when there's no issue 
            manager. '''
        self.assertEqual({}, MetricUnderTest(self.__subject, wiki=FakeWiki(), 
                                             history=FakeHistory()).task_urls())

    def test_no_task_urls(self):
        ''' Test that the metric has no task urls by default. '''
        self.assertEqual({}, self.__metric.task_urls())
        
    def test_one_task_url(self):
        ''' Test that the metric has a task url when the issue manager reports
            so. '''
        self.__fake_tasks.task_urls = ['http://url1']
        self.assertEqual({'Correctieve actie': 'http://url1'}, 
                         self.__metric.task_urls())

    def test_two_task_urls(self):
        ''' Test that the metric has a task urls when the issue manager reports
            so. '''
        self.__fake_tasks.task_urls = ['http://url1', 'http://url2']
        self.assertEqual({'Correctieve actie': 'http://url1',
                          'Correctieve actie 1': 'http://url2'}, 
                         self.__metric.task_urls())
        
    def test_new_task_url(self):
        ''' Test that the metric task url include a new task link when the
            metric is below target and has no existing tasks. '''
        self.__metric.max_old_age = datetime.timedelta(days=1)
        self.__metric.date = datetime.datetime.now() - \
                             datetime.timedelta(hours=25)        
        self.assertEqual({'Maak taak': FakeTasks.new_task_url()}, 
                          self.__metric.task_urls())
        

class LowerIsBetterMetricUnderTest(domain.LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Override LowerIsBetterMetric to implement abstract methods that are 
        needed for running the unit tests. '''
    def value(self):
        return 0
    

class LowerIsBetterMetricTest(unittest.TestCase):  
    # pylint: disable=too-many-public-methods
    ''' Test case for the LowerIsBetterMetric domain class. '''
    
    def setUp(self):  # pylint: disable=C0103
        self.__subject = FakeSubject()
        self.__metric = LowerIsBetterMetricUnderTest(self.__subject, 
                                                     wiki=FakeWiki(), 
                                                     history=FakeHistory())

    def test_default_status(self):
        ''' Test that the default status is perfect. '''
        self.assertEqual('perfect', self.__metric.status())


class HigherIsBetterMetricUnderTest(domain.HigherIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Override HigherIsBetterMetric to implement abstract methods that are 
        needed for running the unit tests. '''
    def value(self):
        return 0
    

class HigherIsBetterMetricTest(unittest.TestCase):  
    # pylint: disable=too-many-public-methods
    ''' Test case for the HigherIsBetterMetric domain class. '''
    
    def setUp(self):  # pylint: disable=C0103
        self.__subject = FakeSubject()
        self.__metric = HigherIsBetterMetricUnderTest(self.__subject, 
                                                      wiki=FakeWiki(), 
                                                      history=FakeHistory())

    def test_default_status(self):
        ''' Test that the default status is red. '''
        self.assertEqual('red', self.__metric.status())
        
    def test_technical_debt(self):
        ''' Test that the status is grey when the current value is accepted
            technical debt. '''
        # pylint: disable=attribute-defined-outside-init
        self.__subject.technical_debt_target = lambda metric: \
            domain.TechnicalDebtTarget(0, 'Comment')
        self.assertEqual('grey', self.__metric.status())


class LowerPercentageIsBetterMetricUnderTest( \
    domain.LowerPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Override LowerPercentageIsBetterMetric to implement abstract methods 
        that are needed for running the unit tests. '''
    low_target_value = 20
    target_value = 10
    numerator = 0
    denominator = 0
    
    def _numerator(self):
        return self.numerator
    
    def _denominator(self):
        return self.denominator


class PercentageMetricTestCase(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Test case for percentage metrics. '''
        
    def setUp(self):  # pylint: disable=invalid-name
        self.__subject = FakeSubject()
        self._metric = self.metric_under_test_class()(self.__subject, 
            wiki=FakeWiki(), history=FakeHistory())
        
    @staticmethod
    def metric_under_test_class():
        ''' Return the metric class to be tested. '''
        raise NotImplementedError  # pragma: no cover
        
    def set_metric_value(self, numerator, denominator):
        ''' Set the metric value by means of the numerator and denominator. '''
        # pylint: disable=attribute-defined-outside-init
        self._metric.numerator = numerator
        self._metric.denominator = denominator
        
        
class LowerPercentageIsBetterMetricTest(PercentageMetricTestCase):  
    # pylint: disable=too-many-public-methods
    ''' Test case for the LowerPercentageIsBetterMetric domain class. '''
    
    @staticmethod
    def metric_under_test_class():
        return LowerPercentageIsBetterMetricUnderTest
    
    def test_perfect_status(self):
        ''' Test that the default status is perfect when the score is 100%. '''
        self.assertEqual('perfect', self._metric.status())

    def test_green_status(self):
        ''' Test that the default status is green when the score is below the 
            low target. '''
        self.set_metric_value(1, 100)
        self.assertEqual('green', self._metric.status())

    def test_yellow_status(self):
        ''' Test that the  status is yellow when the score is between the low
            target and target. '''
        self.set_metric_value(20, 100)
        self.assertEqual('yellow', self._metric.status())

    def test_red_status(self):
        ''' Test that the status is red when the score is higher than the low
            target. '''
        self.set_metric_value(40, 100)
        self.assertEqual('red', self._metric.status())
                
    def test_y_axis_range(self):
        ''' Test that the y axis range is 0-100. '''
        self.assertEqual((0, 100), self._metric.y_axis_range())
        
    def test_default_report(self):
        ''' Test that the default report. '''
        self.set_metric_value(0, 0)
        self.assertEqual('Subclass responsibility', self._metric.report())
        

class HigherPercentageIsBetterMetricUnderTest( \
    domain.HigherPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Override HigherPercentageIsBetterMetric to implement abstract methods 
        that are needed for running the unit tests. '''
    low_target_value = 80
    target_value = 90
    numerator = 0
    denominator = 0
    
    def _numerator(self):
        return self.numerator
    
    def _denominator(self):
        return self.denominator
    

class HigherPercentageIsBetterMetricTest(PercentageMetricTestCase):  
    # pylint: disable=too-many-public-methods
    ''' Test case for the HigherPercentageIsBetterMetric domain class. '''
    
    @staticmethod
    def metric_under_test_class():
        return HigherPercentageIsBetterMetricUnderTest
    
    def test_red_status(self):
        ''' Test that the status is red when the percentage is lower than the
            low target. '''
        self.set_metric_value(0, 5)
        self.assertEqual('red', self._metric.status())
        
    def test_yellow_status(self):
        ''' Test that the status is yellow when the percentage is lower than
            the target. '''
        self.set_metric_value(85, 100)
        self.assertEqual('yellow', self._metric.status())
        
    def test_green_status(self):
        ''' Test that the status is green when the metric value is higher than
            the target value. '''
        self.set_metric_value(95, 100)
        self.assertEqual('green', self._metric.status())

    def test_perfect_status(self):
        ''' Test that the status is perfect when the metric value is 100%. '''
        self.set_metric_value(100, 100)
        self.assertEqual('perfect', self._metric.status())

    def test_y_axis_range(self):
        ''' Test that the y axis range is 0-100. '''
        self.assertEqual((0, 100), self._metric.y_axis_range())
        
    def test_default_report(self):
        ''' Test that the default report. '''
        self.set_metric_value(0, 5)
        self.assertEqual('Subclass responsibility', self._metric.report())