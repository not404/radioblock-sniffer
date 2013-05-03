from distutils.core import setup
import py2exe
import sys
import os


Mydata_files = []

'''
Mydata_files = [('', ['runner.jpg','white.jpg','play.ico','pause.ico','stop.ico',\
                            'logocrono.ico','beep.wav','runnerbeep.wav','play.png'])]
'''
includes = ["pygame.mixer.music", "pygame.mixer_music", "pygame"]
EXCLUDES = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
                                'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
                                'Tkconstants', 'Tkinter']

for files in os.listdir('c:\\Python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\'):
    f1 = 'c:\\Python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\' + files
    if os.path.isfile(f1): # skip directories
        f2 = 'imageformats', [f1]
        Mydata_files.append(f2)
        
#Mydata_files = [('imageformats', ['c:\\Users\\Clara\\Projects\\pyqt\\chap06\\imageformats\\*.*'])]

options = {
    'py2exe': {
        'includes':includes,
        'compressed':True,
        'excludes': EXCLUDES,
        'dll_excludes': ['MSVCP90.dll'],
        'bundle_files' : 1,
        
     }
}

sys.argv.append("py2exe")
sys.argv.append("--includes")
sys.argv.append("sip")
setup(windows = [{"script": 'sm_sniffer.py','icon_resources':[(1,"favicon.ico")]}], data_files = Mydata_files, options=options,
version='1.2',
Author='Clara Ferrando',
email='clara.ferrando@gmail.com')


