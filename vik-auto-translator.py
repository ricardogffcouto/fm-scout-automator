import shutil
import os
import globals as GLOB

TIMES = 10

COORDINATES = {
    'Text to translate': (271, 444),
    'Deepl English': (316, 430),
    'Deepl Portuguese': (726, 356),
    'Text translated': (203, 643),
}

def sleep(time = 0.5):
    os.system("xdotool sleep %s" % time)

def move_click(label):
    os.system("xdotool mousemove %s %s click 1" % COORDINATES[label])
    sleep()

def ctrl(letter):
    os.system("xdotool key ctrl+%s" % letter)
    sleep()

def alt_tab():
    os.system("xdotool keydown alt")
    os.system("sleep .1")
    os.system("xdotool key Tab key alt")
    sleep()


def translate_text():
    move_click('Text to translate')
    ctrl('a')
    ctrl('c')
    alt_tab()
    move_click('Deepl English')
    ctrl('a')
    ctrl('v')
    sleep(3.5)
    move_click('Deepl Portuguese')
    ctrl('a')
    ctrl('c')
    alt_tab()
    move_click('Text translated')
    ctrl('a')
    ctrl('v')


def translate():
    print('10 seconds to start')
    sleep(9)
    print('Starting in 1 second')
    sleep(1)
    
    for translation in range(TIMES):
        translate_text()
        ctrl('Down')

if __name__ == '__main__':
    translate()
