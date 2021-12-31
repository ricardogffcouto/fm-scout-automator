#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  5 08:16:02 2021

@author: ricardo
"""

import pandas as pd

df = pd.read_csv('~/coding/data-science/fm-ocr/personalities.txt', sep='/n', header=None)

df = df[0].str.split(';', expand=True)

pers = ['Amb', 'Loy', 'Pre', 'Pro', 'Spo', 'Tem', 'Con']

pers_min_max = [['Min %s' % (p), 'Max %s' % (p)] for p in pers]

pers_min_max = [pmm for pmm in sum(pers_min_max, [])]

pers_df = pd.DataFrame(columns = ['Name'] + pers_min_max)

pers_df['Name'] = df[0]

    
for pers_index in range(df.shape[0]):

    attribute_series = df.iloc[pers_index].tail(df.iloc[pers_index].shape[0] - 1)
    curr_attr = attribute_series.loc[attribute_series.str.contains('|'.join(pers), na=False)]
    curr_attr = curr_attr.str.split(', ', expand=True)
    
    attr_df = curr_attr.apply(lambda x: x.str.split(' ').explode()).reset_index(drop=True).apply(lambda x: x.str.split('-').explode()).reset_index(drop=True)
    attr_df.rename(columns=attr_df.iloc[0], inplace = True)
    attr_df.drop(df.index[0], inplace=True)
    
    for col in attr_df.columns:
        pers_df.iloc[pers_index]['Min %s' % col] = attr_df[col].iloc[0]
        pers_df.iloc[pers_index]['Max %s' % col] = attr_df[col].iloc[1]
            

media = [
  "Out, Unf",
  "Out, ST, Con",
  "Out, ST",
  "Out, Vol, Con",
  "Out, Vol",
  "Out, Con",
  "Out",
  "Eva, Unf",
  "Eva, ST, Con",
  "Eva, ST",
  "Eva, Vol, Con",
  "Eva, Vol",
  "Eva, Con",
  "Eva, Res",
  "Eva",
  "Unf",
  "ST, Con",
  "ST",
  "Vol, Con",
  "Vol",
  "Con",
  "Res",
  "LH",
  "MF, Unf",
  "MF, ST, Con",
  "MF, ST",
  "MF, Vol, Con",
  "MF, Vol",
  "MF, Con",
  "MF"
]

