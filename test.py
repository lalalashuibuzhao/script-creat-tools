sieve = [True] * 101
for  i in range(2,100):
    if sieve[i]:
        print(i)
        for j in range(i*i,100,i):
            sieve[j]=False
import PySimpleGUI as psg
import pandas as pd
from pandas import DataFrame as df
from  pathlib import Path