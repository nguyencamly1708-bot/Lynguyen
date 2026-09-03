import subprocess
import datetime
import os
import sys

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_git_sync(repo_dir=None, commit_msg=None):
    if not repo_dir:
        repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if not commit_msg:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto-sync update: {now_str}"

    print(f"[{datetime.datetime.now()}] Bắt đầu đồng bộ Git cho thư mục: {repo_dir}")

    try:
        # 1. Kiểm tra trạng thái git status
        status_res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        if not status_res.stdout.strip():
            print("Working tree clean. Không có thay đổi nào cần commit.")
            return True

        print(f"Phát hiện các thay đổi:\n{status_res.stdout.strip()}")

        # 2. Git add
        add_res = subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True, text=True)
        if add_res.returncode != 0:
            print(f"Lỗi git add: {add_res.stderr}")
            return False

        # 3. Git commit
        commit_res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_dir, capture_output=True, text=True)
        print(f"Git commit kết quả: {commit_res.stdout.strip()}")

        # 4. Git push
        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, capture_output=True, text=True)
        if push_res.returncode != 0:
            print(f"Cảnh báo/Lỗi git push:\n{push_res.stderr.strip()}")
            return False
        
        print("Đồng bộ GitHub THÀNH CÔNG!")
        return True

    except Exception as e:
        print(f"Lỗi ngoại lệ khi đồng bộ Git: {e}")
        return False

if __name__ == "__main__":
    success = run_git_sync()
    sys.exit(0 if success else 1)
