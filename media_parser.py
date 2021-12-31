#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

HIDDEN = ['Amb', 'Loy', 'Pre', 'Pro', 'Spo', 'Tem', 'Con']

player_hidden = pd.DataFrame(
    index=HIDDEN
)

def parser(df, attr, order):
    df = df[0].str.split(';', expand=True)
    cols = len(df.columns)
    
    df.columns = ['Name', 'Hidden'] + ['Other {}'.format(i+1) for i in range(cols - 2)]

    col = df.loc[df['Name'] == attr]
    pers = col['Hidden'].str.split(', ', expand=True).T
            
    pers = pers.iloc[:,0].str.split(' ', expand=True)
    pers = pers.set_index(0)
    pers = pers.iloc[:,0].str.split('-', expand=True)

    pers.columns = ['Min %s' % (order,), 'Max %s' % (order,)]
    
    return pers


# Player media and personality

player_media = 'Out'

player_pers = 'Resolute'

# Parsing

media_df = pd.read_csv('./data/media.csv', sep='/n', header=None)

pers_df = pd.read_csv('./data/personalities.csv', sep='/n', header=None)

media_hidden = parser(media_df, player_media, 1)

pers_hidden = parser(pers_df, player_pers, 2)

player_hidden = pd.concat([player_hidden, media_hidden, pers_hidden], axis=1)

player_hidden.fillna(-1, inplace=True)

player_hidden = player_hidden.astype(int)

player_hidden['Min'] = player_hidden[player_hidden[['Min 1', 'Min 2']] > 0].max(axis=1)

player_hidden['Max'] = player_hidden[player_hidden[['Max 1', 'Max 2']] > 0].min(axis=1)

