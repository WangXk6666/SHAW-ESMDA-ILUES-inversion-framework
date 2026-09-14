from datetime import datetime, timedelta
import numpy as np
import os
import csv
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class SoluteResultReader:
    def __init__(self, work_dir):
        self.work_dir = work_dir
        self.sim_data = None
        self.sim_dates = None
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
                    logging.info(f"Column name {h} contains cm units but cannot extract numerical values, skip matching")
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
                    return None, None
                header_line = lines[1].split()
                if not header_line or len(header_line) < 5:
                    logging.info(f"Format error in file {filepath}: incomplete column headings")
                    return None, None
                data_columns = header_line[4:]
                if not data_columns:
                    logging.info(f"File {filepath} has no valid data columns")
                    return None, None
                matching_cols = self._get_matching_columns(data_columns, headers)
                if not matching_cols:
                    logging.info(f"Column matching headers not found in file {filepath}: {headers}")
                    return None, None
                obs_points_data = [[] for _ in range(len(matching_cols))]
                sim_dates = []
                for line_idx, line in enumerate(lines[2:], start=3):
                    line = line.strip()
                    if not line:
                        continue
                    values = line.split()
                    if len(values) < 5:
                        logging.info(f"The data on line {line_idx} of file {filepath} is incomplete, skip it")
                        continue
                    try:
                        yr = int(values[2])
                        dy = int(values[0])
                        hr = int(values[1])
                        base_date = datetime(yr, 1, 1)
                        current_date = base_date + timedelta(days=dy-2, hours=hr)
                        date_str = current_date.strftime("%Y/%m/%d %H:%M")
                        sim_dates.append(date_str)
                    except (ValueError, IndexError) as e:
                        logging.info(f"Time parsing failed on line {line_idx} of file {filepath}: {e}, skip that line")
                        continue
                    data_values = values[4:]
                    for i, col_idx in enumerate(matching_cols):
                        if col_idx < len(data_values):
                            val_str = data_values[col_idx]
                            try:
                                obs_points_data[i].append(float(val_str))
                            except ValueError:
                                logging.info(f"The value in line {line_idx}, column {col_idx+5} of file"
                                      f" {filepath} is invalid: {val_str}, denoted as NaN")
                                obs_points_data[i].append(np.nan)
                data = []
                for obs_data in obs_points_data:
                    data.extend(obs_data)
                return np.array(data), sim_dates
        except FileNotFoundError:
            logging.info(f"{filepath} is not found")
            return None, None
        except Exception as e:
            logging.info(f"Error processing file {filepath}: {str (e)}")
            return None, None
    def _save_to_csv(self, sim_headers, sim_data, sim_dates, output_path=None):
        if sim_data is None or sim_dates is None:
            logging.info("No valid data to save")
            return
        num_points = len(sim_headers)
        num_timesteps = len(sim_dates)
        if len(sim_data) != num_points * num_timesteps:
            logging.info(f"Data length mismatch: observation point {num_points} x "
                  f"time steps {num_timesteps} ≠ data length {len (sim_data)}")
            return
        if not output_path:
            filename = f"{self.obs_type.replace(' ', '_')}_data.csv"
            output_path = os.path.join(self.work_dir, filename)
        reshaped_data = []
        for t in range(num_timesteps):
            row = []
            for p in range(num_points):
                idx = p * num_timesteps + t
                row.append(sim_data[idx])
            reshaped_data.append(row)
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                header = ['Date'] + sim_headers
                writer.writerow(header)
                for i, date_str in enumerate(sim_dates):
                    row = [date_str] + reshaped_data[i]
                    writer.writerow(row)
            logging.info(f"The data has been successfully saved to：{output_path}")
        except Exception as e:
            logging.info(f"Failed to save CSV file：{str(e)}")
    def read_sim_data(self, thread_id, out_iter, inner_iter,obs_type, sim_headers):
        file_path = {
            'solute': os.path.join(self.work_dir, 'SOLUTE CONCENTRATION.OUT'),
            'total_salt': os.path.join(self.work_dir, 'TOTAL SALT CONCENTRATION.OUT'),
            'save_path': os.path.join(self.work_dir, f'sim_{obs_type}.csv'),
        }
        if obs_type not in file_path:
            raise ValueError(f'obs_type must be "solute" or "total_salt"')
        sim_path = file_path[obs_type]
        self.sim_data, self.sim_dates = self._read_data_file_by_headers(sim_path, sim_headers)
        if thread_id == out_iter == inner_iter == 0:
            self._save_to_csv(sim_headers, self.sim_data, self.sim_dates, file_path['save_path'])
        return self.sim_data
