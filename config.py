# The MIT License (MIT) # Copyright (c) 2014-2017 University of Bristol
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import simplejson as json
import os
from utils import Printable


class HyperStreamConfig(Printable):
    def __init__(self):
        self.mongo = None

        try:
            with open('hyperstream_config.json', 'r') as f:
                logging.info('Reading ' + os.path.abspath(f.name))
                config = json.load(f)
                self.mongo = config['mongo']
                self.tool_path = config['tool_path']

        except (OSError, IOError, TypeError) as e:
            # raise
            logging.error("Configuration error: " + str(e))

        try:
            with open('meta_data.json', 'r') as f:
                logging.info('Reading ' + os.path.abspath(f.name))
                config = json.load(f)
                self.meta_data_lists = config['meta_data_lists']
                self.meta_data = config['meta_data']

        except (OSError, IOError, TypeError) as e:
            # raise
            logging.error("Configuration error: " + str(e))
