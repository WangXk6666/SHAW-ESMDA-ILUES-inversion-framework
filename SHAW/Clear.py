import os
import shutil
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Clear:
    @staticmethod
    def clear(N_thread,base_work_dir):
        for i in range(1, N_thread + 1):
            thread_work_dir = os.path.join(base_work_dir, f"thread_{i}")
            if os.path.exists(thread_work_dir):
                 try:
                    shutil.rmtree(thread_work_dir)
                 except Exception as e:
                    logging.info(f"Delete thread directory {thread_work_dir} Failed (file may be occupied): {str(e)}")
            else:
                logging.info(f"The thread directory does not exist, there is no need to delete it: {thread_work_dir}")