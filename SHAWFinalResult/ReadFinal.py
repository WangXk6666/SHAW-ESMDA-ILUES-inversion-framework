import csv
import numpy as np
from datetime import datetime, timedelta
import os
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class ReadFinalResult:
    def _ReadSim(self, Sim_path):
        SimTimes = []
        SimDataList = []
        SimHeaders = ["Time"]
        with open(Sim_path, 'r', encoding='utf-8') as txtfile:
            lines = txtfile.readlines()
            if len(lines) < 3:
                logging.info("Error: Insufficient lines in simulation data file, cannot read header and data.")
                return np.array([]), np.array([]), SimHeaders
            header_line = lines[1].strip().split()
            if len(header_line) < 4:
                logging.info("Error: Incorrect header format of simulation data file, cannot parse data columns.")
                return np.array([]), np.array([]), SimHeaders
            for i in range(3, len(header_line)):
                value = header_line[i]
                try:
                    cm_value = int(float(value) * 100)
                    SimHeaders.append(f"{cm_value} cm")
                except ValueError:
                    logging.info(f"Warning: Cannot convert value '{value}' to centimeter value, skip this column.")
                    continue
            logging.info(f"\n=== Simulation Data Header ===")
            logging.info("SimHeaders = %s", SimHeaders)
            data_lines = lines[2:]
            for line_num, line in enumerate(data_lines, start=3):
                parts = line.strip().split()
                if len(parts) < 4:
                    logging.info(f"Warning: Insufficient data columns in line {line_num}, this line has been skipped.")
                    continue
                try:
                    year = int(parts[2])
                    day_of_year = int(parts[0])
                    hour = int(parts[1]) % 24
                    base_date = datetime.strptime(f"{year} {day_of_year}", "%Y %j")
                    time_obj = datetime(base_date.year, base_date.month, base_date.day, hour)
                    SimTimes.append(time_obj)
                except ValueError as e:
                    logging.info(f"Warning: Time parsing error in line {line_num}: {e}, this line has been skipped.")
                    continue
                try:
                    data_values = list(map(float, parts[3:]))
                    SimDataList.append(data_values)
                except ValueError as e:
                    logging.info(f"Warning: Data value conversion error in line {line_num}: {e}, this line has been skipped.")
                    continue
        SimTimes_array = np.array(SimTimes, dtype='datetime64[s]')
        SimData_array = np.array(SimDataList, dtype=np.float64)
        return SimTimes_array, SimData_array, SimHeaders
    def _ReadObs(self, Obs_path):
        ObsHeaders = []
        with open(Obs_path, 'r', encoding='gbk') as csvfile:
            reader = csv.reader(csvfile)
            try:
                ObsHeaders = next(reader)
                logging.info(f"\n=== Observation Data Header ===")
                logging.info("ObsHeaders = %s", ObsHeaders)
            except StopIteration:
                logging.info("Error: Observation data file is empty, cannot read header.")
                return np.array([]), np.array([]), ObsHeaders
            ObsTimes = []
            ObsDataList = []
            with open(Obs_path, 'r', encoding='gbk') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row_num, row in enumerate(reader, start=2):
                    if len(row) != len(ObsHeaders):
                        logging.info(f"Warning: Column count mismatch in line {row_num} (expected {len(ObsHeaders)} columns, actual {len(row)} columns), this line has been skipped.")
                        continue
                    try:
                        time_str = row[0].strip()
                        time_obj = datetime.strptime(time_str, '%Y/%m/%d %H:%M')
                        ObsTimes.append(time_obj)
                    except ValueError as e:
                        logging.info(f"Warning: Time parsing error in line {row_num}: {e}, this line has been skipped.")
                        continue
                    try:
                        data_values = list(map(float, row[1:]))
                        ObsDataList.append(data_values)
                    except ValueError as e:
                        logging.info(f"Warning: Data value conversion error in line {row_num}: {e}, this line has been skipped.")
                        continue
        ObsTimes_array = np.array(ObsTimes, dtype='datetime64[s]')
        ObsData_array = np.array(ObsDataList, dtype=np.float64)
        return ObsTimes_array, ObsData_array, ObsHeaders
    def _ReadWaterBalance(self, WB_path, obs_type):
        WBTimes = []
        WBDataList = []
        WBHeaders = ["Time", 'PRECIP', 'SNOWMELT', 'INTRCP', 'ET', 'TRANSP', 'CANOPY',
                     'SNOW', 'RESIDUE', 'SOIL', 'DEEP_PERC', 'RUNOFF', 'PONDED',
                     'LATERAL_OUTFLOW', 'SINK_TERM', 'CUM_ET']
        try:
            with open(WB_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            data_start = 0
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                if stripped_line.startswith('DAY HR  YR'):
                    data_start = i + 2
                    break
            if data_start == 0:
                logging.info("Error: Data start marker of water balance file not found")
                return np.array([]), np.array([]), WBHeaders
            for line_num, line in enumerate(lines[data_start:], start=data_start + 1):
                line = line.strip()
                if not line:
                    continue
                parts = list(filter(None, line.split()))
                if len(parts) < 18:
                    logging.info(f"Warning: Incomplete data in line {line_num} ({len(parts)} columns), this line has been skipped.")
                    continue
                try:
                    year = int(parts[2])
                    day_of_year = int(parts[0])
                    hour = int(parts[1]) % 24
                    base_date = datetime(year, 1, 1)
                    time_obj = base_date + timedelta(days=day_of_year - 1, hours=hour)
                    WBTimes.append(time_obj)
                    row_data = {
                        'PRECIP': float(parts[3]),
                        'SNOWMELT': float(parts[4]),
                        'INTRCP': float(parts[5]),
                        'ET': max(0.0, float(parts[6])),
                        'TRANSP': float(parts[7]),
                        'CANOPY': float(parts[8]),
                        'SNOW': float(parts[9]),
                        'RESIDUE': float(parts[10]),
                        'SOIL': float(parts[11]),
                        'DEEP_PERC': float(parts[12]),
                        'RUNOFF': float(parts[13]),
                        'PONDED': float(parts[14]),
                        'LATERAL_OUTFLOW': float(parts[15]),
                        'SINK_TERM': float(parts[16]),
                        'CUM_ET': float(parts[17]),
                    }
                    data_values = row_data[obs_type]
                    WBDataList.append(data_values)
                except (ValueError, IndexError) as e:
                    logging.info(f"Warning: Parsing error in line {line_num}: {e}, this line has been skipped.")
                    continue
            logging.info(f"\n=== Water Balance Data Header ===")
            logging.info("WBHeaders = %s", WBHeaders)
            WBTimes_array = np.array(WBTimes, dtype='datetime64[s]')
            WBData_array = np.array(WBDataList, dtype=np.float64)
            return WBTimes_array, WBData_array, WBHeaders
        except FileNotFoundError:
            logging.info(f"Error: Water balance file '{WB_path}' not found")
            return np.array([]), np.array([]), WBHeaders
        except Exception as e:
            logging.info(f"Error occurred while reading water balance file: {e}")
            return np.array([]), np.array([]), WBHeaders
    def _Readsalt(self, salt_path):
        SaltTimes = []
        SaltDataList = []
        Salt_headers = ["Time"]
        try:
            with open(salt_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            if len(lines) < 3:
                logging.info("Error: Insufficient lines in salt data file, cannot read header and data.")
                return np.array([]), np.array([]), Salt_headers
            header_line = lines[1].strip().split()
            if len(header_line) < 5:
                logging.info("Error: Incorrect header format of salt data file, cannot parse data columns.")
                return np.array([]), np.array([]), Salt_headers
            depth_columns = header_line[4:]
            for depth_str in depth_columns:
                try:
                    depth_m = float(depth_str)
                    depth_cm = int(round(depth_m * 100))
                    Salt_headers.append(f"{depth_cm} cm")
                except ValueError:
                    logging.info(f"Warning: Cannot convert depth '{depth_str}' to numeric value, skip this column.")
                    continue
            logging.info(f"\n=== Salt Data Header ===")
            logging.info("Salt_headers =", Salt_headers)
            data_lines = lines[2:]
            for line_num, line in enumerate(data_lines, start=3):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 5:
                    logging.info(f"Warning: Incomplete data in line {line_num} ({len(parts)} columns), this line has been skipped.")
                    continue
                try:
                    yr = int(parts[2])
                    dy = int(parts[0])
                    hr = int(parts[1]) % 24
                    base_date = datetime(yr, 1, 1)
                    time_obj = base_date + timedelta(days=dy - 1, hours=hr)
                    SaltTimes.append(time_obj)
                except (ValueError, IndexError) as e:
                    logging.info(f"Warning: Time parsing error in line {line_num}: {e}, this line has been skipped.")
                    continue
                try:
                    data_values = [float(val) for val in parts[4:]]
                    SaltDataList.append(data_values)
                except ValueError as e:
                    logging.info(f"Warning: Data value conversion error in line {line_num}: {e}, this line has been skipped.")
                    continue
            SaltTime_array = np.array(SaltTimes, dtype='datetime64[s]')
            SaltData_array = np.array(SaltDataList, dtype=np.float64)
            return SaltTime_array, SaltData_array, Salt_headers
        except FileNotFoundError:
            logging.info(f"Error: Salt data file '{salt_path}' not found")
            return np.array([]), np.array([]), Salt_headers
        except Exception as e:
            logging.info(f"Error occurred while reading salt data file: {e}")
            return np.array([]), np.array([]), Salt_headers
    def ReadData(self, Obs_path, Sim_path, obs_type):
        if obs_type in ['temp', 'moi', 'mat']:
            ObsTimes_array, ObsData_array, ObsHeaders = self._ReadObs(Obs_path)
            SimTimes_array, SimData_array, SimHeaders = self._ReadSim(Sim_path)
        elif obs_type in ['PRECIP', 'SNOWMELT', 'INTRCP', 'ET', 'TRANSP', 'CANOPY', 'SNOW', 'RESIDUE', 'SOIL']:
            ObsTimes_array, ObsData_array, ObsHeaders = self._ReadObs(Obs_path)
            SimTimes_array, SimData_array, SimHeaders = self._ReadWaterBalance(Sim_path, obs_type)
        elif obs_type in ['solute', 'total_salt']:
            ObsTimes_array, ObsData_array, ObsHeaders = self._ReadObs(Obs_path)
            SimTimes_array, SimData_array, SimHeaders = self._Readsalt(Sim_path)
        else:
            raise ValueError(f'obs_type_{obs_type} is not supported, please use the following types:\n'
                             f'[temp, moi, mat, solute, total_salt]\n'
                             f'[PRECIP, SNOWMELT, INTRCP, ET, TRANSP, CANOPY, SNOW, RESIDUE, SOIL, '
                             f'DEEP_PERC, RUNOFF, PONDED, LATERAL_OUTFLOW, SINK_TERM, CUM_ET]')
        return SimTimes_array, SimData_array, SimHeaders, ObsTimes_array, ObsData_array, ObsHeaders
