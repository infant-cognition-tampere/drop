'''
Module that contains supplementary functions that are needed to run drop, but
dont necessarily belong to any specific class.
'''

import os
import json


def load_JSON(filename):
    ''' Return data from json-format file. '''

    with open(filename) as data_file:
        data = json.load(data_file)
    return data


def write_fancy_JSON(filename, data):
    ''' Write json so that it is readable by humans (rowchange, indent..). '''

    with open(filename, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)


def to_psychopy_coord(normx, normy):

    psychopyx = normx*2-1
    psychopyy = 2-normy*2-1

    return psychopyx, psychopyy


def unique(valuelist):
    '''
    Returns all the values that are found from a list, but each once only.
    Returns values in sorted order.
    '''

    return sorted(list(set(valuelist)))


def get_list_from_dict(dictionary, key):
    '''
    Get a list from dictionary, if the key not present, return empty list.
    '''

    if key in dictionary:
        return dictionary[key]
    else:
        return []


def is_file_in_filetree(mediadir, medialist):
    ''' Return a list of keys to be given as a parameter on the
    show_message_box. Missing files marked with tag "red".
    '''

    medialist2 = []
    for i in medialist:
        if os.path.isfile(os.path.join(mediadir, i)):
            medialist2.append(i)
        else:
            medialist2.append(["red", i])

    return medialist2


def dircheck(directory):
    ''' Test if the folder exists, if not, generate. '''

    if not os.access(directory, os.R_OK):
        os.makedirs(directory)


def tree_get_first_column_value(treeview):
    '''
    PYGTK support function find selected first column item name from treeview.
    '''

    (model, pathlist) = treeview.get_selection().get_selected_rows()

    # check something was selected
    if len(pathlist) == 0:
        return

    tree_iter = model.get_iter(pathlist[0])
    return model.get_value(tree_iter, 0)


def aoi_from_experiment_to_cairo(aoi):
    ''' Transform aoi from exp coordinates to cairo coordinates. '''

    width = round(aoi[1]-aoi[0], 2)
    height = round(aoi[3]-aoi[2], 2)

    return([aoi[0], aoi[2], width, height])


def aoi_from_experiment_to_psychopy(aoi):
    ''' Trasform aoi from drop coordinates to psychopy coordinates. '''

    width = round(aoi[1]-aoi[0], 2)
    height = round(aoi[3]-aoi[2], 2)
    posx = aoi[0]+width/2
    posy = aoi[2]+height/2
    psychopy_x, psychopy_y = to_psychopy_coord(posx, posy)

    return([psychopy_x, psychopy_y, width*2, height*2])
