import pandas as pd
import numpy as np
import webbrowser
import glob
import os


MAIN_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

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

# ALL_POSITIONS = ['GKC', 'DL', 'DR', 'DC', 'WBL', 'WBR', 'DMC', 'ML', 'MR', 'MC', 'AML', 'AMR', 'AMC', 'STC']

ALL_POSITIONS = ['GKC', 'DL', 'DR', 'DC', 'DMC', 'ML', 'MR', 'MC', 'AMC', 'STC']

DECAY_OPP_FOOT = 3

def dict_weight_parser(w_dict):
    weighted_dict = {}

    for k in w_dict.keys():
        for p in k.split(', '):
            weighted_dict[p] = w_dict[k]
    
    return weighted_dict

PERSONALITIES = dict_weight_parser(PERSONALITY_WEIGHTS)


def foot_to_num(foot):
    return FOOT_WEIGHTS[foot]


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


def personality_to_num(per):
    return PERSONALITIES[per]


def get_shortlist():
    def shortlist_apply_column(shortlist, column, function):
        shortlist[column] = shortlist[column].apply(function)

    shortlist_names = glob.glob(os.path.join(MAIN_PATH, 'shortlists/*'))

    all_shortlists = []

    for shortlist_name in shortlist_names:
        shortlist = pd.read_html(shortlist_name, header=0)[0]

        # Transform data

        shortlist_apply_column(shortlist, 'Left Foot', foot_to_num)
        shortlist_apply_column(shortlist, 'Right Foot', foot_to_num)
        shortlist_apply_column(shortlist, 'Position', position_to_str)
        shortlist_apply_column(shortlist, 'Sec. Position', position_to_str)
        
        shortlist['Pers. Factor'] = shortlist['Personality'].apply(personality_to_num)

        # Adding scouting data

        shortlist['Footedness'] = shortlist['Right Foot'] - shortlist['Left Foot']
        shortlist['Youth Factor'] = np.minimum(np.maximum(1 - (shortlist['Age'] - 23) / 20, 0), 1)

        for category in ATTRIBUTE_CATEGORIES.keys():
            shortlist[category] = shortlist[ATTRIBUTE_CATEGORIES[category]].sum(axis=1) / len(ATTRIBUTE_CATEGORIES[category])

        all_shortlists.append(shortlist)

    shortlist = pd.concat(all_shortlists)

    return shortlist


def positional_footedness(player_footedness, position_footedness, two_foot_bonus, decay_opp_foot):
    player_two_foot_bonus = (1 - abs(player_footedness)) * two_foot_bonus
    player_decay_opp_foot = np.minimum(player_footedness * position_footedness, 0) * decay_opp_foot
    return player_two_foot_bonus + player_decay_opp_foot


def influence(teamwork, leadership, personality, position_influence_weight):
    return 1 + ((teamwork + leadership) / (20 * 2)) * personality * position_influence_weight


def scouting_report(shortlist, positions = ALL_POSITIONS, youth_bonus = 1, player_amount = 20):
    pos_weights = pd.read_excel(os.path.join(MAIN_PATH, 'data', 'PosWeights.ods'), engine='odf')

    scouting_reports = []

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

        info_columns = ['Name','TOTAL', 'TOTAL FOR POS', 'Age']
        attribute_columns = list(ATTRIBUTE_CATEGORIES.keys())
        personality_columns = ['Personality', 'Pers. Factor']
        dna_columns = ['POSITIONAL DNA','FOOT DNA','YOUTH DNA']

        scouting_columns = info_columns + personality_columns + attribute_columns + dna_columns

        scouting_shortlist[attribute_columns] = scouting_shortlist[attribute_columns].applymap(lambda x: "{0:.0f}".format(x*5))
        scouting_shortlist[dna_columns + ['TOTAL']] = scouting_shortlist[dna_columns + ['TOTAL']].applymap(lambda x: "{0:.2f}%".format(x))
        scouting_shortlist['TOTAL FOR POS'] = position

        scouting_reports.append(scouting_shortlist)

    report = pd.concat(scouting_reports)

    return report[scouting_columns]


def view_report(report):
    id = 'position'
    report_path = os.path.join(MAIN_PATH, 'scouting_report.html')

    header = '''
        <head>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.0/css/jquery.dataTables.css"/>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/fixedheader/3.1.9/css/fixedHeader.dataTables.css"/>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/searchpanes/1.4.0/css/searchPanes.dataTables.css"/>
            
            <script type="text/javascript" src="https://code.jquery.com/jquery-3.3.1.js"></script>
            <script type="text/javascript" src="https://cdn.datatables.net/1.11.0/js/jquery.dataTables.js"></script>
            <script type="text/javascript" src="https://cdn.datatables.net/fixedheader/3.1.9/js/dataTables.fixedHeader.js"></script>
            <script type="text/javascript" src="https://cdn.datatables.net/searchpanes/1.4.0/js/dataTables.searchPanes.js"></script>

            <script>
                $(document).ready( function () {
                    $('#%s').DataTable({
                        "order": [[ 2, "desc" ]],
                        "iDisplayLength": 10
                    });
                } );
            </script>


        </head>
    ''' % (id,)
    
    body = '''
        <body>
    ''' + report.to_html(table_id=id, classes='display')

    style = '''
    <style>
        body {
            font-family: 'Arial';
        }
    </style>
    '''

    close_body =  '''
        </body>
    '''

    html_report = header + body + style + close_body

    report_file = open(report_path, "w")
    report_file.write(html_report)
    report_file.close()

    webbrowser.open(report_path, new=2)

if __name__ == '__main__':
    shortlist = get_shortlist()
    report = scouting_report(shortlist)
    view_report(report)