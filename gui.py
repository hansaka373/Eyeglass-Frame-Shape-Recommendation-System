#!/usr/bin/python3

import base64
import logging
import sys
from functools import partial
from io import BytesIO
import json

import PySimpleGUI as sg
import cv2

from expert_backend import ExpertEyeglassesRecommender



# font-styles
FONT_STYLE = 'Helvetica'
BIG_FONT = (FONT_STYLE, 18)
MEDIUM_FONT = (FONT_STYLE, 15)
SMALL_FONT = (FONT_STYLE, 12)
TINY_FONT = (FONT_STYLE, 10)

sg.theme('DarkBlue')

if __name__ == '__main__':
    # partial functions for some frequent elements to reduce repetitions in arguments
    chart = {1:2.50 , 2:1.50 , 3:1.25, 4:1.00 , 5:0.75 , 6:0.50 , 7:0.25 , 8:0 , 9:0 , 10:0}
    rEye = 0
    lEye = 0
    text_element_left = partial(sg.Text, font=MEDIUM_FONT, justification='left')
    text_element_right = partial(sg.Text, font=MEDIUM_FONT, justification='right')
    text_element_center = partial(sg.Text, font=MEDIUM_FONT, justification='center')
    button_element = partial(sg.Button, visible=True, enable_events=True)
    button_element1 = partial(sg.Button, visible=True, enable_events=True)
    combo_element = partial(sg.Combo, font=MEDIUM_FONT, auto_size_text=True)

    def eye_sight():
        try:
            # lay out for eye sight window
            eye_layout = [[sg.Text(lang_gui['layout2']['header'], font=BIG_FONT, justification="center")],
                          [sg.Image('assets/Eye_Chart.png')],
                          [sg.Text('Right eye', size=(10, 1)), sg.InputText(key='-R-')],
                          [sg.Text('Left eye', size=(10, 1)), sg.InputText(key='-L-')],
                          [button_element("Instruction", key='instructions'), button_element("Submit", key='Submit'),
                           sg.Exit()],
                          ]
            eye_win = sg.Window('Eye sight checker', eye_layout)

            while True:
                e_event, e_values = eye_win.read()

                # instructions for eye sight check
                if e_event == 'instructions':
                    sg.popup_ok("1. Please stand at 20 feat away from chart", "\n",
                                "2. If you has glasses make sure remove the glasses for distance vision.", "\n",
                                "3. You must cover the eye not being tested.", "\n",
                                "4. First read the First line can see on the chart", "\n",
                                "5. If you reads all  letters correctly and there are more lines below try the next line.",
                                "\n",
                                "6. add the most read line to the correct eye input in the window", "\n"
                                                                                                    "6. Repeat steps for opposite eye.")

                # check eye sight
                elif e_event == 'Submit':
                    rEye = 0
                    lEye = 0
                    try:
                        # get input values
                        input_text = (e_values)

                        right = int(input_text['-R-'])
                        left = int(input_text['-L-'])

                        # Convert input values to lens
                        rEye = chart[int(right)]
                        lEye = chart[int(left)]

                        # If eye can read line 8 or more they have normal eyes else need lens
                        if right >= 8 and left <= 7:
                            sg.popup_ok("You have normal eye sight in right eye and you need -" + str(
                                lEye) + "D lens for the left eye")

                        elif left >= 8 and right <= 7:
                            sg.popup_ok("You have normal eye sight in left eye and you need -" + str(
                                rEye) + "D lens for the right eye")

                        elif left >= 8 and right >= 8:
                            sg.popup_ok("you have normal eye sight")

                        else:
                            sg.popup_ok("You need -" + str(rEye) + "D lens for the right eye and", "\n",
                                        " -" + str(lEye) + " D lens for the left eye")

                    except:
                        sg.popup_ok("error in values, please recheck")
                else:
                    eye_win.close()
                    break


        except Exception as exception:
            logger.error(lang_gui['logger']['error']['extracting_editing'], exception)

    # gets or creates a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # define file handler and set formatter
    file_handler = logging.FileHandler('logfile.log')
    file_handler.setLevel(logging.DEBUG)

    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # add file handler to logger
    logger.addHandler(file_handler)

    # layout for start screen
    layout0 = [[sg.Column([[sg.Text('Eye test', key='chose_text1')],
                           [button_element("test eye sight", key='T_sight')],
                            [sg.Text('Choose an image with face', key='chose_text')],
                           [sg.Input(key='file', visible=False, enable_events=True),
                            sg.FileBrowse('Open', key='open')],
                           [sg.Text('Language', key='lang_text')],
                           [combo_element(key='lang', values=('English', 'Русский'),
                                          default_value='English', enable_events=True)]],
                          element_justification='c')]]

    # create the Window
    start_win = sg.Window('Start window', layout0 )
    while True:
        event, values = start_win.read()




        if values['lang'] == 'English':
            LANGUAGE = 'en'


        # load localization of GUI
        with open("lang/%s_lang.json" % LANGUAGE, "r") as f:
            lang_gui = json.load(f)['gui'].copy()

        # update text in the current window
        start_win['lang_text'].update(lang_gui['layout0']['lang_text'])
        start_win['chose_text'].update(lang_gui['layout0']['chose'])
        start_win['open'].update(lang_gui['layout0']['open'])
        start_win.TKroot.title(lang_gui['start_win']['title'])

        # eye sight check with snellen chart
        if event == 'T_sight':
            try:
                # lay out for eye sight window
                eye_layout = [[sg.Text(lang_gui['layout2']['header'], font=BIG_FONT, justification="center")],
                              [sg.Image('assets/Eye_Chart.png')],
                              [sg.Text('Right eye', size=(10, 1)), sg.InputText(key='-R-')],
                              [sg.Text('Left eye', size=(10, 1)), sg.InputText(key='-L-')],
                              [button_element("Instruction", key = 'instructions'),button_element("Submit", key = 'Submit'), sg.Exit()],
                              ]
                eye_win = sg.Window('Eye sight checker', eye_layout)

                while True:
                    e_event, e_values = eye_win.read()

                    # instructions for eye sight check
                    if e_event == 'instructions':
                        sg.popup_ok("1. Please stand at 20 feat away from chart","\n",
                                    "2. If you has glasses make sure remove the glasses for distance vision.","\n",
                                    "3. You must cover the eye not being tested.","\n",
                                    "4. First read the First line can see on the chart","\n",
                                    "5. If you reads all  letters correctly and there are more lines below try the next line.","\n",
                                    "6. add the most read line to the correct eye input in the window", "\n"
                                    "6. Repeat steps for opposite eye.")

                    #check eye sight
                    elif e_event == 'Submit':
                        rEye = 0
                        lEye = 0
                        try:
                            #get input values
                            input_text = (e_values)

                            right = int(input_text['-R-'])
                            left = int(input_text['-L-'])

                            #Convert input values to lens
                            rEye = chart[int(right)]
                            lEye = chart[int(left)]

                            #If eye can read line 8 or more they have normal eyes else need lens
                            if right >= 8 and left <= 7 :
                                sg.popup_ok("You have normal eye sight in right eye and you need -"+str(lEye)+"D lens for the left eye")

                            elif left >= 8 and right <= 7 :
                                sg.popup_ok("You have normal eye sight in left eye and you need -"+str(rEye)+"D lens for the right eye")

                            elif left >= 8 and right >= 8:
                                sg.popup_ok("you have normal eye sight")

                            else:
                                sg.popup_ok("You need -"+str(rEye)+"D lens for the right eye and","\n"," -"+str(lEye)+" D lens for the left eye" )

                        except:
                            sg.popup_ok("error in values, please recheck")
                    else:
                        eye_win.close()
                        break


            except Exception as exception:
                logger.error(lang_gui['logger']['error']['extracting_editing'], exception)


        # if file was chosen, stop the loop
        if values['file']:
            break

    # need to destroy the window as it's still open
    start_win.close()

    # layout for loading components Window
    layout1 = [[sg.Text(lang_gui['layout1']['header'])],
               [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progbar')]]

    image_path = values['file']
    # check when no image was chosen
    if not image_path:
        logger.error(lang_gui['logger']['error']['no_image'])
        sys.exit()

    # window for loading of all necessary components
    prog_win = sg.Window(lang_gui['prog_win']['title'], layout1)
    logger.info(lang_gui['logger']['info']['image'], image_path)

    # initializing window and progressbar
    event, values = prog_win.read(timeout=10)
    prog_win['progbar'].update_bar(0)

    # create instance of ExpertEyeglassesRecommender with window callback to update progressbar
    ins = ExpertEyeglassesRecommender(image_path, prog_win, logger, lang=LANGUAGE)
    prog_win['progbar'].update_bar(100)

    # need to destroy the window as it's still open
    prog_win.close()

    # convert image to base64-encoded string, it is necessary to visualize in the main interface
    is_success, buffer = cv2.imencode('.png', cv2.resize(ins._image, (256, 256)))
    logger.debug(lang_gui['logger']['debug']['base64'], is_success)
    b_io = BytesIO(buffer)
    b_io.seek(0)
    b64string = base64.b64encode(b_io.read())

    # lens = "

    # layout for main window
    layout2 = [[sg.Column([[sg.Text(lang_gui['layout2']['header'], font=BIG_FONT, justification="center")],
                           [sg.Text("recommended lens:", font=MEDIUM_FONT)],
                           [sg.Text("right eye: -"+ str(rEye)+"D lens", font=MEDIUM_FONT),sg.Text("left eye: -" + str(lEye) + "D lens", font=MEDIUM_FONT)],


                           [sg.Text("Image:", font=MEDIUM_FONT),sg.Image(data=b64string, size=(256, 256),
                                     pad=(64, 64), key='face_image'),
                            sg.Input(visible=False, enable_events=True, key='file'),
                            sg.FileBrowse(lang_gui['layout2']['update']),button_element(lang_gui['layout2']['extract'], key='extract'),
                            button_element(lang_gui['layout2']['translate'], key='translate'),
                            button_element(lang_gui['layout2']['explain'], key='explain')
                            ],


                           [
                            button_element1(lang_gui['layout2']['generate'], key='generate'),
                            button_element1(lang_gui['layout2']['save'], key='save'),
                               sg.Exit()]],element_justification='c')]]

    # creating main interface
    main_win = sg.Window(lang_gui['main_win']['title'],
                         layout2, resizable=True,
                         grab_anywhere=True, font=SMALL_FONT)

    # graphical interface work in synchronous mode so we need to wait
    # for each event or command in infinite loop
    while True:
        event, values = main_win.read()
        # updating image scenario
        if event == 'file':
            try:
                image_path = values['file']
                # checking if no file was chosen
                if image_path is not None and image_path != '':
                    logger.info(lang_gui['logger']['info']['process'], image_path)
                    # update current image in expert module
                    ins.update_image(image_path)
                    # call to expert module, all vectors will be calculated at this step
                    ins.expert_module()
                    # convert image to base64-encoded string, it is necessary to visualize
                    # in the main interface
                    is_success, buffer = cv2.imencode('.png', cv2.resize(ins._image, (256, 256)))
                    logger.debug(lang_gui['logger']['debug']['base64'], is_success)
                    b_io = BytesIO(buffer)
                    b_io.seek(0)
                    b64string = base64.b64encode(b_io.read())
                    # update image in the interface
                    main_win['face_image'].update(data=b64string, size=(256, 256))
            except Exception as exception:
                logger.error(lang_gui['logger']['error']['update_image'], exception)
        # extracting facial features and update them if necessary
        elif event == 'extract':
            # get current face vector from expert module
            face_vector = ins.get_facevector()
            logger.info(lang_gui['logger']['info']['extract'], face_vector)
            try:
                # layout for face features interface; initialize them here
                # because of the default values of classifiers predictions
                col1 = [[text_element_left(lang_gui['facelayout']['col1']['proprotions'])],
                        [text_element_left(lang_gui['facelayout']['col1']['beard'])],
                        [text_element_left(lang_gui['facelayout']['col1']['cheeckbones'])],
                        [text_element_left(lang_gui['facelayout']['col1']['eyebrowthick'])],
                        [text_element_left(lang_gui['facelayout']['col1']['nose'])],
                        [text_element_left(lang_gui['facelayout']['col1']['eyes'])],
                        [text_element_left(lang_gui['facelayout']['col1']['bangs'])],
                        [text_element_left(lang_gui['facelayout']['col1']['haircolor'])],
                        [text_element_left(lang_gui['facelayout']['col1']['mustache'])],
                        [text_element_left(lang_gui['facelayout']['col1']['paleskin'])]]
                col2 = [[combo_element(key='ratio',
                                       values=('normal', 'wider', 'longer'),
                                       default_value=face_vector['ratio'])],
                        [combo_element(key='beard',
                                       values=('yes', 'no'),
                                       default_value=face_vector['beard'])],
                        [combo_element(key='highcheeckbones',
                                       values=('yes', 'no'),
                                       default_value=face_vector['highcheeckbones'])],
                        [combo_element(key='eyebrows_thickness',
                                       values=('thick', 'thin', 'normal'),
                                       default_value=face_vector['eyebrows_thickness'])],
                        [combo_element(key='nose_size',
                                       values=('big', 'long', 'small'),
                                       default_value=face_vector['nose_size'])],
                        [combo_element(key='eyes_iris',
                                       values=('brown', 'gray', 'green', 'blue'),
                                       default_value=face_vector['eyes_iris'])],
                        [combo_element(key='bangs', values=('yes', 'no'),
                                       default_value=face_vector['bangs'])],
                        [combo_element(key='hair',
                                       values=('black', 'brown', 'grey', 'blonde', 'red'),
                                       default_value=face_vector['hair'])],
                        [combo_element(key='mustache',
                                       values=('yes', 'no'),
                                       default_value=face_vector['mustache'])],
                        [combo_element(key='paleskin',
                                       values=('yes', 'no'),
                                       default_value=face_vector['paleskin'])]]
                col3 = [[text_element_right(lang_gui['facelayout']['col3']['jawtype'])],
                        [text_element_right(lang_gui['facelayout']['col3']['doublechin'])],
                        [text_element_right(lang_gui['facelayout']['col3']['chubby'])],
                        [text_element_right(lang_gui['facelayout']['col3']['eyebrowshape'])],
                        [text_element_right(lang_gui['facelayout']['col3']['narrow_eyes'])],
                        [text_element_right(lang_gui['facelayout']['col3']['forehead'])],
                        [text_element_right(lang_gui['facelayout']['col3']['lips'])],
                        [text_element_right(lang_gui['facelayout']['col3']['bald'])],
                        [text_element_right(lang_gui['facelayout']['col3']['skintone'])],
                        [text_element_right(lang_gui['facelayout']['col3']['sex'])]]
                col4 = [[combo_element(key='jawtype',
                                       values=('soft', 'angular'),
                                       default_value=face_vector['jawtype'])],
                        [combo_element(key='doublechin',
                                       values=('yes', 'no'),
                                       default_value=face_vector['doublechin'])],
                        [combo_element(key='chubby',
                                       values=('yes', 'no'),
                                       default_value=face_vector['chubby'])],
                        [combo_element(key='eyebrows_shape',
                                       values=('flat', 'curly', 'roof', 'angry'),
                                       default_value=face_vector['eyebrows_shape'])],
                        [combo_element(key='eyes_narrow',
                                       values=('yes', 'no'),
                                       default_value=face_vector['eyes_narrow'])],
                        [combo_element(key='forehead',
                                       values=('big', 'notbig'),
                                       default_value=face_vector['forehead'])],
                        [combo_element(key='lips',
                                       values=('big', 'normal'),
                                       default_value=face_vector['lips'])],
                        [combo_element(key='bald',
                                       values=('yes', 'no'),
                                       default_value=face_vector['bald'])],
                        [combo_element(key='skintone',
                                       values=('neutral', 'warm', 'cool'),
                                       default_value=face_vector['skintone'])],
                        [combo_element(key='gender',
                                       values=('female', 'male'),
                                       default_value=face_vector['gender'])]]
                cols = [col1, col2, col3, col4]
                facelayout = [[sg.Text(lang_gui['facelayout']['header'],
                                       font=BIG_FONT)],
                              [sg.Column(col) for col in cols],
                              [button_element(lang_gui['facelayout']['save'])]]

                # create window for correcting images
                face_win = sg.Window(lang_gui['face_win']['title'], facelayout,
                                     auto_size_text=True, grab_anywhere=True, font=SMALL_FONT
                                    ).Finalize()
                face_events, face_values = face_win.read()
                face_win.close()
                logger.debug(lang_gui['logger']['debug']['face_events'], face_events)
                logger.info(lang_gui['logger']['info']['new_face'], face_values)
                for k, v in face_values.items():
                    if k in face_vector:
                        face_vector[k] = v
                # update face vector of corresponding image
                ins.update_facevector(face_vector)

            except Exception as exception:
                logger.error(lang_gui['logger']['error']['extracting_editing'], exception)
        # converting facial features to eyeglasses features
        elif event == 'translate':
            ins.expert_module()
            sg.popup_auto_close('vector created successfully')
        # save already processed results
        elif event == 'save':
            ins.save()
            sg.popup_auto_close('file saved')
        # eyeglasses recommendation's explanation module
        elif event == 'explain':
            try:
                descr = ins.description
            except AttributeError:
                logger.info(lang_gui['logger']['info']['no_description'])
                ins.expert_module()
                descr = ins.description
            logger.info(lang_gui['logger']['info']['explanation'], descr)
            # layout for explanation window
            descrlayout = [[sg.Text(lang_gui['descrlayout']['header'], font=BIG_FONT)],
                           [button_element(lang_gui['descrlayout']['ok'])],
                           [sg.Column([[sg.Text(descr, font=TINY_FONT, auto_size_text=True)]],
                                      scrollable=True)]]
            # layout for explanation window
            explain_win = sg.Window(lang_gui['explain_win']['title'],
                                    descrlayout, auto_size_text=True,
                                    grab_anywhere=True, font=SMALL_FONT).Finalize()
            # Ok or close button pressed
            _ = explain_win.read()
            explain_win.close()
        # top-6 most suitable eyeglasses
        elif event == 'recommend':
            ins.plot_recommendations(block=False)
        # unique eyeglasses with the help of GANs
        elif event == 'generate':
            ins.generate_unique(block=False)
        # exit button or other unexpected user behavior
        else:
            main_win.close()
            # breaking infinite loop, finishing program
            break
