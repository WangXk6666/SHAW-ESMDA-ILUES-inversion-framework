import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class WaterBalanceReader:
    def __init__(self, work_dir):
        self.work_dir = work_dir
        self.data = None
        self.columns = ['PRECIP', 'SNOWMELT', 'INTRCP', 'ET', 'TRANSP', 'CANOPY', 'SNOW', 'RESIDUE', 'SOIL', 'DEEP_PERC',
            'RUNOFF', 'PONDED', 'LATERAL_OUTFLOW', 'SINK_TERM', 'CUM_ET']
        self.Result = None
    def _parse_data(self, part):
        if part == '*******':
            return np.nan
        return float(part)
    def _read_file(self):
        file_path = os.path.join(self.work_dir, 'SUMMARY WATER BALANCE.OUT')
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        data_start = 0
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.startswith('DAY HR  YR'):
                data_start = i + 2
                break
        data_list = []
        for line in lines[data_start:]:
            line = line.strip()
            if not line:
                continue
            parts = list(filter(None, line.split()))
            if len(parts) < 19:
                continue
            try:
                row_data = {
                    'DAY': int(parts[0]),
                    'HR': int(parts[1]),
                    'YR': int(parts[2]),
                    'PRECIP': self._parse_data(parts[3]),
                    'SNOWMELT': self._parse_data(parts[4]),
                    'INTRCP': self._parse_data(parts[5]),
                    'ET': max(0.0, self._parse_data(parts[6])),
                    'TRANSP': self._parse_data(parts[7]),
                    'CANOPY': self._parse_data(parts[8]),
                    'SNOW': self._parse_data(parts[9]),
                    'RESIDUE': self._parse_data(parts[10]),
                    'SOIL':self._parse_data(parts[11]),
                    'DEEP_PERC':self._parse_data(parts[12]),
                    'RUNOFF': self._parse_data(parts[13]),
                    'PONDED': self._parse_data(parts[14]),
                    'LATERAL_OUTFLOW': self._parse_data(parts[15]),
                    'SINK_TERM': self._parse_data(parts[16]),
                    'CUM_ET': self._parse_data(parts[17]),
                }
                data_list.append(row_data)
            except (ValueError, IndexError) as e:
                logging.info(f"Error parsing line: {line}, error: {e}")
                continue
        self.data = pd.DataFrame(data_list)
        self._convert_date()
        self.Result = self.data[self.columns].to_numpy()
        return self.data
    def _convert_date(self):
        dates = []
        for _, row in self.data.iterrows():
            try:
                base_date = datetime(int(row['YR']), 1, 1)
                date = base_date + timedelta(days=int(row['DAY']) - 1, hours=int(row['HR']))
                dates.append(date.strftime('%Y/%m/%d %H:%M'))
            except (ValueError, TypeError) as e:
                logging.info(f"Error converting date: {e}")
                dates.append(None)
        self.data['DATE'] = dates
        cols = ['DATE'] + [col for col in self.data.columns if col != 'DATE']
        self.data = self.data[cols]
    def _save_to_csv(self):
        outpath = os.path.join(self.work_dir,'water_balance.csv')
        self.data.to_csv(outpath, index=False)
        logging.info(f"The data has been saved to {outpath}")
    def get_result(self, variable):
        self.data = self._read_file()
        if variable not in self.columns:
            raise ValueError(f"The variable {variable} does not exist."
                             f"The available variables include: {', '.join(self.columns)}")
        return self.Result[:, self.columns.index(variable)]

