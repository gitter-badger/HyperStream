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
from datetime import datetime, timedelta

from hyperstream import ChannelManager, HyperStreamConfig, StreamId, Workflow, PlateManager, WorkflowManager, Client
from hyperstream.utils import UTC
from hyperstream.itertools2 import online_average, count as online_count
from sphere_connector_package.sphere_connector import SphereLogger


if __name__ == '__main__':
    # TODO: hyperstream needs it's own logger (can be a clone of this one)
    sphere_logger = SphereLogger(path='/tmp', filename='sphere_connector', loglevel=logging.DEBUG)

    hyperstream_config = HyperStreamConfig()
    client = Client(hyperstream_config.mongo)

    # Define some managers
    channels = ChannelManager(hyperstream_config.tool_path)
    plates = PlateManager(hyperstream_config.meta_data).plates
    workflows = WorkflowManager(channels=channels, plates=plates)

    # Various constants
    t1 = datetime(2016, 4, 28, 20, 0, 0, 0, UTC)
    t2 = t1 + timedelta(minutes=5)
    second = timedelta(seconds=1)
    minute = timedelta(minutes=1)
    hour = timedelta(hours=1)

    # Various channels
    M = channels.memory
    S = channels.sphere
    T = channels.tools
    D = channels.mongo
    
    # TODO: We could make the __getitem__ accept str and do the following, but for now it only accepts StringId
    environmental = StreamId(name='environmental', meta_data={'house': '1'})
    clock = StreamId('clock')
    aggregate = StreamId('aggregate')
    every30s = StreamId('every30s')
    motion_kitchen_windowed = StreamId('motion_kitchen_windowed')
    env_kitchen_30_s_window = StreamId('env_kitchen_30_s_window')
    m_kitchen_30_s_window = StreamId('m_kitchen_30_s_window')
    average = StreamId('averager', meta_data={'house': '1'})
    count = StreamId('counter')
    # sum_ = StreamId('sum')
    sphere = StreamId('sphere')
    component = StreamId('component')

    # Create a simple workflow for querying
    w = Workflow(
        channels=channels,
        plates=plates,
        workflow_id="simple_query_workflow",
        name="Simple query workflow",
        owner="TD",
        description="Just a test of creating workflows")

    # Create some streams (nodes)
    node = w.create_node(stream_name="environmental", plate_ids=["H1"]).window((t1, t1 + 1 * minute))

    # Check the values
    assert(node.streams[0].values()[:1] ==
           [{u'electricity-04063': 0.0, 'noise': None, 'door': None, 'uid': u'04063', 'electricity': None,
             'light': None, 'motion': None, 'dust': None, 'cold-water': None, 'humidity': None, 'hot-water': None,
             'temperature': None}])

    # More complex workflow
    w = Workflow(
        channels=channels,
        plates=plates,
        workflow_id="windowed_query_workflow",
        name="Windowed query workflow",
        owner="TD",
        description="Another test of creating workflows")

    # Try to recreate the following:
    clock_tool = T[clock].define(stride=30 * second)
    M.create_stream(stream_id=every30s, tool_stream=clock_tool)
    env_tool = T[sphere].define(modality='environmental')
    S.create_stream(stream_id=env_kitchen_30_s_window, tool_stream=env_tool)

    motion_tool = T[component].define(input_streams=[S[env_kitchen_30_s_window]], key='motion-S1_K')
    M.create_stream(stream_id=m_kitchen_30_s_window, tool_stream=motion_tool)

    s = M[m_kitchen_30_s_window].relative_window((-30 * second, timedelta(0)))
    counter = T[aggregate].define(input_streams=[M[every30s], s], func=online_count)
    M.create_stream(stream_id=count, tool_stream=counter)
    print(M[count].window((t1, t1 + 5 * minute)).values())

    # w.create_node()
    # # TODO: tool parameters
    # w.create_factor(tool='clock', sources=None)
    # w.create_node(node_id=)

    exit()

    # Simple querying
    env = S[environmental].window((t1, t1 + minute))
    eid = StreamId('electricity')
    elec_tool = T[component].define(input_streams=[env], key='electricity-04063')
    M.create_stream(stream_id=eid, tool_stream=elec_tool)

    el = M[eid].window((t1, t1 + minute))

    q1 = "\n".join("=".join(map(str, ee)) for ee in el)

    print(q1)
    print(el.values())

    clock_tool = T[clock].define(stride=30 * second)
    env_tool = T[sphere].define(modality='environmental')

    # Windowed querying
    M.create_stream(stream_id=every30s, tool_stream=clock_tool)

    print("\n----------")
    print("M[every30s]")
    print("\n".join(map(str, M[every30s].window((t1, t2)))))
    print("----------")
    print("")

    M[every30s] = M.create_stream(stream_id=every30s, tool_stream=clock_tool)
    motion_tool = T[component].define(input_streams=[S[environmental]], key='motion-S1_K')
    M.create_stream(stream_id=m_kitchen_30_s_window, tool_stream=motion_tool)

    print("\n------------------------")
    print("S[m_kitchen_30_s_window]")
    print("\n".join(map(str, M[m_kitchen_30_s_window].window((t1, t2)))))
    print("------------------------")
    print("")

    # Want to be able to reuse the same aggregate tool, but with different parameters (in this case func)
    # Since define() just returns back the object, we have an issue that a new object isn't being created
    # Note that in fact T[aggregate] is returning a stream, and the items() function of the stream just returns a
    # single element, which is the tool class, pre-built with its kwargs
    # So we basically want to have a new stream being created by define, rather than the same one getting reused.
    # Since define is only used for this purpose, there shouldn't be a problem?
    # Hence it seems reasonable to simply use copy.deepcopy when returning the stream object

    averager = T[aggregate].define(
        input_streams=[
            M[every30s],
            S[m_kitchen_30_s_window].relative_window((-30 * second, timedelta(0)))],
        func=online_average
    )

    print(id(averager))

    counter = T[aggregate].define(
        input_streams=[
            M[every30s],
            S[m_kitchen_30_s_window].relative_window((-30 * second, timedelta(0)))],
        func=online_count
    )

    print(id(counter))

    M.create_stream(stream_id=average, tool_stream=averager)
    M.create_stream(stream_id=count, tool_stream=counter)

    stream_ref = M[average].window((t1, t2))
    aa = stream_ref.values()
    print(aa)
    assert (aa == [0.0, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    stream_ref = M[count].window((t1, t1 + 5 * minute))
    cc = stream_ref.values()
    print(cc)
    assert (cc == [3, 4, 4, 3, 3, 3, 3, 3, 3, 3])