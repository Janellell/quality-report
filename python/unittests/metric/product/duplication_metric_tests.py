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

import unittest
from qualitylib import metric


class FakeSonar(object):
    ''' Provide for a fake Sonar object so that the unit test don't need 
        access to an actual Sonar instance. '''
    # pylint: disable=unused-argument
            
    @staticmethod
    def dashboard_url(*args):  
        ''' Return a fake dashboard url. '''
        return 'http://sonar'
           
    @staticmethod
    def duplicated_lines(*args):
        ''' Return the number of duplicated lines. '''
        return 15
    
    @staticmethod
    def lines(*args):
        ''' Return the number of lines. '''
        return 150
            
    
class FakeSubject(object):  # pylint: disable=too-few-public-methods
    ''' Provide for a fake subject. '''
       
    @staticmethod
    def sonar_id():
        ''' Return the Sonar id of the subject. '''
        return ''
              

class DuplicationTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the duplication metric. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self._metric = metric.Duplication(subject=FakeSubject(),  
                                          sonar=FakeSonar(), 
                                          wiki=None, history=None)
        
    def test_value(self):
        ''' Test that the value of the metric equals the percentage of 
            duplicated lines. '''
        self.assertEqual(10., self._metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Sonar=FakeSonar().dashboard_url()), 
                         self._metric.url())