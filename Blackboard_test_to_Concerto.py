import csv
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
            file = open(values[0], "rb")

            # read the contents of the file into a variable
            data = file.read()

            # make a dictionary from the data (which is actually formatted like a xml file) and store into a variable
            dic = xmltodict.parse(data.decode())

            # TODO debugging line
            print(type(data))

            # sift through the dictionary until you get to the first question
            dic = dic['questestinterop']['assessment']['section']['item']

            i = 1
            with open('output.csv', 'w') as f:
                wr = csv.writer(f, quoting=csv.QUOTE_NONE)
                head = ['id', 'fixedIndex', 'trait', 'question', 'responseOptions', 'p1', 'p2', 'p3', 'p4',
                        'SubGroupId', 'SubGroupSortOrder']

                wr.writerow(head)
                wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
                # iterate through each question in the dictionary
                for item in dic:
                    try:
                        # if the question is multiple choice
                        if item['itemmetadata']['bbmd_questiontype'] == "Multiple Choice":
                            # TODO debugging line
                            print(i)

                            # store the current question in a variable
                            currentItem = item

                            # print the current question's title
                            print("Question title = " + str(currentItem['@title']) + "\n")

                            # currentItem = currentItem['presentation']
                            # question = str(
                            #     currentItem['presentation']['flow']['flow'][0]['flow']['material']['mat_extension'][
                            #         'mat_formattedtext'][
                            #         '#text'])
                            # print("Question: " + question)
                            p = []
                            respID = []
                            # pprint("This is the type" + str((currentItem['presentation']['flow']['flow'])))

                            for block in currentItem['presentation']['flow']['flow']:
                                # pprint("asdmakd " + str(len(currentItem['presentation']['flow']['flow'])))

                                if block['@class'] == "QUESTION_BLOCK":
                                    question = str(
                                        block['flow']['material']['mat_extension']['mat_formattedtext']['#text'])
                                    print("Question: " + question)

                                elif block['@class'] == "RESPONSE_BLOCK":
                                    for response in block['response_lid']['render_choice']['flow_label']:
                                        respID.append(response['response_label']['@ident'])
                                        ans = response['response_label']['flow_mat']['material']['mat_extension'][
                                            'mat_formattedtext']['#text']
                                        p.append(ans)
                                        pprint(str(respID) + " " + str(ans))

                            row = [i, '', '', str(question), 'responseOptions', str(p[0]),
                                   str(p[1]), str(p[2]),
                                   str(p[3]), 'SubGroupId', 'SubGroupSortOrder']
                            pprint(row)
                            wr.writerow(row)

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


def iterative(currentItem, p, respID):
    for block in currentItem['presentation']['flow']['flow']:
        pprint("asdmakd " + str(len(currentItem['presentation']['flow']['flow'])))

        if block['@class'] == "QUESTION_BLOCK":
            pprint(block['flow']['material']['mat_extension']['mat_formattedtext']['#text'])

        elif block['@class'] == "RESPONSE_BLOCK":
            for response in block['response_lid']['render_choice']['flow_label']:
                respID.append(response['response_label']['@ident'])
                ans = response['response_label']['flow_mat']['material']['mat_extension'][
                    'mat_formattedtext']['#text']
                p.append(ans)
                pprint(str(respID) + " " + str(ans))

        return {
            "p": p,
            "respID": respID
        }


def convertFileToStr():
    print()


def parse(file, fileName):
    print("hello")


if __name__ == '__main__':
    main()
