from pprint import pprint

import PySimpleGUI as sg
import xml.etree.ElementTree as ET
import pandas as pd
import os

import xmltodict


def main():
    sg.ChangeLookAndFeel('DarkAmber')  # Add a touch of color

    # All the stuff inside your window.
    layout = [[sg.Text('Upload Blackboard sample quiz for conversion to .csv')],
              [sg.Text('Upload .dat file:', size=(15, 1)), sg.InputText(),
               sg.FileBrowse(size=(10, 1), file_types=(("DAT files", "*.dat"),))],
              [sg.Submit(), sg.Cancel()]]

    # Create the Window
    window = sg.Window('Window Title', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break
        elif event == 'Submit':
            file = open(values[0])
            s = '' + values[0]
            s = s.split('/')[-1]  # grab the filename
            data = file.read()  # this is the contents of the file
            dic = xmltodict.parse(data)
            print(type(dic))
            dic2 = dic['questestinterop']['assessment']['section']
            # pprint(dic2)
            # pprint(dic2[0]['presentation'])
            # ['presentation']['flow']['flow']['flow']['material']['mat_extension']['mat_formattedtext']

            for k in dic2:
                try:
                    print("Question title = " + str(k['@title']) + "\n")
                    print("Question = ")
                    print(k)
                    print(k['presentation']['flow']['flow']['flow']['material']['mat_extension']['mat_formattedtext'])
                    print("Answer = ")
                except ValueError:
                    print("This is not multiple choice")

            # if os.path.exists(s):
            #     os.remove(s)
            s = s.split('.')[0] + '.xml'  # change the filename .xml (this only works with res00001.dat for some reason)
            file2 = open(s, 'w')
            file2.write(data)  # new .xml file with old .dat info
            break
    # print('You entered ', values[0])

    window.close()


def convertFileToStr():
    print()


def parse(file, fileName):
    print("hello")


if __name__ == '__main__':
    main()
