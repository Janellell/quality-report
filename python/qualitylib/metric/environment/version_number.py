"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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
from __future__ import absolute_import

from distutils.version import LooseVersion

from ..quality_attributes import ENVIRONMENT_QUALITY
from ...domain import HigherIsBetterMetric
from ... import metric_source, utils


class SonarVersion(HigherIsBetterMetric):
    name = 'Sonar versie'
    norm_template = 'Sonar heeft minimaal versie {target}, lager dan versie {low_target} is rood.'
    template = 'Sonar is versie {value}.'
    target_value = LooseVersion('4.5.6')
    perfect_value = LooseVersion('999.999.999')
    low_target_value = LooseVersion('4.5.4')
    quality_attribute = ENVIRONMENT_QUALITY
    metric_source_classes = (metric_source.Sonar,)

    def __init__(self, *args, **kwargs):
        super(SonarVersion, self).__init__(*args, **kwargs)
        self._sonar = self._project.metric_source(metric_source.Sonar)

    def numerical_value(self):
        return utils.version_number_to_numerical(self.value().version)

    def value(self):
        return LooseVersion(self._sonar.version_number())

    def url(self):
        return {'Sonar': self._sonar.url()}

    def _missing(self):
        return False  # Not supported yet.


class SonarPluginVersion(HigherIsBetterMetric):
    """ Measure the version number of a Sonar plugin. """
    name = 'Sonar plugin versie'
    plugin_key = 'Subclass responsibility'
    plugin_name = 'Subclass responsibility'
    norm_template = 'Sonar plugin {plugin} heeft minimaal versie {target}, lager dan versie {low_target} is rood.'
    template = 'Sonar plugin {plugin} is versie {value}.'
    target_value = LooseVersion('1.0')
    perfect_value = LooseVersion('999.999.999')
    low_target_value = LooseVersion('0.1')
    quality_attribute = ENVIRONMENT_QUALITY
    metric_source_classes = (metric_source.Sonar,)

    def __init__(self, *args, **kwargs):
        super(SonarPluginVersion, self).__init__(*args, **kwargs)
        self._sonar = self._project.metric_source(metric_source.Sonar)

    def numerical_value(self):
        return utils.version_number_to_numerical(self.value().version)

    def value(self):
        return LooseVersion(self._sonar.plugin_version(self.plugin_key))

    def url(self):
        return {'Sonar': self._sonar.url()}

    def _parameters(self):
        parameters = super(SonarPluginVersion, self)._parameters()
        parameters['plugin'] = self.plugin_name
        return parameters

    def _missing(self):
        return False  # Not supported yet.


class SonarPluginVersionJava(SonarPluginVersion):
    """ Measure the version number of the Java Sonar plugin. """
    name = 'Sonar Java plugin version'
    plugin_key = 'java'
    plugin_name = 'Java'