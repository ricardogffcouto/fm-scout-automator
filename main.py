import shutil
import os
import pandas as pd
import numpy as np


INITIAL_FILTER_Y = 807
FILTER_OFFSET_Y = 30
NUM_FILTERS = 4

def dict_weight_parser(w_dict):
    weighted_dict = {}

    for k in w_dict.keys():
        for p in k.split(', '):
            weighted_dict[p] = w_dict[k]
    
    return weighted_dict

def activate_fm():
    window_id = os.popen("xdotool search --name 'Football Manager 2019 Touch'").read()
    os.system("xdotool key 'F2'")
    os.system('xdotool windowactivate %s' % (window_id) )
    os.system("xdotool sleep 0.5")


def sleep():
    os.system("xdotool sleep 0.5")


def move_click(x, y):
    os.system("xdotool mousemove %s %s click 1" % (x, y))
    sleep()


def extract_scouting(filter_id):
    # Select filter
    move_click(1836, 175)
    move_click(946, 667)
    move_click(946, INITIAL_FILTER_Y + filter_id * FILTER_OFFSET_Y)
    move_click(1058, 586)
    sleep()

    # Open print screen menu
    move_click(1647, 33)
    move_click(1647, 33)
    move_click(1647, 451)

    # Print to web page
    move_click(1041, 618)
    move_click(1161, 764)
    sleep()

    src_path = '/home/ricardo/.steam/steam/steamapps/compatdata/872820/pfx/drive_c/users/steamuser/My Documents/Sports Interactive/Football Manager 2019 Touch/Untitled.html'
    dst_path = './scouting1.html'
    shutil.move(src_path, dst_path)


def scout():
    activate_fm()
    for filter_id in range(NUM_FILTERS):
        extract_scouting(filter_id)


PERSONALITY_WEIGHTS = {
    'Model Citizen, Resolute, Model Professional, Driven, Iron Willed': 0.2,
    'Perfectionist, Professional, Fairly Professional, Spirited, Very Ambitious, Ambitious, Determined, Fairly Determined, Charismatic Leader, Born Leader, Leader, Resilient': 0.05,
    'Jovial, Light Hearted, Devoted / Very Loyal, Loyal, Fairly Loyal, Honest, Sporting, Fairly Sporting, Realist, Balanced, Fairly Ambitious, Light-Hearted': 0,
    'Unsporting, Slack, Casual, Temperamental, Unambitious, Easily Discouraged, Low Determination, Spineless, Low Self Belief, Mercenary, Fickle': -0.2,
}

ATTRIBUTE_CATEGORIES = {
    'Intel': ['Ant', 'Cmp', 'Cnt', 'Dec', 'OtB', 'Pos', 'Vis'],
    'Work': ['Agg', 'Bra', 'Det', 'Tea', 'Wor', 'Nat', 'Sta'],
    'Def': ['Agg', 'Ant', 'Bra', 'Cmp', 'Cnt', 'Det', 'Pos', 'Tea', 'Acc', 'Jum', 'Str'],
    'Atk': ['Tec', 'Ant', 'Cmp', 'OtB', 'Acc', 'Pac'],
    'Ginga': ['Dri', 'Tec', 'Fla', 'Acc', 'Agi', 'Pac']
}

FOOT_WEIGHTS = {
    'Very Strong': 1,
    'Strong': 0.8,
    'Fairly Strong': 0.6,
    'Reasonable': 0.4,
    'Weak': 0.2,
    'Very Weak': 0,
}

ALL_POSITIONS = ['GKC', 'DL', 'DR', 'DC', 'WBL', 'WBR', 'DMC', 'ML', 'MR', 'MC', 'AML', 'AMR', 'AMC', 'STC']

DECAY_OPP_FOOT = 3


def foot_to_num(foot):
    return FOOT_WEIGHTS[foot]


def load_shortlist():
    def position_to_str(pos):
        player_pos = []
        positions = pos.split(', ')

        for p in positions:
            p = p.split(' ')
            posits = p[0].split('/')

            sides = ['C']        
            if len(p) > 1:
                sides = list(p[1].replace('(','').replace(')',''))

            for posit in posits:
                if posit != '-':
                    for side in sides:
                        player_pos.append('%s%s' % (posit, side))

        return ', '.join(player_pos)

    PERSONALITIES = dict_weight_parser(PERSONALITY_WEIGHTS)


    def personality_to_num(per):
        return PERSONALITIES[per]


    def shortlist_apply_column(column, function):
        SHORTLIST[column] = SHORTLIST[column].apply(function)


    SHORTLIST = pd.read_html('scouting1.html', header=0)[0]

    # Transform data

    shortlist_apply_column('Left Foot', foot_to_num)
    shortlist_apply_column('Right Foot', foot_to_num)
    shortlist_apply_column('Position', position_to_str)
    shortlist_apply_column('Sec. Position', position_to_str)
    
    SHORTLIST['Pers. Factor'] = SHORTLIST['Personality'].apply(personality_to_num)

    # Adding scouting data

    SHORTLIST['Footedness'] = SHORTLIST['Right Foot'] - SHORTLIST['Left Foot']
    SHORTLIST['Youth Factor'] = np.minimum(np.maximum(1 - (SHORTLIST['Age'] - 23) / 20, 0), 1)

    for category in ATTRIBUTE_CATEGORIES.keys():
        SHORTLIST[category] = SHORTLIST[ATTRIBUTE_CATEGORIES[category]].sum(axis=1) / len(ATTRIBUTE_CATEGORIES[category])


    return SHORTLIST


def positional_footedness(player_footedness, position_footedness, two_foot_bonus, decay_opp_foot):
    player_two_foot_bonus = (1 - abs(player_footedness)) * two_foot_bonus
    player_decay_opp_foot = np.minimum(player_footedness * position_footedness, 0) * decay_opp_foot
    return player_two_foot_bonus + player_decay_opp_foot


def influence(teamwork, leadership, personality, position_influence_weight):
    return 1 + ((teamwork + leadership) / (20 * 2)) * personality * position_influence_weight


def scouting_report(shortlist, positions = [], youth_bonus = 1, player_amount = 20):
    pos_weights = pd.read_excel('PosWeights.ods', engine='odf')

    shortlist['Main Pos.'] = shortlist['Position'].apply(lambda pos: pos.split(', ')[0])

    for position in positions:
        weights = pos_weights.loc[lambda df: (df['Pos+Side'] == position), :]
        attributes = shortlist.columns.intersection(weights.columns)

        relative_weights = weights[attributes].div(weights[attributes].sum(axis=1), axis=0)

        position_shortlist = shortlist.loc[shortlist['Position'].str.contains(position) | shortlist['Sec. Position'].str.contains(position)]
        
        position_shortlist = position_shortlist.copy()
        
        scouting_shortlist = position_shortlist.copy()

        position_shortlist[attributes] = position_shortlist[attributes].mul(np.array(relative_weights), axis='columns', fill_value=0)

        scouting_shortlist['POSITIONAL DNA'] = (position_shortlist[attributes].sum(axis=1)) * 5 

        scouting_shortlist['FOOT DNA'] = positional_footedness(
            position_shortlist['Footedness'],
            weights['Pos Footedness'].iloc[0],
            weights['Two Foot Bonus'].iloc[0],
            DECAY_OPP_FOOT,
        )

        scouting_shortlist['YOUTH DNA'] = (position_shortlist['Youth Factor'] * youth_bonus - 1)

        scouting_shortlist['INFLUENCE'] = influence(
            position_shortlist['Tea'],
            position_shortlist['Ldr'],
            position_shortlist['Pers. Factor'],
            weights['Influence Weight'].iloc[0],
        )

        scouting_shortlist['TOTAL'] = ((scouting_shortlist['POSITIONAL DNA'] + scouting_shortlist['FOOT DNA'] + scouting_shortlist['YOUTH DNA']) * scouting_shortlist['INFLUENCE'])

        info_columns = ['Name','Position','Sec. Position','Age']
        attribute_columns = list(ATTRIBUTE_CATEGORIES.keys())
        personality_columns = ['Personality', 'Pers. Factor']
        dna_columns = ['POSITIONAL DNA','FOOT DNA','YOUTH DNA', 'TOTAL']

        scouting_columns = info_columns + attribute_columns + personality_columns + dna_columns

        scouting_shortlist[attribute_columns] = scouting_shortlist[attribute_columns].applymap(lambda x: "{0:.0f}".format(x*5))
        scouting_shortlist[dna_columns] = scouting_shortlist[dna_columns].applymap(lambda x: "{0:.2f}%".format(x))

    return scouting_shortlist[scouting_columns].sort_values('TOTAL', ascending=False).head(player_amount)

print(scouting_report(load_shortlist(), positions=['DL']))