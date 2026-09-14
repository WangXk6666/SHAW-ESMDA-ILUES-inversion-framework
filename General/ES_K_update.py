import numpy as np
import sys

class ES:
    @staticmethod
    def update(X_f, Y_f, obs, sd, param_range,N_var1):
        X_f = np.array(X_f)
        Y_f = np.array(Y_f,dtype='float64')
        obs = np.array(obs)
        N_obs = len(obs)
        N_e = X_f.shape[1]
        if N_e == 1:
            print('Warning: Setting N_e to 1 will cause an error due to a zero denominator in C_XY!')
            sys.exit(1)
        mu_X = np.mean(X_f, axis=1, keepdims=True,dtype='float64')
        mu_Y = np.mean(Y_f, axis=1, keepdims=True,dtype='float64')
        C_XY = (X_f - mu_X) @ (Y_f - mu_Y).T / (N_e - 1)

        C_YY = np.cov(Y_f)
        C_Y = np.diag(np.full(N_var1, sd ** 2, dtype='float64'))
        obs_e = np.tile(obs.reshape(-1, 1), (1, N_e)) + \
                np.random.normal(0, sd, (N_obs, N_e))
        X_a = X_f + C_XY @ np.linalg.solve(C_YY + C_Y, obs_e - Y_f)
        lb = np.tile(param_range[:, 0].reshape(-1, 1), (1, N_e))
        ub = np.tile(param_range[:, 1].reshape(-1, 1), (1, N_e))
        below_lb = X_a < lb
        X_a[below_lb] = (X_f[below_lb] + lb[below_lb]) / 2
        above_ub = X_a > ub
        X_a[above_ub] = (X_f[above_ub] + ub[above_ub]) / 2
        X_k = np.around(X_a, decimals=3)
        return X_k
