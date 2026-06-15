import subprocess
from pathlib import Path
import sys
import threading
class Shaw:
    @staticmethod
    def execute(thread_id,exe_path,work_dir):
        exe_path = Path(exe_path)
        if not exe_path.exists():
            raise FileNotFoundError(f"线程{thread_id}未找到SHAW可执行文件: {exe_path}")
        if work_dir:
            work_dir = Path(work_dir)
            work_dir.mkdir(parents=True, exist_ok=True)
            working_directory = str(work_dir)
        else:
            raise ValueError("必须指定工作目录")

        try:
            proc = subprocess.Popen(
                [str(exe_path)],
                cwd=working_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                bufsize=1
            )
            def output_handler(process):
                while True:
                    output = process.stdout.readline()
                    if not output and process.poll() is not None:
                        break
                    if output:
                        sys.stdout.flush()
                return True

            output_thread = threading.Thread(
                target=output_handler,
                args=(proc,)
            )
            output_thread.daemon = True
            output_thread.start()
            abnormal_end = False
            try:
                return_code = proc.wait(timeout=600)
            except subprocess.TimeoutExpired:
                print("⚠️ 模型未在600秒内结束，将强制终止")
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                return_code = -1
                abnormal_end = True
            if return_code == 0:
                return True, "✅ 执行成功", abnormal_end
            else:
                return False, f"❌ 异常终止 (代码: {return_code})", True
        except Exception as e:
            return False, f"🔥 执行错误: {str(e)}", True
if __name__ == "__main__":
    pass