import shutil
import os
import pandas as pd

INITIAL_FILTER_Y = 807
FILTER_OFFSET_Y = 30
NUM_FILTERS = 4

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



df_list = pd.read_html('scouting1.html')

for i, df in enumerate(df_list):
    print(df)
    df.to_csv('table {}.csv'.format(i))