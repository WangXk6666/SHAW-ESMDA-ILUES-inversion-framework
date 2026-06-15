import numpy as np
import csv
import os
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class obs_read:
    def __init__(self, work_dir):
        self.work_dir = work_dir
        self.temp_headers = None
        self.moi_headers = None
        self.mat_headers = None
        self.et_headers = None
        self.solute_headers = None
        self.total_salt_headers = None

    def _load_to_array_by_column(self, file_path):
        if not file_path or not os.path.exists(file_path):
            return None, None
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                first_line = f.readline()
                delimiter = '\t' if '\t' in first_line else ','
                f.seek(0)
                reader = csv.reader(f, delimiter=delimiter)
                headers = next(reader)
                data_headers = headers[1:] if len(headers) > 1 else []
                num_obs_points = len(data_headers)
                obs_points_data = [[] for _ in range(num_obs_points)]
                for row in reader:
                    if not row:
                        continue
                    for j in range(num_obs_points):
                        if j + 1 < len(row):
                            try:
                                obs_points_data[j].append(float(row[j + 1]))
                            except ValueError:
                                obs_points_data[j].append(np.nan)
                        else:
                            obs_points_data[j].append(np.nan)
                data = []
                for obs_data in obs_points_data:
                    data.extend(obs_data)
                return np.array(data), data_headers
        except Exception as e:
            logging.info(f"File loading error {file_path}: {str(e)}")
            return None,None
    def _obs_temp(self, Obs_temp_path):
        temp_array, self.temp_headers = self._load_to_array_by_column(Obs_temp_path)
        return temp_array

    def _obs_moi(self, Obs_moi_path):
        moi_array, self.moi_headers = self._load_to_array_by_column(Obs_moi_path)
        return moi_array

    def _obs_matric(self, Obs_matric_path):
        matric_array, self.mat_headers = self._load_to_array_by_column(Obs_matric_path)
        return matric_array

    def _obs_evapotranspiration(self, Obs_et_path):
        et_array, self.et_headers = self._load_to_array_by_column(Obs_et_path)
        return et_array

    def _obs_solute(self, Obs_solute_path):
        solute_array, self.solute_headers = self._load_to_array_by_column(Obs_solute_path)
        return solute_array

    def _obs_total_salt(self, Obs_total_salt_path):
        total_salt_array, self.total_salt_headers = self._load_to_array_by_column(Obs_total_salt_path)
        return total_salt_array

    def _temp_moi(self, Obs_temp_path, Obs_moi_path):
        temp = self._obs_temp(Obs_temp_path)
        moi = self._obs_moi(Obs_moi_path)
        return temp, moi

    def _temp_matric(self, Obs_temp_path, Obs_matric_path):
        temp = self._obs_temp(Obs_temp_path)
        matric = self._obs_matric(Obs_matric_path)
        return temp, matric

    def _et_moi(self, Obs_moi_path, Obs_et_path):
        et = self._obs_evapotranspiration(Obs_et_path)
        moi = self._obs_moi(Obs_moi_path)
        return et, moi

    def _et_mat(self, Obs_matric_path, Obs_et_path):
        et = self._obs_evapotranspiration(Obs_et_path)
        matric = self._obs_matric(Obs_matric_path)
        return et, matric

    def _et_temp(self, Obs_temp_path, Obs_et_path):
        et = self._obs_evapotranspiration(Obs_et_path)
        temp = self._obs_temp(Obs_temp_path)
        return et, temp

    def _solute_moi(self, Obs_solute_path, Obs_moi_path):
        solute = self._obs_solute(Obs_solute_path)
        moi = self._obs_moi(Obs_moi_path)
        return solute, moi

    def _solute_mat(self, Obs_solute_path, Obs_mat_path):
        solute = self._obs_solute(Obs_solute_path)
        mat = self._obs_matric(Obs_mat_path)
        return solute,mat

    def _total_salt_moi(self, Obs_total_salt_path, Obs_moi_path):
        total_salt = self._obs_total_salt(Obs_total_salt_path)
        moi = self._obs_moi(Obs_moi_path)
        return total_salt, moi

    def _total_salt_mat(self, Obs_total_salt_path, Obs_mat_path):
        total_salt = self._obs_total_salt(Obs_total_salt_path)
        mat = self._obs_matric(Obs_mat_path)
        return total_salt, mat

    def observation(self, obs_type):
        Obs_path = {'temp':os.path.join(self.work_dir, 'Obs_temperature.csv'),
                    'moi':os.path.join(self.work_dir, 'Obs_liquid.csv'),
                    'mat':os.path.join(self.work_dir, 'Obs_matric.csv'),
                    'ET':os.path.join(self.work_dir, 'Obs_evapotranspiration.csv'),
                    'solute':os.path.join(self.work_dir, 'Obs_solute.csv'),
                    'total_salt':os.path.join(self.work_dir, 'Obs_total_salt.csv'),
                 }
        if obs_type == 'temp':
            obs_value_1 = self._obs_temp(Obs_path['temp'])
            obs_value_2 = self._obs_moi(Obs_path['moi'])
            obs_type={'First':'temp','Second':'moi'}
        elif obs_type == 'moi':
            obs_value_1 = self._obs_moi(Obs_path['moi'])
            obs_value_2 = self._obs_temp(Obs_path['temp'])
            obs_type = {'First': 'moi', 'Second': 'temp'}
        elif obs_type == 'mat':
            obs_value_1 = self._obs_matric(Obs_path['mat'])
            obs_value_2 = self._obs_temp(Obs_path['temp'])
            obs_type = {'First': 'mat', 'Second': 'temp'}
        elif obs_type == 'ET':
            obs_value_1 = self._obs_evapotranspiration(Obs_path['ET'])
            obs_value_2 = self._obs_moi(Obs_path['moi'])
            obs_type = {'First': 'ET', 'Second': 'moi'}
        elif obs_type == 'solute':
            obs_value_1 = self._obs_solute(Obs_path['solute'])
            obs_value_2 = self._obs_moi(Obs_path['moi'])
            obs_type = {'First': 'solute', 'Second': 'moi'}
        elif obs_type == 'total_salt':
            obs_value_1 = self._obs_total_salt(Obs_path['total_salt'])
            obs_value_2 = self._obs_moi(Obs_path['moi'])
            obs_type = {'First': 'total_salt', 'Second': 'moi'}

        else:
            valid_options = "['moi', 'temp', 'mat', 'ET', 'solute', 'total_salt']"
            raise ValueError(f"obs_type 必须为 {valid_options} 之一，当前值为 '{obs_type}'")
        relevant_headers = {
            'temp_headers': self.temp_headers, 'moi_headers': self.moi_headers,'mat_headers': self.mat_headers,
            'solute_headers': self.solute_headers, 'total_salt_headers': self.total_salt_headers}
        logging.info(f"relevant_headers={relevant_headers}")
        return obs_value_1, obs_value_2, relevant_headers,obs_type


if __name__ == "__main__":
    pass

