"""ExperimentPsychopyView-class."""

import os
import utils
import glib
from psychopy import visual, sound


class ExperimentPsychopyView:
    """Psychopy-view for the experiment-instance."""

    def __init__(self, debug, res, bgcolor, position):
        """Constructor."""
        self.window = self.create_window(debug, res, bgcolor, position)

        self.playing = []
        self.stopped = False
        self.draw_diagnostics = False
        self.volume = 1.0

        # temporarily here
        self.overlay_texts = {}

        glib.idle_add(self.redraw)

    def on_add_draw_que(self, itemid, draw_parameters):
        """Parameters: txt, loc(x,y) 0->1coord, hloc, vloc."""
        self.overlay_texts[itemid] = draw_parameters

    def on_draw_que_updated(self):
        """Callback for on_draw_que_updated."""
        self.overlay_texts = {}

    def stop(self):
        """Method for stopping the experiment."""
        self.stopped = True

    def play(self):
        """Method for starting to play the experiment."""
        self.stopped = False
        glib.idle_add(self.redraw)

    def add_model(self, model):
        """
        Add a model for this view.

        Parameters: model[section-instance handle]
        """
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
        """
        Remove a model from this view.

        Parameters: model[section-instance handle]
        """
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
        """Callback for draw_diagnostics signal."""
        self.draw_diagnostics = do_it

    def on_imagefiles_added(self, mediadir, files):
        """Load list of imagefiles to RAM."""
        self.imageobjects = {}
        for imagef in files:
            himg = self.load_image(self.window, os.path.join(mediadir, imagef))
            self.imageobjects[imagef] = himg

    def on_moviefiles_added(self, mediadir, files):
        """Load list of moviefiles to RAM."""
        self.movieobjects = {}
        for movief in files:
            hmovie = self.load_movie(self.window,
                                     os.path.join(mediadir, movief))
            self.movieobjects[movief] = hmovie

    def on_soundfiles_added(self, mediadir, files):
        """Load list of soundfiles to RAM."""
        self.soundobjects = {}
        for soundf in files:
            hsound = self.load_sound(os.path.join(mediadir, soundf))
            self.soundobjects[soundf] = hsound

    def on_play_image(self, stimname, aoi):
        """Callback for play_image signal."""
        stm = self.imageobjects[stimname]
        self.play_image(stm, aoi)
        self.playing.append(stm)

    def on_play_movie(self, stimname, aoi):
        """Callback for play_movie signal."""
        stm = self.movieobjects[stimname]
        self.play_movie(stm, aoi)
        self.playing.append(stm)

    def on_play_sound(self, stimname):
        """Callback for play_sound signal."""
        stm = self.soundobjects[stimname]
        stm.play()
        self.playing.append(stm)

    def redraw(self):
        """Drawing loop."""
        if not self.stopped:
            # draw frames from movies and pictures
            for i in self.playing:
                if i.__class__.__name__ == 'MovieStim3':
                    i.draw()
                elif i.__class__.__name__ == 'ImageStim':
                    i.draw()

            if self.draw_diagnostics:
                self.draw_overlay_texts()

            self.window.flip()

            glib.idle_add(self.redraw)

        return False

    def on_stimuli_cleared(self):
        """Close all running stimuli."""
        for k in self.playing:
            if k.__class__.__name__ == 'MovieStim3':
                k.seek(0)  # go start # errors some times
                k.pause()
                # k.autoDraw = False

            elif k.__class__.__name__ == 'SoundStim':
                k.stop()
            else:
                # imageobject
                k.autoDraw = False

        self.playing = []

    def draw_overlay_texts(self):
        """Draw all elements in the que. Draws by order of the list."""
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

    def create_window(self, debug, res, bgcolor, position):
        """Create a window for the experiment. Debug[bool]:windowed mode."""
        res_ratio = float(res[1])/float(res[0])

        if debug:
            return visual.Window(size=(500, res_ratio*500), pos=(200, 300),
                                 color=bgcolor)
        else:
            return visual.Window(screen=1,  size=(res[0], res[1]),
                                 allowGUI=False, color=bgcolor,
                                 pos=position)

    def load_movie(self, window, filepath):
        """Load a moviefile to RAM tied to specified window."""
        movieobject = visual.MovieStim3(window, filepath, loop=True)
        movieobject.units = "norm"

        return movieobject

    def load_image(self, window, filepath):
        """Load ann imagefile to RAM tied to specified window."""
        return visual.ImageStim(window, image=filepath)

    def load_sound(self, filepath):
        """Load a soundfile to RAM."""
        return sound.Sound(value=filepath)

    def play_movie(self, movieobject, aoi):
        """Start playing movie."""
        # Transfer to psychopy coordinates (-1->1, 1->-1)
        # from normalized (0->1, 0->1)
        p_x, p_y, width, height = utils.aoi_from_experiment_to_psychopy(aoi)

        movieobject.play()

        movieobject.pos = (p_x, p_y)
        movieobject.size = [width, height]
        movieobject.draw()
        # stm.autoDraw = True

    def play_image(self, imageobject, aoi):
        """Start playing image."""
        p_x, p_y, width, height = utils.aoi_from_experiment_to_psychopy(aoi)

        imageobject.pos = (p_x, p_y)
        imageobject.size = [width, height]
        imageobject.draw()
        # stm.autoDraw = True

    def __del__(self):
        """Destructor."""
        self.stopped = True
        self.window.close()
        self.window = None
