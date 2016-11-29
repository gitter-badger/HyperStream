"""
The MIT License (MIT)
Copyright (c) 2014-2017 University of Bristol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""

from hyperstream import TimeInterval
from hyperstream.stream import StreamInstance
from hyperstream.tool import Tool, check_input_stream_count
from hyperstream.utils import get_timedelta


class AligningWindow(Tool):
    def __init__(self, lower=-1.0, upper=0.0):
        """
        Simple clock ticker tool
        :param lower: The lower end of the sliding execute
        :param upper: The upper end of the sliding execute
        """
        super(AligningWindow, self).__init__(lower=lower, upper=upper)

        # Validate lower and upper
        self._lower = get_timedelta(lower)
        self._upper = get_timedelta(upper)

    @check_input_stream_count(1)
    def _execute(self, sources, alignment_stream, interval):
        for (time, _) in sources[0].window(interval, force_calculation=True):
            yield StreamInstance(
                time, TimeInterval(time + self._lower, time + self._upper))

