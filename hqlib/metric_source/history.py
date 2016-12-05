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

import datetime
import io
import logging

from .. import utils, domain


class History(domain.MetricSource):
    """ Class representing the history file. """
    metric_source_name = 'Measurement history file'

    def __init__(self, history_filename, recent_history=250, file_=file):
        self.__history_filename = history_filename
        self.__recent_history = recent_history
        self.__file = file_
        super(History, self).__init__(url=history_filename)

    def recent_history(self, *metric_ids):
        """ Retrieve the recent history for the metric_ids. """
        values = []
        for measurement in self.__historic_values():
            for metric_id in metric_ids:
                if metric_id in measurement:
                    values.append(measurement[metric_id])
                    break  # inner loop
        return values

    def complete_history(self):
        """ Return the complete history. """
        return self.__historic_values(recent_only=False)

    def status_start_date(self, metric_id, current_status, now=datetime.datetime.now):
        """ Return the start date of the current status of the metric. """
        last_status, date = self.__last_status(metric_id)
        return date if last_status == current_status else now()

    def __last_status(self, metric_id):
        """ Return the last recorded status of the metric and the date that the metric first had that status. """
        try:
            last_measurement = self.__eval_history()[-1][metric_id]
        except (IndexError, KeyError):
            last_measurement = None
        if isinstance(last_measurement, tuple) and len(last_measurement) >= 3:
            last_status = last_measurement[1]
            time_stamp = last_measurement[2]
            time_stamp_format = '%Y-%m-%d %H:%M:%S'
            if '.' in time_stamp:
                time_stamp_format += '.%f'
            date = datetime.datetime.strptime(time_stamp, time_stamp_format)
            return last_status, date
        else:
            return '', datetime.datetime.min

    @utils.memoized
    def __historic_values(self, recent_only=True):
        """ Return only the historic values from the history file. """
        measurements = self.__eval_history(recent_only)
        value_only_measurements = []
        for measurement in measurements:
            values_only_measurement = dict()
            for metric_id, measurement_data in measurement.items():
                if isinstance(measurement_data, tuple):
                    value = measurement_data[0]
                else:
                    value = measurement_data
                values_only_measurement[metric_id] = value
            value_only_measurements.append(values_only_measurement)
        return value_only_measurements

    @utils.memoized
    def __eval_history(self, recent_only=True):
        """ Load and eval measurements from the history file. """
        return [eval(line) for line in self.__load_history(recent_only)]

    @utils.memoized
    def __load_history(self, recent_only=True):
        """ Load measurements from the history file. """
        try:
            history_file = self.__file(self.__history_filename)
        except IOError:
            logging.warning('Could not open %s', self.__history_filename)
            history_file = io.StringIO()  # Fake an empty file
        lines = history_file.readlines()
        history_file.close()
        if recent_only:
            lines = lines[-self.__recent_history:]
        logging.info('Read %d lines from %s', len(lines), self.__history_filename)
        return [line.strip() for line in lines if line.strip()]
