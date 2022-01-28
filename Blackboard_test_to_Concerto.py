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
            # get the file that is selected on the form
            file = open(values[0])

            # read the contents of the file into a variable
            data = file.read()

            # make a dictionary from the data (which is actually formatted like a xml file) and store into a variable
            dic = xmltodict.parse(data)

            # TODO debugging line
            print(type(dic))

            # sift through the dictionary until you get to the first question
            dic = dic['questestinterop']['assessment']['section']['item']

            i = 0
            # iterate through each question in the dictionary
            for k in dic:
                try:
                    # if the question is multiple choice
                    if k['itemmetadata']['bbmd_questiontype'] == "Multiple Choice":
                        print(i)
                        # store the current question in a variable
                        currentItem = k

                        # print the current question's title
                        print("Question title = " + str(currentItem['@title']) + "\n")


                        # currentItem = currentItem['presentation']
                        temp = str(currentItem['presentation']['flow']['flow'][0]['flow']['material']['mat_extension']['mat_formattedtext'][
                                   '#text'])
                        print("Question: " + temp[temp.find("<p>")+3:temp.rfind("</p>")])
                        # print("Question = " + str(
                        #     currentItem['flow']['flow']['flow']['material']['mat_extension']['mat_formattedtext']))

                    # print(k)

                    # print(k['presentation']['flow']['flow']['flow']['material']['mat_extension']['mat_formattedtext'])
                    # print("Answer = ")
                    i += 1
                except ValueError:
                    print("This is not multiple choice")

            # if os.path.exists(s):
            #     os.remove(s)
            # s = s.split('.')[0] + '.xml'  # change the filename .xml (this only works with res00001.dat for some reason)
            # file2 = open(s, 'w')
            # file2.write(data)  # new .xml file with old .dat info
            break
    # print('You entered ', values[0])

    window.close()


def convertFileToStr():
    print()


def parse(file, fileName):
    print("hello")


if __name__ == '__main__':
    main()
