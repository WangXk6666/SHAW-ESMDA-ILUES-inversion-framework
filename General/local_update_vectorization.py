import numpy as np
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
try:
    import cupy as cp
    from cupy.linalg import inv as cp_inv
    from cupy.linalg import solve as cp_solve
    GPU_AVAILABLE = cp.cuda.runtime.getDeviceCount() > 0
    if GPU_AVAILABLE:
        gpu_device = cp.cuda.Device(0)
        gpu_device.use()
        total_mem = gpu_device.mem_info[1]
        free_mem = gpu_device.mem_info[0]
        logging.info(f"✅ GPU environment detected（cupy {cp.__version__}）")
        gpu_props = cp.cuda.runtime.getDeviceProperties(0)
        gpu_name = gpu_props['name'].decode('utf-8') if isinstance(gpu_props['name'], bytes) else gpu_props['name']
        logging.info(f"   GPU model：{gpu_name}")
        logging.info(f"   Total graphics memory：{total_mem / 1e9:.2f}GB | Available graphics memory：{free_mem / 1e9:.2f}GB")
    else:
        logging.info("⚠️ GPU not detected, will fallback to CPU computation")
except ImportError:
    cp = None
    cp_inv = None
    cp_solve = None
    GPU_AVAILABLE = False
    logging.info("⚠️ Cupy not installed, will be rolled back to CPU computing")

class LocalUpdate:
    @staticmethod
    def local_update(
            out_iter, X_f, Y_f, obs, sd, param_range, C_XX, C_Y, alpha=0.1, flag='K', beta=0.25, batch_size=2000, N_var1=100):
        dtype = np.float64
        xp = cp if GPU_AVAILABLE else np
        inv_func = cp_inv if GPU_AVAILABLE else np.linalg.inv
        solve_func = cp_solve if GPU_AVAILABLE else np.linalg.solve
        X_f = xp.atleast_2d(X_f).astype(dtype)
        Y_f = xp.atleast_2d(Y_f).astype(dtype)
        obs = xp.atleast_1d(obs).astype(dtype)
        N_param = X_f.shape[0]
        N_e = X_f.shape[1]
        N_obs = Y_f.shape[0]
        N_le = int(xp.ceil(N_e * alpha))
        param_range = xp.array(param_range, dtype=dtype)
        C_Y = xp.array(C_Y[:N_var1, :N_var1], dtype=dtype)
        Y_f = Y_f
        obs = obs
        C_XX = xp.array(C_XX, dtype=dtype)
        inv_CXX = inv_func(C_XX)
        if N_le < 2:
            logging.critical(f"The local set size N_le={N_le} must be ≥ 2 (covariance denominator is 0)")
        if flag != 'K':
            logging.critical("Only supports 'K' (Kalman update) mode")
        if GPU_AVAILABLE:
            def estimate_required_mem(batch_sz):
                mem_elements = (
                    N_param * N_le * batch_sz +
                    N_obs * N_le * batch_sz +
                    N_param * N_obs * batch_sz +
                    N_obs * N_obs * batch_sz
                )
                return int(mem_elements * 8 * 1.5)

            current_free_mem = gpu_device.mem_info[0]
            required_mem_full = estimate_required_mem(N_e)

            if current_free_mem >= required_mem_full:
                actual_batch_size = N_e
                logging.info(f"  ✅ GPU memory sufficient (available {current_free_mem / 1e9:.2f} GB "
                             f"≥ required {required_mem_full / 1e9:.2f} GB)")
                logging.info(f"  Enable full-batch update (actual_batch_size={actual_batch_size})")
            else:
                candidate_batch = min(batch_size, N_e)
                while candidate_batch >= 1:
                    required_mem_candidate = estimate_required_mem(candidate_batch)
                    if current_free_mem >= required_mem_candidate:
                        actual_batch_size = candidate_batch
                        logging.info(f"  ⚠️ GPU memory limited → use batch processing")
                        logging.info(f"     Available: {current_free_mem / 1e9:.2f} GB | "
                                     f"Required for batch={candidate_batch}: {required_mem_candidate / 1e9:.2f} GB")
                        logging.info(f"     Selected batch_size = {actual_batch_size}")
                        break
                    else:
                        candidate_batch //= 2
                else:
                    actual_batch_size = 1
                    logging.warning("  ❗ GPU memory extremely limited! Forced batch_size = 1")
        else:
            logging.info(f"  CPU mode: using batch_size={batch_size}")
            actual_batch_size = batch_size
        n_batches = (N_e + actual_batch_size - 1) // actual_batch_size
        X_f_T = X_f.T
        A = X_f_T @ inv_CXX @ X_f_T.T
        diag_A = xp.diag(A).reshape(-1, 1)
        J0 = diag_A + diag_A.T - 2 * A
        J0 = J0 / xp.max(J0) if xp.max(J0) != 0 else J0
        obs_diff = Y_f.T - obs.reshape(1, -1)
        J1 = xp.diag(obs_diff @ solve_func(C_Y, obs_diff.T))
        J1 = xp.expand_dims(J1 / xp.max(J1), 1) if xp.max(J1) != 0 else xp.expand_dims(J1, 1)
        J = (1 - beta) * J0 + beta * J1
        le_indices = xp.argsort(J, 1)[:, :N_le]
        X_le_as = xp.empty((N_param, N_le, N_e), dtype=dtype)
        logging.info(f"  Batch configuration：Total set number {N_e}，Actual batch size {actual_batch_size}，Total number of batches {n_batches}")

        for batch_idx in range(n_batches):
            batch_start = batch_idx * actual_batch_size
            batch_end = min((batch_idx + 1) * actual_batch_size, N_e)
            batch_len = batch_end - batch_start
            if n_batches > 1:
                logging.info(f"  Handling the {batch_idx + 1}/{n_batches} batch：[{batch_start}:{batch_end}]（{batch_len} members）")
            le_indices_slice = le_indices[batch_start:batch_end]
            X_le_fs_slice = X_f[:, le_indices_slice.T]
            Y_le_fs_slice = Y_f[:, le_indices_slice.T]
            X_le_as_slice = LocalUpdate._es_update(X_le_fs_slice, Y_le_fs_slice, obs, sd, param_range, xp=xp,
                                                   solve_func=solve_func, dtype=dtype)
            X_le_as[:, :, batch_start:batch_end] = X_le_as_slice

        selected_indices = xp.random.randint(0, N_le, size=N_e, dtype=xp.int32)
        X = X_le_as[xp.arange(N_param)[:, None], selected_indices, xp.arange(N_e)]
        if GPU_AVAILABLE and isinstance(X, cp.ndarray):
            X = cp.asnumpy(X)
        X_a = np.around(X, decimals=3)
        logging.info(f"The {out_iter} outer iterations - local update finish（X_a.shape: {X_a.shape} | float64 precision）")
        if GPU_AVAILABLE:
            cp.get_default_memory_pool().free_all_blocks()
            remaining_mem = gpu_device.mem_info[0]
            logging.info(f"  GPU memory cleared（remaining：{remaining_mem / 1e9:.2f}GB）")
        return X_a

    @staticmethod
    def _es_update(X_f_batch, Y_f_batch, obs, sd, param_range,xp, solve_func, dtype):
        sd = xp.asarray(sd, dtype)
        X_f_batch = xp.atleast_3d(X_f_batch).astype(dtype)
        Y_f_batch = xp.atleast_3d(Y_f_batch).astype(dtype)
        obs = xp.atleast_1d(obs).astype(dtype)
        N_param, N_le, batch_len = X_f_batch.shape
        N_obs = Y_f_batch.shape[0]
        mu_X_batch = xp.mean(X_f_batch, axis=1, keepdims=True)
        mu_Y_batch = xp.mean(Y_f_batch, axis=1, keepdims=True)
        X_res = X_f_batch - mu_X_batch
        Y_res = Y_f_batch - mu_Y_batch
        C_XY_batch = xp.einsum('ple,ole->pol', X_res, Y_res) / (N_le - 1)
        C_YY_batch = xp.einsum('ile,jle->ijl', Y_res, Y_res) / (N_le - 1)
        perturb = xp.random.normal(0, sd, Y_f_batch.shape).astype(dtype)
        obs_Y_res = (obs[:, None, None] + perturb) - Y_f_batch
        C_Y = xp.diag(xp.full(N_obs, sd ** 2, dtype=dtype))

        A = C_YY_batch + C_Y[..., None]
        K_T = solve_func(A.transpose(2, 0, 1), C_XY_batch.transpose(2, 1, 0))
        K = K_T.transpose(2, 1, 0)

        delta = xp.einsum('pol,ole->ple', K, obs_Y_res)

        X_a_batch = X_f_batch + delta
        lb = xp.broadcast_to(param_range[:, 0].reshape(-1, 1, 1), X_a_batch.shape)
        ub = xp.broadcast_to(param_range[:, 1].reshape(-1, 1, 1), X_a_batch.shape)
        X_a_batch = xp.where(X_a_batch < lb, (X_f_batch + lb) / 2, X_a_batch)
        X_a_batch = xp.where(X_a_batch > ub, (X_f_batch + ub) / 2, X_a_batch)
        return X_a_batch