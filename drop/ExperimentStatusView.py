"""ExperimentStatusView-class."""

import gtk
import cairo
import math
import glib
import utils


class ExperimentStatusView(gtk.DrawingArea):
    """A view for experiment that provides information to the observer."""

    def __init__(self, controller):
        """Constructor."""
        gtk.DrawingArea.__init__(self)
        self.controller = controller
        self.refresh_interval = 50  # ms
        self.set_size_request(200, 120)
        self.connect("expose_event", self.on_expose)
        self.latest_gui_update = 0
        self.draw_que = {}

        # indicator tresholds
        self.green_thresh = 0.8
        self.yellow_thresh = 0.5

        # initiate trackstatus loop
        glib.idle_add(self.redraw)

    def add_model(self, model):
        """Add a model to the view."""
        model.on("play_image", self.on_play_image)
        model.on("play_movie", self.on_play_movie)
        model.on("data_condition_added", self.on_data_condition_added)
        # model.on("clear_draw_que", self.on_clear_draw_que)
        model.on("draw_que_updated", self.clear_draw_que)
        model.on("phase_ended", self.clear_draw_que)
        model.on("add_draw_que", self.add_draw_que)
        model.on("trial_completed", self.on_trial_completed)
        model.on("metric_threshold_updated", self.on_threshold_updated)

    def remove_model(self, model):
        """Add a model to the view."""
        model.remove_listener("play_image", self.on_play_image)
        model.remove_listener("play_movie", self.on_play_movie)
        model.remove_listener("data_condition_added",
                              self.on_data_condition_added)
        # model.remove_listener("clear_draw_que", self.on_clear_draw_que)
        model.remove_listener("draw_que_updated", self.clear_draw_que)
        model.remove_listener("phase_ended", self.clear_draw_que)
        model.remove_listener("add_draw_que", self.add_draw_que)
        model.remove_listener("trial_completed", self.on_trial_completed)
        model.remove_listener("metric_threshold_updated",
                              self.on_threshold_updated)

    def on_threshold_updated(self, thresholds):
        """Callback for threshold_updated signal."""
        self.green_thresh = thresholds[1]
        self.yellow_thresh = thresholds[0]

    def on_trial_completed(self, a, b, c, d):
        """Callback for the trial_completed signal."""
        self.draw_que = {}

    def on_data_condition_added(self, datacondition):
        """Callback for data_condition_added signal."""
        if datacondition["type"] == "aoi":
            # just put something for the unique identifier
            key = "wgc_aoi" + str(len(self.draw_que))
            self.draw_que[key] = {"type": "aoi", "r": 0, "g": 0, "b": 1,
                                  "o": 1, "aoi": datacondition["aoi"]}

    def on_play_image(self, stmnum, aoi):
        """Callback for play_image signal."""
        self.draw_que["maoi"+str(stmnum)] = {"type": "aoi", "r": 0, "g": 1,
                                             "b": 0, "o": 1, "aoi": aoi}

    def on_play_movie(self, stmnum, aoi):
        """Callback for play_movie signal."""
        self.draw_que["iaoi"+str(stmnum)] = {"type": "aoi", "r": 0, "g": 1,
                                             "b": 0, "o": 1, "aoi": aoi}

    def add_draw_que(self, itemid, draw_parameters):
        """Add elements to be drawn on the trackstatus canvas."""
        self.draw_que[itemid] = draw_parameters

    def clear_draw_que(self):
        """Clear all draw-elements."""
        self.draw_que = {}

    def remove_draw_que(self, key):
        """
        Remove element from the trackstatus canvas.

        Parameter is an id of the
        element. Reserved word: "all" clears everything from the queue.
        """
        if key in self.draw_que:
            self.draw_que.pop(key)

    def redraw(self):
        """Callback for the idle_add drawing-loop."""
        if self.window:
            alloc = self.get_allocation()
            rect = gtk.gdk.Rectangle(0, 0, alloc.width, alloc.height)
            self.window.invalidate_rect(rect, True)
            self.window.process_updates(True)

    def draw(self, ctx):
        """Draw the canvas."""
        # wallpaper
        ctx.set_source_rgb(0., 0., 0.)
        ctx.rectangle(0, 0, 1, 1)  # (0, 0, 1, .9)
        ctx.fill()

        # draw all the active aois to observer window
        # draw the information from controller to the trackstatus-window
        ctx.set_line_width(0.005)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        txtstart = 0.05
        for i in sorted(self.draw_que):
            item = self.draw_que[i]

            if "r" and "g" and "b" and "o" in item:
                ctx.set_source_rgba(item["r"], item["g"], item["b"], item["o"])

            itype = item["type"]
            if itype == "rect":
                # get all the extra information to be presented
                aoi = utils.aoi_from_experiment_to_cairo(item["aoi"])

                # draw the rectangle
                ctx.rectangle(aoi[0], aoi[1], aoi[2], aoi[3])
                ctx.fill()

            elif itype == "aoi":

                # check if aoi is circular or rect
                if len(item["aoi"]) == 3:
                    # circle
                    ctx.arc(item["aoi"][0], item["aoi"][1], item["aoi"][2],
                            0, 2 * math.pi)
                    ctx.stroke()
                else:
                    # rectangular
                    # get all the extra information to be presented
                    aoi = utils.aoi_from_experiment_to_cairo(item["aoi"])

                    # draw the rectangle
                    ctx.rectangle(aoi[0], aoi[1], aoi[2], aoi[3])
                    ctx.stroke()

            elif itype == "circle":
                ctx.arc(item["x"], item["y"], item["radius"], 0, 2 * math.pi)
                ctx.fill()

            elif itype == "text":
                txt = item["txt"]
                ctx.set_source_rgb(0.0, 1.0, 0.0)
                ctx.set_font_size(0.05)
                ctx.move_to(0.01, txtstart)
                ctx.show_text(txt)
                txtstart += 0.05

            elif itype == "metric":
                values = item["values"]

                if len(values) > 0:
                    width = 0.3
                    xincrement = width/len(values)
                    xstart = 0.01
                    for v in values:

                        if self.green_thresh <= v:
                            ctx.set_source_rgba(0, 1, 0, 1)
                        elif self.yellow_thresh <= v and v < self.green_thresh:
                            ctx.set_source_rgba(1, 1, 0, 1)
                        elif 0 <= v and v < self.yellow_thresh:
                            ctx.set_source_rgba(1, 0, 0, 1)
                        elif v == -1:
                            ctx.set_source_rgba(0.5, 0.5, 0.5, 1.0)

                        ctx.rectangle(xstart, txtstart-0.03, xincrement, 0.03)
                        ctx.fill()
                        xstart += xincrement
                    txtstart += 0.05

        glib.timeout_add(self.refresh_interval, self.redraw)

    def stop(self):
        """Some other views might want to stop loops."""
        return False

    def on_expose(self, widget, event):
        """Callback for expose_event."""
        context = widget.window.cairo_create()
        context.rectangle(event.area.x, event.area.y, event.area.width,
                          event.area.height)
        context.clip()

        rect = widget.get_allocation()
        context.scale(rect.width, rect.height)

        self.draw(context)
        return False
