from datetime import datetime, timedelta
import numpy as np
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class SingleResultReader:
    def __init__(self, sim_temp_path, sim_moi_path, sim_matric_path, temp_headers, moi_headers, mat_headers):
        self.sim_temp_path = sim_temp_path
        self.sim_moi_path = sim_moi_path
        self.sim_matric_path = sim_matric_path
        self.temp_headers = temp_headers
        self.moi_headers = moi_headers
        self.mat_headers = mat_headers
        self.sim_temp = None
        self.sim_moi = None
        self.sim_matric = None
        self.temp_moi = None
        self.temp_mat = None
    def _get_matching_columns(self, header, headers):
        headers = [h.strip().lower() for h in headers if h.strip()]
        target_values = []
        for h in headers:
            if 'cm' in h:
                try:
                    cm_value = float(h.replace('cm', '').strip())
                    m_value = cm_value / 100
                    target_values.append("{0:.2f}".format(m_value))
                except ValueError:
                    continue
            else:
                target_values.append(h)
        matching_indices = []
        for idx, col_name in enumerate(header):
            if col_name.lower() in target_values:
                matching_indices.append(idx)
        return matching_indices
    def _read_data_file_by_headers(self, filepath, headers):
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
                if len(lines) < 3:
                    logging.info(f"Format error in file {filepath}: insufficient lines")
                    return None
                header_line = lines[1].split()
                if not header_line:
                    logging.info(f"File {filepath} format error: no column headers")
                    return None
                data_columns = header_line[3:]
                matching_cols = self._get_matching_columns(data_columns, headers)
                if not matching_cols:
                    logging.info(f"Column matching {headers} not found in file {filepath}")
                    return None
                obs_points_data = [[] for _ in range(len(matching_cols))]
                for line in lines[2:]:
                    if not line.strip():
                        continue
                    values = line.split()
                    if len(values) < 4:
                        continue
                    data_values = values[3:]
                    for i, col_idx in enumerate(matching_cols):
                        if col_idx < len(data_values):
                            try:
                                obs_points_data[i].append(float(data_values[col_idx]))
                            except ValueError:
                                obs_points_data[i].append(np.nan)
                data = []
                for obs_data in obs_points_data:
                    data.extend(obs_data)
                return np.array(data)
        except FileNotFoundError:
            logging.info(f" {filepath} is not found")
            return None
        except Exception as e:
            logging.info(f"Error processing file {filepath}: {str (e)}")
            return None
    def read_sim_temp(self):
        self.sim_temp = self._read_data_file_by_headers(
            self.sim_temp_path, self.temp_headers
        )
        return self.sim_temp
    def read_sim_moi(self):
        self.sim_moi = self._read_data_file_by_headers(
            self.sim_moi_path, self.moi_headers
        )
        return self.sim_moi
    def read_sim_matric(self):
        self.sim_matric = self._read_data_file_by_headers(
            self.sim_matric_path, self.mat_headers
        )
        return self.sim_matric
