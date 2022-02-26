import csv
from pprint import pprint

import PySimpleGUI as gui
import xmltodict


def main():
    # set the window color theme
    gui.ChangeLookAndFeel('DarkAmber')

    # add features to the window
    layout = [[gui.Text('Upload Blackboard sample quiz for conversion to .csv')],
              [gui.Text('Upload .dat file:', size=(15, 1)), gui.InputText(),
               gui.FileBrowse(size=(10, 1), file_types=(("DAT files", "*.dat"),))],
              [gui.Submit(), gui.Cancel()]]

    # initialize the window with the layout we made
    window = gui.Window('Window Title', layout)

    # loop that handles events and gets the values of whatever is input -- in our case, a .DAT file
    while True:
        event, values = window.read()
        if event == gui.WIN_CLOSED or event == 'Cancel':  # if a user closes the window or clicks cancel
            break
        elif event == 'Submit':
            # get the file that is selected using the form
            file = open(values[0], "rb")

            # read the contents of the file into a variable
            fileContents = file.read()

            # make a dictionary from the fileContents (which is actually formatted like a xml file) and store it into
            # a variable
            contentDict = xmltodict.parse(fileContents.decode())

            # Sift through the dictionary until you get to where the questions are stored
            # TODO move this to the actual documentation and not in the comments
            #  We manually found where in the contentDict the file was found by converting the .DAT file to
            #  an .XML file and using a JetBrains IDE (PyCharm, IntelliJ, etc) to format that .XML file correctly
            #  so it was humanly-readable
            contentDict = contentDict['questestinterop']['assessment']['section']['item']

            i = 1
            with open('output.csv', 'w') as f:
                # wr = csv.writer(f, quoting=csv.QUOTE_NONE)
                head = 'id,fixedIndex,trait,question,responseOptions,p1,p2,p3,p4,SubGroupId,SubGroupSortOrder\n'
                f.write(head)

                # iterate through each question in the dictionary
                for questEntry in contentDict:
                    try:
                        # if the question is multiple choice -- making sure the questions are the correct type
                        if questEntry['itemmetadata']['bbmd_questiontype'] == "Multiple Choice":

                            # store the current question in a variable
                            currentQuest = questEntry


                            retVal = getQuestionsAndResponses(currentQuest, [], [])
                            questionStr = retVal['question']
                            respList = retVal['resp']
                            respIDList = retVal['respID']

                            sortedRespList = responseSort(currentQuest['resprocessing']['respcondition'], respList,
                                                          respIDList)

                            responseOptions = answer_generator_normal(sortedRespList, '"')

                            row = str(i) + ',,' + ',' + '"' + str(
                                questionStr) + '",' + responseOptions + ',,,,,,\n'

                        pprint(row)
                        f.write(row)

                        i += 1
                    except ValueError:
                        print("This is not multiple choice")

    window.close()


def getQuestionsAndResponses(currentItem, resp, respID):
    question = ""
    for block in currentItem['presentation']['flow']['flow']:

        if block['@class'] == "QUESTION_BLOCK":
            question = block['flow']['material']['mat_extension']['mat_formattedtext']['#text']
            pprint(question)

        elif block['@class'] == "RESPONSE_BLOCK":
            for response in block['response_lid']['render_choice']['flow_label']:
                respID.append(response['response_label']['@ident'])
                ans = response['response_label']['flow_mat']['material']['mat_extension'][
                    'mat_formattedtext']['#text']
                resp.append(ans)
                pprint(str(respID) + " " + str(ans))

    return {
        "resp": resp,
        "respID": respID,
        "question": question
    }


def responseSort(currentItem, respList, respIDList):
    sortedRespList = [respList[0]]
    i = 0

    for setOfResponses in currentItem:
        if setOfResponses['@title'] == "correct":
            for respID in respIDList:
                print(setOfResponses)
                if respID == setOfResponses['conditionvar']['varequal']['#text']:
                    sortedRespList[0] = respList[i]
                else:
                    sortedRespList.append(respList[i])
                i = i + 1
            break

    return sortedRespList

# Code from Dr. Gordon for creating the responseOptions line
def answer_generator_normal(sortedRespList, bracket_char):
    # ResponseOptions = '{"type":"options","optionsRandomOrder":"1","options":['
    ResponseOptions = '{""type"":","options"",""optionsRandomOrder"":""1"",""options"":['

    AnswerOptionRaw = bracket_char*2 + sortedRespList[0] + bracket_char*2

    # Each line that looks like this was changed from this:
    # ResponseOptions = ResponseOptions + '{"label":"' + AnswerOptionRaw + '","value":"1"}'
    # To this:
    ResponseOptions = ResponseOptions + '{""label"":' + AnswerOptionRaw + ',""value"":""1""}'
    # This is because there were too many quotes

    ResponseOptions = ResponseOptions + ','

    AnswerOptionRaw = bracket_char*2 + sortedRespList[1] + bracket_char*2

    ResponseOptions = ResponseOptions + '{""label"":' + AnswerOptionRaw + ',""value"":""2""}'

    ResponseOptions = ResponseOptions + ','

    AnswerOptionRaw = bracket_char*2 + sortedRespList[2] + bracket_char*2

    ResponseOptions = ResponseOptions + '{""label"":' + AnswerOptionRaw + ',""value"":""3""}'

    ResponseOptions = ResponseOptions + ','

    AnswerOptionRaw = bracket_char*2 + sortedRespList[3] + bracket_char*2

    ResponseOptions = ResponseOptions + '{""label"":' + AnswerOptionRaw + ',""value"":""4""}'

    ResponseOptions = ResponseOptions + '],""defaultScore"":""0"",""scoreMap"":[{""value"":""1"",""score"":""1"",""trait"":null}]}'

    ResponseOptions = ResponseOptions.replace('\\', '\\\\')

    # ResponseOptions = ResponseOptions.replace('"', '""')

    # Lines added by Chris
    ResponseOptions = '"' + ResponseOptions + '"'

    return ResponseOptions


if __name__ == '__main__':
    main()
