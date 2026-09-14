import numpy as np

class PriorSampler:
    @staticmethod
    def draw_samples_seed(param_range, N_e=1, seed=42):
        rng = np.random.default_rng(seed) if seed is not None else np.random.default_rng()
        param_range = np.array(param_range)
        N_par = param_range.shape[0]
        X = np.zeros((N_par, N_e))
        for i in range(N_e):
            sample = param_range[:, 0] + (param_range[:, 1] - param_range[:, 0]) * rng.random(N_par)
            sample_rounded = np.around(sample, decimals=3)
            X[:, i] = sample_rounded
        return X
    @staticmethod
    def draw_samples(param_range, N_e=1, seed=None):
        rng = np.random.default_rng(seed) if seed is not None else np.random.default_rng()
        param_range = np.array(param_range)
        N_par = param_range.shape[0]
        X = np.zeros((N_par, N_e))
        for i in range(N_e):
            sample = param_range[:, 0] + (param_range[:, 1] - param_range[:, 0]) * rng.random(N_par)
            sample_rounded = np.around(sample, decimals=3)
            X[:, i] = sample_rounded
        return X

    @staticmethod
    def save_prior_to_csv(samples, file_path):
        np.savetxt(file_path, samples, delimiter=',', fmt='%.3f')

    @staticmethod
    def load_prior_from_csv(file_path):
        X = np.loadtxt(file_path, delimiter=',')
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        return X