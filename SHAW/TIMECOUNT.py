import time
from functools import wraps
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class TIME:
    @staticmethod
    def time_it(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.perf_counter()
            result = func(self, *args, **kwargs)
            end_time = time.perf_counter()
            duration_sec = end_time - start_time
            if duration_sec<60 :
                duration = duration_sec
                unit = 's'
            elif 60 <= duration_sec < 3600:
                duration = duration_sec / 60
                unit = 'min'
            elif 3600 <= duration_sec < 86400:
                duration = duration_sec / 3600
                unit = 'h'
            else:
                duration = duration_sec / 86400
                unit = 'd'
            logging.info(f"\n【 Timing Log 】 Method '{func.__name__}' Completed:")
            logging.info(f"  - time-consuming:  {duration:.4f} {unit}")
            logging.info("-" * 60)
            return result
        return wrapper