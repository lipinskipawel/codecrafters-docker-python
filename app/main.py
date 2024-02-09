import subprocess
import sys
import tempfile
import os
import shutil
# foreign function library
import ctypes
import urllib.request
import json
import tarfile


def main():
    image = sys.argv[2]
    command = sys.argv[3]
    args = sys.argv[4:]
    image_version = "latest"
    image_name = image
    if ":" in image:
        image_name, image_version = image.split(":")

    token_url = "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/" + image_name + ":pull"

    res = urllib.request.urlopen(token_url)
    res_json = json.loads(res.read().decode())
    token = res_json["token"]


    manifest_url = "https://registry.hub.docker.com/v2/library/" + image_name + "/manifests/" + image_version

    request = urllib.request.Request(
        manifest_url,
        headers={
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
            "Authorization": "Bearer " + token,
        },
    )
    res = urllib.request.urlopen(request)
    res_json = json.loads(res.read().decode())
    layers = res_json["layers"]

    temp_path = tempfile.mkdtemp()

    for layer in layers:
        request = urllib.request.Request(
            "https://registry.hub.docker.com/v2/library/"
            + image_name
            + "/blobs/"
            + layer["digest"],
            headers={"Authorization": "Bearer " + token},
        )
        res = urllib.request.urlopen(request)
        tmp_file = os.path.join(temp_path, "file.tar")
        with open(tmp_file, "wb") as f:
            shutil.copyfileobj(res, f)
        with tarfile.open(tmp_file) as tar:
            tar.extractall(temp_path)
        os.remove(tmp_file)

    # man pid_namespaces
    # loading the standard C library (libc.so.6)
    # man libc. libc is just glibc
    # man 2 unshare
    libc = ctypes.cdll.LoadLibrary("libc.so.6")
    # define CLONE_NEWPID	0x20000000	/* New pid namespace.  */
    # sched.h
    libc.unshare(0x20000000)

    os.chroot(temp_path)

    completed_process = subprocess.Popen(
        [command, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    stdout, stderr = completed_process.communicate()
    if stdout:
        print(stdout.decode("utf-8"), end="")
    if stderr:
        print(stderr.decode("utf-8"), file=sys.stderr, end="")

    sys.exit(completed_process.returncode)

if __name__ == "__main__":
    main()
