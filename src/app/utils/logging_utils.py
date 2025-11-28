import os
import sys
import time
import datetime

class Tee(object):
    """Tee class for redirecting output to multiple streams"""
    def __init__(self, *files):
        self.files = files
    
    def write(self, obj):
        for f in self.files:
            try:
                # 确保所有输出都使用 UTF-8 编码
                if isinstance(obj, str):
                    # 如果文件是文本模式但编码不匹配，尝试编码转换
                    if hasattr(f, 'encoding') and f.encoding:
                        try:
                            f.write(obj)
                        except UnicodeEncodeError:
                            # 如果编码失败，使用 errors='replace' 处理
                            encoded = obj.encode(f.encoding, errors='replace').decode(f.encoding)
                            f.write(encoded)
                    else:
                        f.write(obj)
                else:
                    f.write(obj)
                f.flush()
            except (UnicodeEncodeError, AttributeError) as e:
                # 如果仍然失败，尝试替换无法编码的字符
                try:
                    if isinstance(obj, str):
                        safe_obj = obj.encode('utf-8', errors='replace').decode('utf-8')
                        f.write(safe_obj)
                        f.flush()
                except Exception:
                    # 最后的后备方案：跳过无法编码的字符
                    pass
    
    def flush(self):
        for f in self.files:
            f.flush()

def setup_logging(args):
    """Setup logging redirection if --log flag is provided"""
    if hasattr(args, 'log') and args.log:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"console_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        log_f = open(log_file, "w", encoding="utf-8")
        sys.stdout = Tee(sys.stdout, log_f)
        sys.stderr = Tee(sys.stderr, log_f)
        print(f"Log redirected to: {log_file}")
        start_time = time.time()
        return log_file, start_time
    else:
        return None, time.time()

def finalize_logging(log_file, start_time, interrupted=False):
    """Write final runtime information to log file"""
    if log_file:
        try:
            end_time = time.time()
            duration = end_time - start_time
            with open(log_file, "a", encoding="utf-8") as f:
                if interrupted:
                    f.write("\nUser interrupted and exited\n")
                f.write(f"\nTotal runtime: {duration:.2f} seconds\n")
        except Exception as e:
            print(f"Failed to write runtime to log file: {e}") 