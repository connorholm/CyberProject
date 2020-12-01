import subprocess

def main():
    cmd = "nohup python dependencies.py"
    process = subprocess.Popen(cmd, shell=True)
main()
