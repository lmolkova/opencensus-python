# Copyright 2017, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import os
import sys

sys.path.append(os.path.relpath("."))
from opencensus.trace import execution_context
from opencensus.trace import span
from opencensus.trace import attributes
from opencensus.trace import link
from opencensus.trace import time_event
from opencensus.trace import status
from opencensus.trace.exporters import opencensusd_exporter

from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import always_on
from datetime import timedelta
from datetime import datetime
import time


def function_to_trace():
    time.sleep(1)


def main():
    sampler = always_on.AlwaysOnSampler()
    exporter = opencensusd_exporter.OpenCensusDExporter(
        service_name="helloworld_main")

    tracer = Tracer(sampler=sampler, exporter=exporter)

    for i in range(100):
        with tracer.span(name='request') as root_span:
            tracer.add_attribute_to_current_span(
                attribute_key='root1', attribute_value='example value')
            tracer.add_attribute_to_current_span(
                attribute_key='root2', attribute_value=1)
            tracer.add_attribute_to_current_span(
                attribute_key='root3', attribute_value=False)
            function_to_trace()
            root_span.span_kind = span.SpanKind.SERVER
            root_span.status = status.Status(2, "ERR")
            root_span.same_process_as_parent_span = False

            annotation1 = time_event.TimeEvent(
                timestamp=datetime.utcnow() + timedelta(seconds=-10),
                annotation=time_event.Annotation(description="hi there1", attributes=attributes.Attributes(attributes={"a": "a", "1": 1, "False": False})))

            root_span.add_time_event(annotation1)

            te1 = time_event.TimeEvent(
                timestamp=datetime.utcnow() + timedelta(seconds=-1),
                message_event=time_event.MessageEvent(id=1234, type=time_event.Type.SENT, uncompressed_size_bytes=10, compressed_size_bytes=1))

            root_span.add_time_event(te1)

            #root_span._child_spans = 1
            with tracer.span(name='child') as child_span:
                #tracer.add_attribute_to_current_span(attribute_key='child1', attribute_value=1234)

                function_to_trace()
                child_span.span_kind = span.SpanKind.CLIENT
                child_span.status = status.Status(0, "OK")
                l1 = link.Link("1af32e7d9a324b6eb32b92a4ca449a41", "16e156e4fc274474", link.Type.CHILD_LINKED_SPAN, attributes=attributes.Attributes(
                    attributes={'test_str_key': 'test_str_value', 'test_int_key': 1, 'test_bool_key': False}))
                child_span.add_link(l1)

                #l2 = link.Link("2af32e7d9a324b6eb32b92a4ca449a41", "26e156e4fc274474", link.Type.PARENT_LINKED_SPAN, {"a":1, "b":False, "c":"s"})
                # child_span.add_link(l2)

                child_span.same_process_as_parent_span = True
                child_span.add_annotation(
                    'hi there2', name='octo-span', age=98)
        time.sleep(5)


if __name__ == '__main__':
    main()
