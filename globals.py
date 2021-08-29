import os

MAIN_PATH = os.path.abspath((os.path.dirname( __file__ )))
FM_PATH = '/home/ricardo/.steam/steam/steamapps/compatdata/872820/pfx/drive_c/users/steamuser/My Documents/Sports Interactive/Football Manager 2019 Touch/Untitled.html'

PERSONALITY_WEIGHTS = {
    'Model Citizen': 2, 
    'Resolute, Model Professional, Driven, Iron Willed': 1,
    'Perfectionist, Professional, Fairly Professional, Spirited, Very Ambitious, Ambitious, Determined, Fairly Determined, Charismatic Leader, Born Leader, Leader, Resilient': 0.25,
    'Jovial, Light Hearted, Devoted / Very Loyal, Loyal, Fairly Loyal, Honest, Sporting, Fairly Sporting, Realist, Balanced, Fairly Ambitious, Light-Hearted': 0,
    'Unsporting, Slack, Casual, Temperamental, Unambitious, Easily Discouraged, Low Determination, Spineless, Low Self Belief, Mercenary, Fickle': -1.75,
}

ATTRIBUTE_CATEGORIES = {
    'Intel': ['Ant', 'Dec', 'Tea', 'Vis'],
    'Focus': ['Cmp', 'Cnt'],
    'Endea': ['Agg', 'Bra', 'Det', 'Wor'],
    'Physi': ['Bal', 'Str', 'Jum'],
    'Mobil': ['Acc', 'Agi', 'Pac'],
    'Ctrl': ['Fir', 'Tec', 'Cmp'],
    'Fit': ['Nat', 'Sta'],
    'Infl': ['Tea', 'Ldr'],
    'FK': ['Fre'],
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

YOUTH_BONUS = 1