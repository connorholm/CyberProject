from multiprocessing import Pool
from multiprocessing import cpu_count
import math

def f(x):
    while True:
        x * math.factorial(1000000)

def main():
    while True:
        processes = cpu_count()
        pool = Pool(processes)
        pool.map(f, range(processes))
main()
