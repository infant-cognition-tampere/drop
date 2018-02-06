"""Module that contains supplementary functions that are needed to run drop."""

import os
import json


def load_JSON(filename):
    """Return data from json-format file."""
    with open(filename) as data_file:
        data = json.load(data_file)
    return data


def write_fancy_JSON(filename, data):
    """Write json so that it is readable by humans (rowchange, indent..)."""
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)


def to_psychopy_coord(normx, normy):
    """Transform coordinates from normalized to psychopy-format."""
    psychopyx = normx*2-1
    psychopyy = 2-normy*2-1

    return psychopyx, psychopyy


def unique(valuelist):
    """Return all values found from a list, but each once only and sorted."""
    return sorted(list(set(valuelist)))


def get_list_from_dict(dictionary, key):
    """Get a list from dictionary, if key not present, return empty list."""
    if key in dictionary:
        return dictionary[key]
    else:
        return []


def is_file_in_filetree(mediadir, medialist):
    """Return a list of keys. Missing files marked with tag "red"."""
    # TODO:function parameters and return values a bit unclear
    medialist2 = []
    for i in medialist:
        if os.path.isfile(os.path.join(mediadir, i)):
            medialist2.append(i)
        else:
            medialist2.append(["red", i])

    return medialist2


def dircheck(directory):
    """Test if the folder exists, if not, generate."""
    if not os.access(directory, os.R_OK):
        os.makedirs(directory)


def tree_get_first_column_value(treeview):
    """Find selected first column item name from treeview (PYGTK-specific)."""
    (model, pathlist) = treeview.get_selection().get_selected_rows()

    # check something was selected
    if len(pathlist) == 0:
        return

    tree_iter = model.get_iter(pathlist[0])
    return model.get_value(tree_iter, 0)


def aoi_from_experiment_to_cairo(aoi):
    """Transform aoi from exp coordinates to cairo coordinates."""
    width = round(aoi[1]-aoi[0], 2)
    height = round(aoi[3]-aoi[2], 2)

    return([aoi[0], aoi[2], width, height])


def aoi_from_experiment_to_psychopy(aoi):
    """Trasform aoi from drop coordinates to psychopy coordinates."""
    width = round(aoi[1]-aoi[0], 2)
    height = round(aoi[3]-aoi[2], 2)
    posx = aoi[0]+width/2
    posy = aoi[2]+height/2
    psychopy_x, psychopy_y = to_psychopy_coord(posx, posy)

    return([psychopy_x, psychopy_y, width*2, height*2])


def recursive_indexing(indstr, hashtable, index):
    """
    Recursive indexing with a string pointing dict.

    Delimiter "->"
    No nested indexing.
    indstr = pointer string e.g. "a->b->c" cut by split("->") to list of str
    hashtable = "dictionary" that contains the variables and tables
    index = number, that indexes the list in hashtable where pointer points
    """
    if len(indstr) == 1:

        htelement = hashtable[indstr[0]]
        # process if the htelement is a list or constant..
        # list returns list element [index], constant returns constant
        if type(htelement) is list:
            return htelement[index]
        else:
            return htelement
    else:
        string = indstr.pop(0)
        if string.isdigit():
            # the string was a number -> reference with the number
            newindex = int(string)
        else:
            newindex = hashtable[string][index]

        return recursive_indexing(indstr, hashtable, newindex)


def list_depth(l):
    """Return the depth of the FIRST (0) element of lists inside lists."""
    if type(l) is list:
        if len(l) > 0:
            return 1 + list_depth(l[0])
        else:
            return 1
    else:
        return 0
