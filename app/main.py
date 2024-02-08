import subprocess
import sys
import tempfile
import os
import shutil
# foreign function library
import ctypes


def main():
    command = sys.argv[3]
    args = sys.argv[4:]

    temp_path = tempfile.mkdtemp()
    shutil.copy2(command, temp_path)
    os.chroot(temp_path)

    isolated_command = os.path.join("/", os.path.basename(command))

    # man pid_namespaces
    # loading the standard C library (libc.so.6)
    # man libc. libc is just glibc
    # man 2 unshare
    libc = ctypes.cdll.LoadLibrary("libc.so.6")
    # define CLONE_NEWPID	0x20000000	/* New pid namespace.  */
    # sched.h
    libc.unshare(0x20000000)

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
