import subprocess

def main():
    cmd = "nohup python CPULoadGen.py"
    process = subprocess.Popen(cmd, shell=True)
main()
