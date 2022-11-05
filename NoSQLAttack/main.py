import os

import shodan
import sys

import signal
import globalVar as GlobalVar
from mongo import netAttacks
import option
from getApps import getApps
from scanIP import scanMongoDBIP
mainMe = 1
def main():
#    signal.signal(signal.SIGINT, signal_handler)
    global optionSet
    #Set a list so we can track whether options are set or not to avoid resetting them in subsequent cals to the options menu.
    optionSet = [False]*9
    global yes_tag
    global no_tag
    yes_tag = ['y', 'Y']
    no_tag = ['n', 'N']
    global victim
    global webPort
    global uri
    global httpMethod
    global platform
    global https
    global myIP
    global myPort
    global verb
    global scanNeedCreds
    global dbPort
    #Use MongoDB as the default, since it's the least secure ( :-p at you 10Gen )
    platform = "MongoDB"
    dbPort = 27017
    myIP = "Not Set"
    myPort = "Not Set"
    mainMenu()

def mainMenu():
    global platform
    global victim
    global dbPort
    global myIP
    global myPort
    mmSelect = True
    while mmSelect:
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        os.system('clear')
        select = raw_input("Select an option:")
        if select == "1":
            scanMongoDBIP()
        if select == "2":
            option.option();
        elif select == "3":
            if (
                GlobalVar.get_optionSet(0) == True
                and GlobalVar.get_optionSet(4) == True
            ) and platform == "MongoDB":
                netAttacks( GlobalVar.get_victim(),GlobalVar.get_dbPort(),GlobalVar.get_myIP(),GlobalVar.get_myPort())
        elif select == "4":
            if (
                (GlobalVar.get_optionSet(0) == True)
                and (GlobalVar.get_optionSet(2) == True)
                and GlobalVar.get_httpMethod() == "GET"
            ):
                getApps()
        elif select == "x":
            sys.exit()
        else:
            raw_input("Invalid selection.  Press enter to continue.")


if __name__ == "__main__":
    main()