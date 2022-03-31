from pprint import pprint
import unicodedata
import PySimpleGUI as gui
import xmltodict
import copy


def main():
    # set the window color theme
    gui.ChangeLookAndFeel('DarkAmber')

    # add features to the window
    layout = [[gui.Text('Upload Blackboard test for conversion to .csv')],
              [gui.Text('Upload .dat file:', size=(15, 1)), gui.InputText(),
               gui.FileBrowse(size=(10, 1), file_types=(("DAT files", "*.dat"),))],
              [gui.Submit(), gui.Cancel()]]

    # initialize the window with the layout we made
    window = gui.Window('Blackboard Test Conversion', layout)

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
            outFileName = file.name.split(".")[0] + ".csv"
            with open(outFileName, 'w') as f:
                # wr = csv.writer(f, quoting=csv.QUOTE_NONE)
                head = 'id,*fixedIndex,*trait,*question,*responseOptions,*p1,*p2,*p3,*p4,*SubGroupId,' \
                       '*SubGroupSortOrder\n'
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

                            questionStr = sanitizeString(questionStr)

                            respList = retVal['resp']
                            respIDList = retVal['respID']

                            sortedRespList = responseSort(currentQuest['resprocessing']['respcondition'], respList,
                                                          respIDList)

                            responseOptions = answer_generator_normal(sortedRespList, '"')
                            responseOptions = sanitizeString(responseOptions)

                            # responseOptions = unicodedata.normalize('NFKD', responseOptions)

                            # TODO possibly convert to a list of variables
                            row = str(i) + ',*,*1,*' + '"' + str(
                                questionStr) + '",*' + responseOptions + ',*1,*1,*1,*1,*1,*1\n'  # ,* is used as
                            # a delineation tool later

                        # pprint(row)
                        f.write(row)

                        i += 1
                    except ValueError:
                        print("This is not multiple choice")

            csvEditLayout = makeNewLayout(outFileName)
            window = gui.Window('Edit .csv file', csvEditLayout, no_titlebar=False)

            # tab_keys = ('-TAB1-', '-TAB2-')#, '-TAB3-') #TODO this is for doing checked or invisible tabs if wanted
            while True:
                event, values = window.read()  # type: str, dict
                print(event, values)
                if event == gui.WIN_CLOSED:
                    break
                elif event == "Submit":
                    confirmVal = areYouSureWin()
                    if confirmVal == "Confirm":
                        return #TODO continue your stuff
                    elif confirmVal == "Cancel":
                        break

                elif event == "Cancel":
                    break
            # if event == 'Invisible':
            #     window[tab_keys[int(values['-IN-']) - 1]].update(visible=False)
            # if event == 'Visible':
            #     window[tab_keys[int(values['-IN-']) - 1]].update(visible=True)
            # if event == 'Select':
            #     window[tab_keys[int(values['-IN-']) - 1]].select()

    window.close()


def areYouSureWin():
    layout = [[gui.Text(
        "Are you sure you want to save the file? Any further changes to the .CSV will need to be made manually.")],
              [gui.Submit("Confirm"), gui.Cancel()]]

    window = gui.Window('Confirm', layout, no_titlebar=False)

    # tab_keys = ('-TAB1-', '-TAB2-')#, '-TAB3-') #TODO this is for doing checked or invisible tabs if wanted
    while True:
        event, values = window.read()  # type: str, dict
        print(event, values)
        if event == gui.WIN_CLOSED:
            break
        elif event == "Confirm":
            window.close()
            return "Confirm"
        elif event == "Cancel":
            return "Cancel"
    # ,
    # [gui.Text('Make tab number'), gui.Input(key='-IN-', size=(3, 1)), gui.Button('Invisible'),
    #  gui.Button('Visible'), gui.Button('Select')]]
    window.close()
    return layout


def makeNewLayout(outFilename):
    file = open(outFilename, "r")

    # TODO add in between layout if statement that allows the user to opt out of this if they so decide (get rid
    #  of deliniation phrases from csv and return)
    listOfEntries = file.readlines()
    numEntries = len(listOfEntries)
    allTabs = []
    windowLines = []
    windowTabLines = []
    header = listOfEntries.pop(0)
    header = header.split(',*')

    # windowTabLines.append(gui.Text(item) for item in header)
    for item in header:
        windowTabLines.append(gui.Text(str(item), size=13))
    deep_tabbed = copy.deepcopy(windowTabLines)
    windowLines.append(deep_tabbed)
    windowTabLines.clear()

    for i, line in enumerate(listOfEntries, 1):
        line = line.split(',*')
        for item in line:
            windowTabLines.append(gui.InputText(str(item), size=15))

        deep_tabbed = copy.deepcopy(windowTabLines)
        windowLines.append(deep_tabbed)
        windowTabLines.clear()

        if i != 0 and i % 10 == 0 or i == numEntries:
            deep_windowed = copy.deepcopy(windowLines)
            allTabs.append(deep_windowed)
            windowLines.clear()
            for item in header:
                windowTabLines.append(gui.Text(str(item), size=13))
            deep_tabbed = copy.deepcopy(windowTabLines)
            windowLines.append(deep_tabbed)
            windowTabLines.clear()

    tabGroupLayout = []
    for j in range(len(allTabs)):
        tabGroupLayout.append([gui.Tab("Tab %d" % (j + 1), allTabs[j], key='-TAB%d-' % (j + 1))])

    layout = [[gui.TabGroup(tabGroupLayout,
                            enable_events=True,
                            key='-TABGROUP-')],
              [gui.Submit(), gui.Cancel()]]
    # ,
    # [gui.Text('Make tab number'), gui.Input(key='-IN-', size=(3, 1)), gui.Button('Invisible'),
    #  gui.Button('Visible'), gui.Button('Select')]]

    return layout


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
                ans = str(ans)
                ans = ans[ans.find("<p>") + 3: ans.rfind("</p>")]
                resp.append(ans)
                pprint(str(respID) + " " + str(ans))

    return {
        "resp": resp,
        "respID": respID,
        "question": question
    }


def sanitizeString(s):
    # retList = []
    # for r in listR:
    saniStr = unicodedata.normalize('NFKD', s)
    saniStr = saniStr.encode('utf-8')
    saniStr = saniStr.replace(b'\xe2\x80\x9c', b"'")
    saniStr = saniStr.replace(b'\xe2\x80\x9d', b"'")
    saniStr = saniStr.replace(b'\xe2\x80\x99', b"'")
    saniStr = saniStr.decode('utf-8')

    return saniStr


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
    ResponseOptions = '{""type"":""options"",""optionsRandomOrder"":""1"",""options"":['

    AnswerOptionRaw = bracket_char * 2 + sortedRespList[0] + bracket_char * 2

    # Each line that looks like this was changed from this:
    # ResponseOptions = ResponseOptions + '{"label":"' + AnswerOptionRaw + '","value":"1"}'
    # To this:
    ResponseOptions = ResponseOptions + '{""label"":' + AnswerOptionRaw + ',""value"":""1""}'
    # This is because there were too many quotes

    ResponseOptions = ResponseOptions + ','

    AnswerOptionRaw = bracket_char * 2 + sortedRespList[1] + bracket_char * 2

    ResponseOptions = ResponseOptions + '{""label"":' + AnswerOptionRaw + ',""value"":""2""}'

    ResponseOptions = ResponseOptions + ','

    AnswerOptionRaw = bracket_char * 2 + sortedRespList[2] + bracket_char * 2

    ResponseOptions = ResponseOptions + '{""label"":' + AnswerOptionRaw + ',""value"":""3""}'

    ResponseOptions = ResponseOptions + ','

    AnswerOptionRaw = bracket_char * 2 + sortedRespList[3] + bracket_char * 2

    ResponseOptions = ResponseOptions + '{""label"":' + AnswerOptionRaw + ',""value"":""4""}'

    ResponseOptions = ResponseOptions + '],""defaultScore"":""0"",""scoreMap"":[{""value"":""1"",""score"":""1"",""trait"":null}]}'

    ResponseOptions = ResponseOptions.replace('\\', '\\\\')

    # ResponseOptions = ResponseOptions.replace('"', '""')

    # Lines added by Chris
    ResponseOptions = '"' + ResponseOptions + '"'

    return ResponseOptions


if __name__ == '__main__':
    main()
