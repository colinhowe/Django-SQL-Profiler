#
# Django SQL Profiler
# Author: Colin Howe (http://github.com/colinhowe)
# License: Apache License, Version 2 (http://www.apache.org/licenses/LICENSE-2.0.html)
#
# == Description ==
# 
# This is a CursorWrapper that adds profiling to each SQL query. There is a
# configurable random chance that an SQL query will be profiled and logged.
#
# This log can then be analysed to find which SQL queries are taking the longest
# total time. This is helpful as it will catch cases where your bottleneck is a 
# fast query being executed millions of times. 
#
# == Usage ==
#
# 1. In your settings module set:
#    a. SQL_LOG_PATH to the path where the SQL log should be
#    b. SQL_LOG_FREQ to the frequency with which queries should be logged
#       SQL_LOG_FREQ = 0.2 would cause 20% of queries to be logged
# 2. Add this module to your INSTALLED_APPS
# 3. Let your app run for a while
# 4. Use analyse.py to analyse the generated log
# 
try:
    from settings import SQL_LOG_PATH, SQL_LOG_FREQ
    
    if SQL_LOG_PATH is not None and SQL_LOG_FREQ is not None:
        import random
        from time import time
        from picklefield.fields import dbsafe_encode

        class CursorDebugWrapper(object):
            def __init__(self, cursor, db):
                self.cursor = cursor
                self.db = db
        
            def log_sql(self, sql, time):
                import traceback
                if random.random() < SQL_LOG_FREQ:
                    stack = [trace for trace in traceback.extract_stack()]
                    
                    f = open(SQL_LOG_PATH, 'a')
                    f.write("%s\n"%(dbsafe_encode((time, sql, stack), compress_object=True)))
                    f.close()
        
            def execute(self, sql, params=()):
                start = time()
                try:
                    return self.cursor.execute(sql, params)
                finally:
                    stop = time()
                    sql = self.db.ops.last_executed_query(self.cursor, sql, params)
                    self.log_sql(sql, stop - start)
        
            def executemany(self, sql, param_list):
                start = time()
                try:
                    return self.cursor.executemany(sql, param_list)
                finally:
                    stop = time()
                    self.log_sql(sql, stop - start)
        
            def __getattr__(self, attr):
                if attr in self.__dict__:
                    return self.__dict__[attr]
                else:
                    return getattr(self.cursor, attr)
        
            def __iter__(self):
                return iter(self.cursor)
            
        def fake_cursor(self):
            return CursorDebugWrapper(self._cursor(), self)

        import django.db.backends
        django.db.backends.BaseDatabaseWrapper.cursor = fake_cursor
except:
    pass
