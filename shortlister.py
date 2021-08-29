import shutil
import os
import globals as GLOB

INITIAL_FILTER_Y = 807
FILTER_OFFSET_Y = 30
NUM_FILTERS = 5


def activate_fm():
    window_id = os.popen("xdotool search --name 'Football Manager 2019 Touch'").read()
    if (window_id):
        os.system("xdotool key 'F2'")
        os.system('xdotool windowactivate %s' % (window_id) )
        os.system("xdotool sleep 0.5")
        return True
    return False


def sleep():
    os.system("xdotool sleep 0.5")


def move_click(coordinates):
    os.system("xdotool mousemove %s %s click 1" % coordinates)
    sleep()


COORDINATES = {
    'Edit search': (1836, 175),
    'Open filters': (946, 667),
    'Search OK': (1058, 586),
    'FM Menu': (1647, 33),
    'Print Screen': (1647, 451),
    'Print to Web Page OK': (1041, 618)
    'Print to Web Page Save': (1161, 764),
}


def extract_shortlist(filter_id):
    # Select filter
    move_click(COORDINATES['Edit search'])
    move_click(COORDINATES['Open filters'])
    move_click((COORDINATES['Edit search'][0], INITIAL_FILTER_Y + filter_id * FILTER_OFFSET_Y))
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

    dst_path = os.path.join(GLOB.MAIN_PATH, 'shortlists', 'shortlist_%s.html' % filter_id)
    shutil.move(GLOB.FM_PATH, dst_path)

def import_shortlists():
    if activate_fm():
        for filter_id in range(NUM_FILTERS):
            extract_shortlist(filter_id)

if __name__ == '__main__':
    import_shortlists()