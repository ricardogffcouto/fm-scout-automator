#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import itertools


HIDDEN = [
    ['Amb', 1, -1], 
    ['Loy', 1, 1],
    ['Pre', 2.5, 1], 
    ['Pro', 4, 1],
    ['Spo', 0.5, 1],
    ['Tem', 1.5, 1],
    ['Con', 2, -1],
    ['Det', 0.5, 1],
    ['Inf', 0.5, 1]
]

SUM_WEIGHTS = np.add.reduce(list(map(lambda x: x[1], HIDDEN)))

MEDIA_DF = pd.read_csv('./data/media.csv', sep='/n', header=None)

PERS_DF = pd.read_csv('./data/personalities.csv', sep='/n', header=None)


def _parser(df, attr, order):
    df = df[0].str.split(';', expand=True)
    cols = len(df.columns)
    
    df.columns = ['Name', 'Hidden'] + ['Other {}'.format(i+1) for i in range(cols - 2)]
    
    attr_variations = itertools.permutations(attr.split(', '), len(attr.split(', ')))
    
    for var in attr_variations:
        attr = ', '.join(var)
        if attr in df['Name'].values:
            col = df.loc[df['Name'] == attr]
            break
        
    pers = col['Hidden'].str.split(', ', expand=True).T
                
    pers = pers.iloc[:,0].str.split(' ', expand=True)
    pers = pers.set_index(0)
    pers = pers.iloc[:,0].str.split('-', expand=True)

    pers.columns = ['Min %s' % (order,), 'Max %s' % (order,)]
    
    return pers


def _hidden(player_media, player_pers):
    player_hidden = pd.DataFrame(
        index=list(map(lambda x: x[0], HIDDEN))
    )
    
    media_hidden = _parser(MEDIA_DF, player_media, 1)

    pers_hidden = _parser(PERS_DF, player_pers, 2)

    player_hidden = pd.concat([player_hidden, media_hidden, pers_hidden], axis=1)

    player_hidden.fillna(-1, inplace=True)
    
    player_hidden = player_hidden.astype('int64')

    player_hidden['Min'] = player_hidden[player_hidden[['Min 1', 'Min 2']] > 0].max(axis=1)

    player_hidden['Max'] = player_hidden[player_hidden[['Max 1', 'Max 2']] > 0].min(axis=1)

    return player_hidden

def normalize(value, min_val, max_val, min_new, max_new):
    return (max_new-min_new)/(max_val-min_val)*(value-min_val)+min_new

def rate(player_media, player_pers):
    MAX_MIN_INFLUENCE = 0.35
    MIN_RATING = 0.25
    
    if (pd.isna(player_media) or pd.isna(player_pers)):
        return MAX_MIN_INFLUENCE 
    
    p = _hidden(player_media, player_pers)
    
    p = p.T
    
    rating = 0
    uncertainty = 0
    
    for h in HIDDEN:
        order = ['Min', 'Max']
        
        rate = 0
        
        if (h[2] < 0):
            order.reverse()
            
        if (np.isnan(p[h[0]][order[0]])):
            uncertainty += h[1]
        else:
            rate = p[h[0]][order[0]]
            
        if (np.isnan(p[h[0]][order[1]])):
            uncertainty += MAX_MIN_INFLUENCE * 0.5 * h[1]
        else:
            rate += h[2] * MAX_MIN_INFLUENCE * p[h[0]][order[1]]
        
        rating += rate * h[1]
        
    return normalize(rating - (20 * uncertainty), 0, 20 * SUM_WEIGHTS, MIN_RATING, 1)