#
# Django SQL Profiler Log Analyser
# Author: Colin Howe (http://github.com/colinhowe)
# License: Apache License, Version 2 (http://www.apache.org/licenses/LICENSE-2.0.html)
#
# == Description ==
# 
# This is an analyser for the log files generated by the profiler.
#
# == Usage ==
#
# python analyse.py < logfile
# 
# This will output the data as a number of sections like the following:
#   Trace: ('/home/colin/code/polls/models.py', 52, 'get_all_comments', 'comments = Comment.objects.all()')
#   Time: 0.00267
#   Count: 18
#   Sample query: SELECT `id`, `text` FROM `polls_comment`
#
# The sections will be ordered by time ascending. This means that the slowest 
# query will be at the bottom of the output.
#
# The total time and count only include sampled queries. So, if your sampling
# rate is 20% then these numbers will be approximately 20% of the actual count
# and total time.
# 

import sys
from base64 import b64decode
from zlib import decompress
from pickle import loads

# This dictionary is keyed by the last entry in the stack trace. This lets us
# group SQL queries according to the code that they originated from. 
time_by_trace = {}

for line in sys.stdin:
    (time, sql, stack) = loads(decompress(b64decode(line)))
    origin = stack[-1]
    (old_time, old_count, _) = time_by_trace.get(origin, (0.0, 0, sql))
    time_by_trace[origin] = (old_time + time, old_count + 1, sql)
    
# Sort the traces by time and print
as_list = time_by_trace.items()
as_list.sort(key = lambda x: x[1][0])
for (trace, time) in as_list:
    print "Trace: %s\nTime: %.5f\nCount: %s\nSample query: %s\n"%(trace, time[0], time[1], time[2])
