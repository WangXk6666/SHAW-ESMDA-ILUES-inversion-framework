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
                    logging.info(f"⚠️ The file is locked, wait for {retry_delay} seconds and retry... (尝Try {attempt + 1}/{max_retries})")
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
if __name__ == '__main__':
    input_path=r'H:\Numerical case\model & demo\TEST_SHAW\Model\SIT.INP'
    parameters=[7.565,0.521,11.567,-219.342,562.244,7.841,33.922,18.885,0.403,0.55,10.106,0.225,112.469,
27553.454,5.272,0.237,1.731,1513,45.997,-0.322,0.356,3.669,1555,40.888,-0.187,0.362,4.956,1214,33.608,-0.33,
0.394,5.726,
1256,36.544,
-0.111,0.381,
5.635,1456,
36.155,
-0.331,
0.388,
5.861,
1356,
38.04,
-0.163,
0.372,
5.94,
1240,
39.415,
-0.343,
0.383,
5.381,
1350,
37.119,
-0.113,
0.38,
5.745,
1020,
41.355,
-0.258,
0.369,
4.951,
1100,
37.794,
-0.393,
0.398,
5.493,
]
    mapping = {
        'single': [(4, 0, 0), (6, 3, 1), (6, 4, 2), (6, 7, 3), (7, 0, 4), (7, 1, 5), (7, 2, 6), (7, 3, 7),
                   (7, 4, 8), (7, 5, 9), (8, 3, 10), (8, 4, 11), (11, 1, 12), (11, 4, 13), (11, 5, 14),
                   (12, 2, 15), (12, 3, 16)],
        'range': [(13, 20, 6, 17), (13, 20, 7, 18), (13, 20, 9, 19), (13, 20, 10, 20), (13, 20, 11, 21),
                  (20, 24, 6, 22), (20, 24, 7, 23), (20, 24, 9, 24), (20, 24, 10, 25), (20, 24, 11, 26),
                  (24, 28, 6, 27), (24, 28, 7, 28), (24, 28, 9, 29), (24, 28, 10, 30), (24, 28, 11, 31),
                  (28, 32, 6, 32), (28, 32, 7, 33), (28, 32, 9, 34), (28, 32, 10, 35), (28, 32, 11, 36),
                  (32, 36, 6, 37), (32, 36, 7, 38), (32, 36, 9, 39), (32, 36, 10, 40), (32, 36, 11, 41),
                  (36, 40, 6, 42), (36, 40, 7, 43), (36, 40, 9, 44), (36, 40, 10, 45), (36, 40, 11, 46),
                  (40, 44, 6, 47), (40, 44, 7, 48), (40, 44, 9, 49), (40, 44, 10, 50), (40, 44, 11, 51),
                  (44, 48, 6, 52), (44, 48, 7, 53), (44, 48, 9, 54), (44, 48, 10, 55), (44, 48, 11, 56),
                  (48, 52, 6, 57), (48, 52, 7, 58), (48, 52, 9, 59), (48, 52, 10, 60), (48, 52, 11, 61),
                  (52, 54, 6, 62), (52, 54, 7, 63), (52, 54, 9, 64), (52, 54, 10, 65), (52, 54, 11, 66),
                  ]}
    R=ParaRewrite()
    R.rewrite(input_path,parameters,mapping)