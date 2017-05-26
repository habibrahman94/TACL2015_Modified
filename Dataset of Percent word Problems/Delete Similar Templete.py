#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 26 21:12:53 2017

@author: habib
"""
vis=[]
for i in range(310):
    vis.append(0)
Res = open("Final/RevisedDataset.txt",'w')
Dup = open("Final/Rejected.txt", 'w')
for i in range(309):
    if vis[i+1]==0:
        Fi = open("Data/q"+str(i+1)+".txt", 'r')
        lin1 = next(Fi)
        for j in range(309):
            if vis[j]==0 and j!=i:
                Fj = open("Data/q"+str(j+1)+".txt", 'r') 
                lin2 = next(Fj)
                mn = min(len(lin1), len(lin2))
                dif = max(len(lin1),len(lin2)) - mn
                for k in range(mn):
                    if lin1[k]!=lin2[k]:
                        dif+=1
                tot = (len(lin1)+len(lin2))/2.0
                pr = (dif/tot)*100.00
                if pr<10.00:
                    Dup.write(lin1)
                    Dup.write(lin2)
                    Dup.write("\n")
                    vis[j]=1
                Fj.close()
        Res.write(lin1)
        vis[i]=1
        Fi.close()
Dup.close()
Res.close()
