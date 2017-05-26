#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 26 20:59:20 2017

@author: habib
"""
fileToRead = open("PercentDataset.txt",'r')
fileToSave = 'Data/q'
Cnt=1
for line in fileToRead:
    print(repr(Cnt)+" : " + line )
    F = open(fileToSave+str(Cnt)+'.txt', 'w')
    F.write(line)
    F.close()
    Cnt+=1
fileToRead.close()

