import pandas as pd
import numpy as np
import webbrowser
import glob
import os
import globals as GLOB
from scipy.stats.mstats import gmean


def dict_weight_parser(w_dict):
    weighted_dict = {}

    for k in w_dict.keys():
        for p in k.split(', '):
            weighted_dict[p] = w_dict[k]
    
    return weighted_dict


def foot_to_num(foot):
    if not pd.isna(foot):
        return GLOB.FOOT_WEIGHTS[foot]
    return 0


def position_to_str(pos):
    if not pd.isna(pos):
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

personalities = dict_weight_parser(GLOB.PERSONALITY_WEIGHTS)
media_handlings = dict_weight_parser(GLOB.MEDIA_HANDLING_WEIGHTS)

def personality_to_num(per):
    if not pd.isna(per) and per in personalities:
        return personalities[per]
    return 0

def media_handling_to_num(mh):
    if not pd.isna(mh) and mh in media_handlings:
        return media_handlings[mh]
    return 0


def get_shortlist():
    def shortlist_apply_column(shortlist, column, function):
        shortlist[column] = shortlist[column].apply(function)

    shortlist_names = glob.glob(os.path.join(GLOB.MAIN_PATH, 'shortlists/*'))

    all_shortlists = []

    for shortlist_name in shortlist_names:
        shortlist = pd.read_html(shortlist_name, header=0)[0]

        # Transform data

        shortlist_apply_column(shortlist, 'Left Foot', foot_to_num)
        shortlist_apply_column(shortlist, 'Right Foot', foot_to_num)
        shortlist_apply_column(shortlist, 'Position', position_to_str)
        shortlist_apply_column(shortlist, 'Sec. Position', position_to_str)
        
        shortlist['Pers. Factor'] = shortlist['Personality'].apply(personality_to_num) + shortlist['Media Handling'].apply(media_handling_to_num)

        # Adding scouting data

        shortlist['Footedness'] = shortlist['Right Foot'] - shortlist['Left Foot']
        shortlist['Youth Factor'] = np.minimum(np.maximum(1 - (shortlist['Age'] - 16) / 20, 0), 1)

        for category in GLOB.ATTRIBUTE_CATEGORIES.keys():
            shortlist[category] = shortlist[GLOB.ATTRIBUTE_CATEGORIES[category]].sum(axis=1) / len(GLOB.ATTRIBUTE_CATEGORIES[category])

        all_shortlists.append(shortlist)

    shortlist = pd.concat(all_shortlists)

    return shortlist.drop_duplicates(subset=['UID'] )


def positional_footedness(player_footedness, position_footedness, two_foot_bonus, decay_opp_foot):
    player_two_foot_bonus = (1 - abs(player_footedness)) * two_foot_bonus
    player_decay_opp_foot = np.minimum(player_footedness * position_footedness, 0) * decay_opp_foot
    return player_two_foot_bonus + player_decay_opp_foot


def influence(teamwork, leadership, personality, position_influence_weight):
    return personality * position_influence_weight

def potential(total, youth_factor, personality_factor):
    if youth_factor <= 0.7:
        return total + personality_factor * 4
    return 0



def youth_dna(relative_youth, youth_bonus):
    youth_steps = [0.7, 0.35]
    if relative_youth <= youth_steps[0]:
        return 1 + (relative_youth - youth_steps[0]) * youth_bonus
    if relative_youth <= youth_steps[1]:
        return (relative_youth - youth_steps[1]) / (youth_steps[0] - youth_steps[1])
    return (relative_youth - youth_steps[1]) * youth_bonus


def scouting_report(shortlist, positions = GLOB.ALL_POSITIONS, youth_bonus = GLOB.YOUTH_BONUS):
    pos_weights = pd.read_excel(os.path.join(GLOB.MAIN_PATH, 'data', 'PosWeights.ods'), engine='odf')

    scouting_reports = []

    for position in positions:
        weights = pos_weights.loc[lambda df: (df['Pos+Side'] == position), :]
        attributes = shortlist.columns.intersection(weights.columns)

        relative_weights = weights[attributes].div(weights[attributes].sum(axis=1), axis=0)

        position_shortlist = shortlist.loc[shortlist['Position'].str.contains(position) | shortlist['Sec. Position'].str.contains(position)]
        
        if len(position_shortlist) > 0:

            position_shortlist = position_shortlist.copy()
            
            scouting_shortlist = position_shortlist.copy()
            
            scouting_shortlist['GMEAN DNA'] = (gmean(1 + position_shortlist[attributes], axis=1, weights=weights[attributes].iloc[0].fillna(0)) - 1) * 5

            scouting_shortlist['WEIGHTED DNA'] = position_shortlist[attributes].mul(np.array(relative_weights), axis='columns', fill_value=0).sum(axis=1) * 5

            scouting_shortlist['POSITIONAL DNA'] = scouting_shortlist['GMEAN DNA'] * (1 - GLOB.IMPORTANCE_WEIGHTED) + scouting_shortlist['WEIGHTED DNA'] * GLOB.IMPORTANCE_WEIGHTED
            
            scouting_shortlist['FOOT DNA'] = positional_footedness(
                position_shortlist['Footedness'],
                weights['Pos Footedness'].iloc[0],
                weights['Two Foot Bonus'].iloc[0],
                GLOB.DECAY_OPP_FOOT,
            )

            scouting_shortlist['YOUTH DNA'] = position_shortlist['Youth Factor'].apply(lambda x: youth_dna(x, youth_bonus))

            scouting_shortlist['INFLUENCE'] = influence(
                position_shortlist['Tea'],
                position_shortlist['Ldr'],
                position_shortlist['Pers. Factor'],
                weights['Influence Weight'].iloc[0],
            )

            scouting_shortlist['TOTAL'] = scouting_shortlist['POSITIONAL DNA'] + scouting_shortlist['FOOT DNA'] + scouting_shortlist['YOUTH DNA'] + scouting_shortlist['INFLUENCE']

            scouting_shortlist['POTENTIAL'] = scouting_shortlist['TOTAL'] + (scouting_shortlist['Pers. Factor'] * 4)

            info_columns = ['Name','TOTAL', 'TOTAL FOR POS', 'Age']
            attribute_columns = list(GLOB.ATTRIBUTE_CATEGORIES.keys())
            personality_columns = ['Personality']
            dna_columns = ['POSITIONAL DNA', 'POTENTIAL', 'INFLUENCE', 'FOOT DNA','YOUTH DNA']

            scouting_columns = info_columns + personality_columns + attribute_columns + dna_columns

            scouting_shortlist[attribute_columns] = scouting_shortlist[attribute_columns].applymap(lambda x: "{0:.0f}".format(x*5))
            scouting_shortlist[dna_columns + ['TOTAL']] = scouting_shortlist[dna_columns + ['TOTAL']].applymap(lambda x: "{0:.2f}%".format(x))
            scouting_shortlist['TOTAL FOR POS'] = position

            scouting_reports.append(scouting_shortlist)

    report = pd.concat(scouting_reports)

    return report[scouting_columns]


def view_report(report):
    id = 'position'
    report_path = os.path.join(GLOB.MAIN_PATH, 'scouting_report.html')

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
                        order: [[ 2, "desc" ]],
                        iDisplayLength: 10,
                        initComplete: function () {
                            console.log(this.api().columns())
                            this.api().column(3).every( function () {
                                var column = this;
                                var select = $('<select><option value=""></option></select>')
                                    .appendTo( $(column.header()).empty() )
                                    .on( 'change', function () {
                                        var val = $.fn.dataTable.util.escapeRegex(
                                            $(this).val()
                                        );
                
                                        column
                                            .search( val ? '^'+val+'$' : '', true, false )
                                            .draw();
                                    } );
                
                                column.data().unique().sort().each( function ( d, j ) {
                                    select.append( '<option value="'+d+'">'+d+'</option>' )
                                } );
                            } );
                        }
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