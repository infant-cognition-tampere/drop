''' ExperimentPsychopyView-class. '''

import os
import utils
import glib
from psychopy import visual, sound


class ExperimentPsychopyView:

    def __init__(self, debug):

        self.window = self.create_window(debug)

        self.playing = []
        self.stopped = False
        self.draw_diagnostics = False
        self.volume = 1.0

        # temporarily here
        self.overlay_texts = {}

        glib.idle_add(self.redraw)

    def on_add_draw_que(self, itemid, draw_parameters):
        ''' parameters: txt, loc(x,y) 0->1coord, hloc, vloc. '''

        self.overlay_texts[itemid] = draw_parameters

    def on_draw_que_updated(self):
        self.overlay_texts = {}

    def stop(self):
        self.stopped = True

    def play(self):
        self.stopped = False
        glib.idle_add(self.redraw)

    def add_model(self, model):

        model.on("imagefiles_added", self.on_imagefiles_added)
        model.on("moviefiles_added", self.on_moviefiles_added)
        model.on("soundfiles_added", self.on_soundfiles_added)
        model.on("play_image", self.on_play_image)
        model.on("play_movie", self.on_play_movie)
        model.on("play_sound", self.on_play_sound)
        model.on("stimuli_cleared", self.on_stimuli_cleared)
        model.on("draw_diagnostics", self.on_draw_diagnostics)
        model.on("add_draw_que", self.on_add_draw_que)
        model.on("draw_que_updated", self.on_draw_que_updated)

    def remove_model(self, model):

        model.remove_listener("imagefiles_added", self.on_imagefiles_added)
        model.remove_listener("moviefiles_added", self.on_moviefiles_added)
        model.remove_listener("soundfiles_added", self.on_soundfiles_added)
        model.remove_listener("play_image", self.on_play_image)
        model.remove_listener("play_movie", self.on_play_movie)
        model.remove_listener("play_sound", self.on_play_sound)
        model.remove_listener("stimuli_cleared", self.on_stimuli_cleared)
        model.remove_listener("draw_diagnostics", self.on_draw_diagnostics)
        model.remove_listener("add_draw_que", self.on_add_draw_que)
        model.remove_listener("draw_que_updated", self.on_draw_que_updated)

    def on_draw_diagnostics(self, do_it):
        self.draw_diagnostics = do_it

    def on_imagefiles_added(self, mediadir, files):
        ''' Load list of imagefiles to RAM. '''

        self.imageobjects = []
        for imagef in files:
            himg = self.load_image(self.window, os.path.join(mediadir, imagef))
            self.imageobjects.append(himg)

    def on_moviefiles_added(self, mediadir, files):
        ''' Load list of moviefiles to RAM. '''

        self.movieobjects = []
        for movief in files:
            hmovie = self.load_movie(self.window,
                                     os.path.join(mediadir, movief))
            self.movieobjects.append(hmovie)

    def on_soundfiles_added(self, mediadir, files):
        ''' Load list of soundfiles to RAM. '''

        self.soundobjects = []
        for soundf in files:
            hsound = self.load_sound(os.path.join(mediadir, soundf))
            self.soundobjects.append(hsound)

    def on_play_image(self, stimnum, aoi):
        stm = self.imageobjects[stimnum]
        self.play_image(stm, aoi)
        self.playing.append(stm)

    def on_play_movie(self, stimnum, aoi):
        stm = self.movieobjects[stimnum]
        self.play_movie(stm, aoi)
        self.playing.append(stm)

    def on_play_sound(self, stimnum):
        stm = self.soundobjects[stimnum]
        self.play_sound(stm)
        self.playing.append(stm)

    def redraw(self):
        ''' Drawing loop. '''

        if not self.stopped:
            # draw frames from movies and pictures
            for i in self.playing:
                if i.__class__.__name__ == 'MovieStim':
                    self.draw_movie(i)
                elif i.__class__.__name__ == 'ImageStim':
                    self.draw_image(i)

            if self.draw_diagnostics:
                self.draw_overlay_texts()

            self.window.flip()

            glib.idle_add(self.redraw)

        return False

    def on_stimuli_cleared(self):
        ''' Close all running stimuli. '''

        for k in self.playing:
            if k.__class__.__name__ == 'MovieStim':
                # movieobject
                self.stop_movie(k)
            elif k.__class__.__name__ == 'SoundStim':
                # soundobject
                self.stop_sound(k)
            else:
                # imageobject
                self.stop_image(k)

        self.playing = []

    def draw_overlay_texts(self):
        '''
        Draws all elements in the self.draw_elements que on self.window.
        Will draw in order of appearance in the list.
        '''

        ystartloc = 0.95
        # loop through all the elements
        for key in self.overlay_texts:
            item = self.overlay_texts[key]
            itype = item["type"]

            if itype == "text":
                htxt = visual.TextStim(self.window, text=item["txt"],
                                       pos=(-0.95, ystartloc),
                                       alignHoriz="left", alignVert="center")
                htxt.draw()
                ystartloc = ystartloc-0.1
            elif itype == "circle":
                x, y = utils.to_psychopy_coord(item["x"], item["y"])
                htxt = visual.TextStim(self.window, text="o", pos=(x, y),
                                       alignHoriz="center", alignVert="center")
                htxt.draw()

    def create_window(self, debug):

        res = [1024, 768]
        res_ratio = float(res[1])/float(res[0])

        if debug:
            return visual.Window(size=(500, res_ratio*500), pos=(200, 300))
        else:
            return visual.Window(screen=1,  size=(res[0], res[1]),
                                 fullscr=True, allowGUI=False)

    def load_movie(self, window, filepath):
        # loads a moviefile to RAM tied to specified window

        movieobject = visual.MovieStim(window, filepath)
        movieobject.units = "norm"
        movieobject.loop = True

        return movieobject

    def load_image(self, window, filepath):
        # loads ann imagefile to RAM tied to specified window

        return visual.ImageStim(window, image=filepath)

    def load_sound(self, filepath):
        # loads a soundfile to RAM
        return sound.SoundPygame(value=filepath)

    def play_sound(self, soundobject):
        # makes the sound "play"
        soundobject.play()

    def play_movie(self, movieobject, aoi):
        '''
        Transfer to psychopy coordinates (-1->1, 1->-1)
        from normalized (0->1, 0->1)
        '''

        p_x, p_y, width, height = utils.aoi_from_experiment_to_psychopy(aoi)

        movieobject.play()

        movieobject.pos = (p_x, p_y)
        movieobject.size = [width, height]
        # stm.autoDraw = True
        movieobject.draw()

    def play_image(self, imageobject, aoi):
        p_x, p_y, width, height = utils.aoi_from_experiment_to_psychopy(aoi)

        imageobject.pos = (p_x, p_y)
        imageobject.size = [width, height]
        # stm.autoDraw = True
        imageobject.draw()

    def draw_image(self, imageobject):
        imageobject.draw()

    def draw_movie(self, movieobject):
        movieobject.draw()

    def stop_movie(self, movieobject):
        movieobject.seek(0)  # go start # errors some times
        movieobject.pause()
        # movieobject.autoDraw = False

    def stop_image(self, imageobject):
        imageobject.autoDraw = False

    def stop_sound(self, soundobject):
        soundobject.stop()

    def __del__(self):

        self.stopped = True
        self.window.close()
        self.window = None
