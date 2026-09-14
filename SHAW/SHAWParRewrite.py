import numpy as np
import time
import re
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class ParaRewrite:
    @staticmethod
    def rewrite(InputPath, Parameters, mapping):
        max_retries = 50
        retry_delay = 0.1
        content = None
        for attempt in range(max_retries):
            try:
                with open(InputPath, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f]
                max_cols = max(len(re.split(r'[ \t]+', line)) for line in lines) if lines else 0
                content = np.full((len(lines), max_cols), fill_value='', dtype=object)
                for i, line in enumerate(lines):
                    data = re.split(r'[ \t]+', line)
                    content[i, :len(data)] = data
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    logging.info(f"⚠️ The file is locked, wait for {retry_delay} seconds and retry... (Try {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    raise RuntimeError(f"❌ Unable to read file {InputPath}, possibly locked by SHAW model")
        if 'single' in mapping:
            for item in mapping['single']:
                try:
                    row, col, param_idx = item
                    if (0 <= row < len(content) and
                            0 <= col < content.shape[1] and
                            0 <= param_idx < len(Parameters)):
                        content[row, col] = str(Parameters[param_idx])
                    else:
                        logging.info(f"⚠️ 'Single' rule {item} index out of bounds, skip")
                except Exception as e:
                    logging.info(f"⚠️ Error processing 'single' rule {item}: {e}, skip")
        if 'range' in mapping:
            for item in mapping['range']:
                try:
                    start_row, end_row, col, param_idx = item
                    rows = slice(start_row, end_row)
                    if (0 <= start_row < end_row <= len(content) and
                            0 <= col < content.shape[1] and
                            0 <= param_idx < len(Parameters)):
                        content[rows, col] = str(Parameters[param_idx])
                    else:
                        logging.info(f"⚠️ 'range' rule {item} index out of bounds, skip")
                except Exception as e:
                    logging.info(f"⚠️ Error processing 'range' rule {item}: {e}, skip")
        for attempt in range(max_retries):
            try:
                with open(InputPath, 'w', encoding='utf-8') as f:
                    for row in content:
                        line_parts = [str(item) for item in row if item != '']
                        line_str = '\t'.join(line_parts)
                        f.write(line_str + '\n')
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    logging.info(f"⚠️ The file is locked, wait for {retry_delay} seconds and retry writing"
                          f"... (Try {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    raise RuntimeError(f"❌ Unable to write file {InputPath}，May be locked by SHAW model")
