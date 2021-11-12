import PySimpleGUI as sg
import xml.etree.ElementTree as ET
import pandas as pd
import os


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
            s = s.split('/')[-1] #grab the filename
            data = file.read() #this is the contents of the file
            if os.path.exists(s):
                os.remove(s)
            s = s.split('.')[0] + '.xml' #change the filename .xml (this only works with res00001.dat for some reason)
            file2 = open(s, 'w')
            file2.write(data) #new .xml file with old .dat info
            convert(file2, s)
            break
    # print('You entered ', values[0])

    window.close()


def convert(file, fileName):
    print(file)
    tree = ET.parse(fileName) #supposed to parse .xml file into its components
    root = tree.getroot()

    get_range = lambda col: range(len(col))
    l = [{r[i].tag: r[i].text for i in get_range(r)} for r in root]

    df = pd.DataFrame.from_dict(l)
    df.to_csv(fileName.split('.')[0] + '.csv')

if __name__ == '__main__':
    main()
