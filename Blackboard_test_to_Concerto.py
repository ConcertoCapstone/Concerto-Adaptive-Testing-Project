import unicodedata
import PySimpleGUI as gui
import xmltodict
import copy
import glob


def make_window1():
    layout = [[gui.Text('Upload Blackboard test for conversion to .csv')],
              [gui.Text('Selected Blackboard Test Folder', size=(15, 1)), gui.FolderBrowse(size=(10, 1))],
              [gui.Submit(), gui.Cancel()]]
    return gui.Window('Blackboard Test Conversion', layout, finalize=True)


def make_window2(out_filename):
    file = open(out_filename, "r")

    # TODO add in between layout if statement that allows the user to opt out of this if they so decide (get rid
    #  of delineation phrases from csv and return)
    list_of_entries = file.readlines()
    all_tabs = []
    window_lines = []
    window_tab_lines = []
    header = list_of_entries.pop(0).split(',*')

    for item in header:
        window_tab_lines.append(gui.Text(str(item), size=13))
    deep_tabbed = copy.deepcopy(window_tab_lines)
    window_lines.append(deep_tabbed)
    window_tab_lines.clear()

    for i, line in enumerate(list_of_entries, 1):
        line = line.split(',*')
        for item in line:
            window_tab_lines.append(gui.InputText(str(item), size=15))

        deep_tabbed = copy.deepcopy(window_tab_lines)
        window_lines.append(deep_tabbed)
        window_tab_lines.clear()

        if i != 0 and i % 10 == 0 or i == len(list_of_entries):
            deep_windowed = copy.deepcopy(window_lines)
            all_tabs.append(deep_windowed)
            window_lines.clear()
            for item in header:
                window_tab_lines.append(gui.Text(str(item), size=13))
            deep_tabbed = copy.deepcopy(window_tab_lines)
            window_lines.append(deep_tabbed)
            window_tab_lines.clear()

    tab_group_layout = []
    for j in range(len(all_tabs)):
        tab_group_layout.append([gui.Tab("Tab %d" % (j + 1), all_tabs[j], key='-TAB%d-' % (j + 1))])

    layout = [[gui.TabGroup(tab_group_layout, enable_events=True, key='-TABGROUP-')], [gui.Submit(), gui.Cancel()]]
    return gui.Window('Blackboard Test Conversion', layout, finalize=True)


def make_window3():
    layout = [[gui.Text(
        "Are you sure you want to save the file? Any further changes to the .CSV will need to be made manually.")],
        [gui.Submit("Confirm"), gui.Cancel()]]
    return gui.Window('Confirm', layout, no_titlebar=False, finalize=True)


# def make_window4():
#     layout = [[gui.Text(
#         "Would you like to edit the test questions now or in a .csv file later?")],
#         [gui.Submit("Confirm"), gui.Cancel()]]
#     return gui.Window('Confirm', layout, no_titlebar=False, finalize=True)


def main():
    # set the window color theme
    gui.ChangeLookAndFeel('DarkGrey13')

    # initialize the window with the layout we made
    window1, window2, window3= make_window1(), None, None

    while True:
        window, event, values = gui.read_all_windows()
        if event == gui.WIN_CLOSED or event == 'Cancel':
            window.close()
            if window == window3:
                window3 = None
            elif window == window2:
                window2 = None
            elif window == window1:
                break
        elif event == 'Submit' and not window2 and not window3:
            test_file = qualify_file(directory=values.get('Browse'))
            csv_file = parse_dat_file(test_file=test_file)
            window2 = make_window2(out_filename=csv_file)
        elif event == 'Submit' and not window3:
            window3 = make_window3()

    window.close()


def parse_dat_file(test_file):
    file = open(test_file, "rb")

    # read the contents of the file into a variable
    file_contents = file.read()

    # make a dictionary from the fileContents (which is actually formatted like a xml file) and store it into
    # a variable
    content_dict = xmltodict.parse(file_contents.decode())

    # TODO move this to the actual documentation and not in the comments
    #  We manually found where in the contentDict the file was found by converting the .DAT file to
    #  an .XML file and using a JetBrains IDE (PyCharm, IntelliJ, etc) to format that .XML file correctly
    #  so it was humanly-readable
    # Sift through the dictionary until you get to where the questions are stored
    content_dict = content_dict['questestinterop']['assessment']['section']['item']

    out_file_name = file.name.split(".")[0] + ".csv"
    with open(out_file_name, 'w') as f:
        # wr = csv.writer(f, quoting=csv.QUOTE_NONE)
        head = 'id,*fixedIndex,*trait,*question,*responseOptions,*p1,*p2,*p3,*p4,*SubGroupId,' \
               '*SubGroupSortOrder\n'
        f.write(head)

        # iterate through each question in the dictionary
        for i, questEntry in enumerate(content_dict, start=1):
            try:
                # if the question is multiple choice -- making sure the questions are the correct type
                if questEntry['itemmetadata']['bbmd_questiontype'] == "Multiple Choice":
                    # store the current question in a variable
                    current_quest = questEntry
                    ret_val = get_questions_and_responses(current_quest, [], [])
                    question_str = sanitize_string(s=ret_val['question'])
                    resp_list = ret_val['resp']
                    resp_id_list = ret_val['resp_id']

                    sorted_resp_list = response_sort(current_item=current_quest['resprocessing']['respcondition'],
                                                     resp_list=resp_list, resp_id_list=resp_id_list)
                    response_options = answer_generator_normal(sorted_resp_list, '"')
                    response_options = sanitize_string(s=response_options)

                    # TODO possibly convert to a list of variables
                    row = str(i) + ',*,*1,*' + '"' + str(
                        question_str) + '",*' + response_options + ',*1,*1,*1,*1,*1,*1\n'
                    # ,* is used as a delineation tool later
                f.write(row)

            except ValueError:
                print("This is not multiple choice")
    return out_file_name


def get_questions_and_responses(current_item, resp, resp_id):
    question = ""
    for block in current_item['presentation']['flow']['flow']:

        if block['@class'] == "QUESTION_BLOCK":
            question = block['flow']['material']['mat_extension']['mat_formattedtext']['#text']

        elif block['@class'] == "RESPONSE_BLOCK":
            for response in block['response_lid']['render_choice']['flow_label']:
                resp_id.append(response['response_label']['@ident'])
                ans = str(
                    response['response_label']['flow_mat']['material']['mat_extension']['mat_formattedtext']['#text'])
                ans = ans[ans.find("<p>") + 3: ans.rfind("</p>")]
                resp.append(ans)
    return {
        "resp": resp,
        "resp_id": resp_id,
        "question": question
    }


def sanitize_string(s):
    sanitize_str = unicodedata.normalize('NFKD', s)
    sanitize_str = sanitize_str.encode('utf-8')
    sanitize_str = sanitize_str.replace(b'\xe2\x80\x9c', b"'")
    sanitize_str = sanitize_str.replace(b'\xe2\x80\x9d', b"'")
    sanitize_str = sanitize_str.replace(b'\xe2\x80\x99', b"'")
    sanitize_str = sanitize_str.decode('utf-8')
    return sanitize_str


def response_sort(current_item, resp_list, resp_id_list):
    sorted_resp_list = [resp_list[0]]

    for set_of_responses in current_item:
        if set_of_responses['@title'] == "correct":
            for i, respID in enumerate(resp_id_list):
                if respID == set_of_responses['conditionvar']['varequal']['#text']:
                    sorted_resp_list[0] = resp_list[i]
                else:
                    sorted_resp_list.append(resp_list[i])
            break
    return sorted_resp_list


# Code from Dr. Gordon for creating the responseOptions line
def answer_generator_normal(sorted_resp_list, bracket_char):
    response_options = '{""type"":""options"",""optionsRandomOrder"":""1"",""options"":['

    for i in range(4):
        raw_answer_option = bracket_char * 2 + sorted_resp_list[i] + bracket_char * 2
        temp = i + 1
        response_options += '{""label"":' + raw_answer_option + ',""value"":""' + str(temp) + '""}'
        if i < 3:
            response_options += ','
    response_options += '],""defaultScore"":""0"",""scoreMap"":[{""value"":""1"",""score"":""1"",""trait"":null}]}'

    response_options = response_options.replace('\\', '\\\\')
    response_options = '"' + response_options + '"'
    return response_options


# given a directory, will look through the files and find the one containing
# proper information about the tests
# (check if <questestinterop> is universal between tests in blackboard)
def qualify_file(directory):
    for filename in glob.iglob(f'{directory}/*.dat'):
        with open(filename, 'r', encoding='utf-8') as f:
            readfile = f.read()
            if '<questestinterop>' in readfile:
                return filename


if __name__ == '__main__':
    main()
