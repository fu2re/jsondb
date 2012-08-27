#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
#sys.path.append('/home/fu2re/Documents/Project/content_engine')
from main import command

def main():
    app, mainForm, window = command.init()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 