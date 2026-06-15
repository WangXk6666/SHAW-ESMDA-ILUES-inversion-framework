import numpy as np
from scipy.linalg import inv
from General.ES_K_update import ES


class LocalUpdate:
    @staticmethod
    def local_update(out_iter, X_f, Y_f, obs, sd, param_range,C_XX,C_Y,alpha = 0.1,flag='K',beta=1.0, N_var1=100):
        sd = np.array(sd)
        param_range = np.array(param_range)
        C_Y = np.array(C_Y)
        C_XX = np.array(C_XX)
        alpha = alpha
        beta = beta
        X_f = np.array(X_f)
        Y_f = np.array(Y_f)
        obs = np.array(obs)
        print(obs)
        N_e = X_f.shape[1]
        N_le = int(np.ceil(N_e * alpha))
        X_a = np.full_like(X_f, np.nan)
        obs_diff = Y_f.T - obs.reshape(1, -1)
        J1 = np.diag(obs_diff @ np.linalg.solve(C_Y, obs_diff.T))
        J1 = J1 / np.max(J1)
        for i in range(N_e):
            state_diff = X_f.T - X_f[:, i].reshape(1, -1)
            J2 = np.diag(state_diff @ np.linalg.solve(C_XX, state_diff.T))
            J2 = J2 / np.max(J2)
            J = J1 + beta * J2
            bb = np.argsort(J)
            X_le_f = X_f[:, bb[:N_le]]
            Y_le_f = Y_f[:, bb[:N_le]]
            if flag == 'K':
                X_le_a = ES.update(X_le_f, Y_le_f, obs, sd, param_range, N_var1)
                selected = np.random.randint(0, N_le)
                X_a[:, i] = X_le_a[:, selected]
            if (i+1)%(N_e/2) == 0:
                print(f'Thread {out_iter}-{i+1}, ILUES has update{i+1}/{N_e}')
        return X_a