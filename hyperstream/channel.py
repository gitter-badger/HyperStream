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
from utils import Printable
from channels import ToolChannel, SphereChannel, MemoryChannel, DatabaseChannel
from datetime import datetime
import pytz


class ChannelCollection(Printable):
    def __init__(self, tool_path):
        self.tool_channel = ToolChannel(1, tool_path, up_to_timestamp=datetime.utcnow().replace(tzinfo=pytz.utc))
        self.sphere_channel = SphereChannel(2)
        self.memory_channel = MemoryChannel(3)
        self.database_channel = DatabaseChannel(4)

    def __getitem__(self, item):
        if item in self.memory_channel:
            return self.memory_channel[item]
        if item in self.database_channel:
            return self.database_channel[item]
        # if item in self.tool_channel:
        #     return self.tool_channel[item]
        if item in self.sphere_channel:
            return self.sphere_channel[item]
        raise KeyError("{} not found in channels".format(item))