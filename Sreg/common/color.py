#!/usr/bin/env python
# coding=utf8
# author=e0@2015<ff0000team>


def inBlack(s):
    return highlight('') + f"{chr(27)}[30;2m{s}{chr(27)}[0m"


def inRed(s):
    return highlight('') + f"{chr(27)}[31;2m{s}{chr(27)}[0m"


def inGreen(s):
    return highlight('') + f"{chr(27)}[32;2m{s}{chr(27)}[0m"


def inYellow(s):
    return highlight('') + f"{chr(27)}[33;2m{s}{chr(27)}[0m"


def inBlue(s):
    return highlight('') + f"{chr(27)}[34;2m{s}{chr(27)}[0m"


def inPurple(s):
    return highlight('') + f"{chr(27)}[35;2m{s}{chr(27)}[0m"


def inWhite(s):
    return highlight('') + f"{chr(27)}[37;2m{s}{chr(27)}[0m"


def highlight(s):
    return f"{chr(27)}[30;2m{s}{chr(27)}[1m"
