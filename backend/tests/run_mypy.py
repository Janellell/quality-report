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

# Run the mypy static type checker.

import pathlib
from mypy import api


def run_mypy():
    """ Create report folder and run mypy. """
    backend_dir = pathlib.Path(__file__).parent.parent
    hqlib_dir = backend_dir / "hqlib"
    report_dir = backend_dir.parent / "build" / "mypy_report"
    report_dir.mkdir(parents=True, exist_ok=True)

    result = api.run([str(hqlib_dir), "--html-report", str(report_dir)])

    if result[0]:
        print("\nType checking report:\n")
        print(result[0])  # stdout

    if result[1]:
        print("\nError report:\n")
        print(result[1])  # stderr

    print("\nExit status:", result[2])


if __name__ == "__main__":  # pragma: no branch
    run_mypy()
