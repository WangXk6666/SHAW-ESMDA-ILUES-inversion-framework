import numpy as np

class PriorSampler:
    @staticmethod
    def draw_samples(param_range,N_e=1):
        param_range = np.array(param_range)
        N_par =param_range.shape[0]
        X = np.zeros((N_par, N_e))
        for i in range(N_e):
            sample = param_range[:, 0] + (param_range[:, 1] - param_range[:, 0]) * np.random.rand(N_par)
            sample_rounded = np.around(sample, decimals=3)
            X[:, i] = sample_rounded
        return X
if __name__ == '__main__':
    P=PriorSampler()
    param_range = np.array([[0.1, 5],  # Line E
                            [0, 1], [0, 20], [-300, -100],  # -Line F1
                            [0, 1000], [0, 20], [20, 40], [10, 40], [0, 1], [0, 1],  # Fa-1
                            [0, 20], [0, 0.4],  # F0-1
                            [0, 200], [1000, 50000], [0, 8],  # Line H1
                            [0.1, 0.3], [0, 3],  # Line J
                            [1000, 1600], [25, 50], [-0.2, 0], [0.35, 0.42], [2.5, 7],  # Layer 1
                            [1000, 1600], [25, 50], [-0.2, 0], [0.35, 0.42], [2.5, 7],  # Layer 2
                            [1000, 1600], [25, 50], [-0.2, 0], [0.35, 0.42], [2.5, 7],  # Layer 3
                            [1000, 1600], [25, 50], [-0.2, 0], [0.35, 0.42], [2.5, 7],  # Layer 4
                            [1000, 1600], [25, 50], [-0.2, 0], [0.35, 0.42], [2.5, 7],  # Layer 5
                            [1000, 1600], [25, 50], [-0.2, 0], [0.35, 0.42], [2.5, 7],  # Layer 6
                            [1000, 1600], [25, 50], [-0.2, 0], [0.35, 0.42], [2.5, 7],  # Layer 7
                            [1000, 1600], [25, 50], [-0.2, 0], [0.35, 0.42], [2.5, 7],  # Layer 8
                            [1000, 1600], [25, 50], [-0.2, 0], [0.35, 0.42], [2.5, 7],  # Layer 9
                            [1000, 1600], [25, 50], [-0.2, 0], [0.35, 0.42], [2.5, 7],  # Layer 10
                            ])
    PAR=P.draw_samples(param_range,1)
    print(PAR)
