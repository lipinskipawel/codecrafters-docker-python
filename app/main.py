import subprocess
import sys
import tempfile
import os
import shutil


def main():
    command = sys.argv[3]
    args = sys.argv[4:]

    temp_path = tempfile.mkdtemp()
    shutil.copy2(command, temp_path)
    os.chroot(temp_path)

    isolated_command = os.path.join("/", os.path.basename(command))

    completed_process = subprocess.Popen(
        [isolated_command, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    stdout, stderr = completed_process.communicate()
    if stdout:
        print(stdout.decode("utf-8"), end="")
    if stderr:
        print(stderr.decode("utf-8"), file=sys.stderr, end="")

    sys.exit(completed_process.returncode)

if __name__ == "__main__":
    main()
