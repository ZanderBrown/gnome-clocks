# Copyright(c) 2011-2012 Collabora, Ltd.
#
# Gnome Clocks is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or(at your
# option) any later version.
#
# Gnome Clocks is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with Gnome Clocks; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# Author: Seif Lotfy <seif.lotfy@collabora.co.uk>

import time
from gi.repository import Gtk, GObject
from clocks import Clock


class Stopwatch(Clock):
    LABEL_MARKUP = "<span font_desc=\"64.0\">%02i:%04.1f</span>"
    BUTTON_MARKUP = "<span font_desc=\"18.0\">%s</span>"

    class State:
        RESET = 0
        RUNNING = 1
        STOPPED = 2

    def __init__(self):
        Clock.__init__(self, _("Stopwatch"))

        self.state = Stopwatch.State.RESET
        self.timeout_id = 0
        self.start_time = 0
        self.time_diff = 0

        grid = Gtk.Grid()
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_valign(Gtk.Align.CENTER)
        grid.set_row_spacing(48)
        grid.set_column_spacing(24)
        grid.set_column_homogeneous(True)
        self.add(grid)

        self.time_label = Gtk.Label()
        # add margin to match the spinner size in the timer
        self.time_label.set_margin_top(42)
        self.time_label.set_margin_bottom(42)
        self.set_time_label(0, 0)
        grid.attach(self.time_label, 0, 0, 2, 1)

        self.left_button = Gtk.Button()
        self.left_button.set_size_request(200, -1)
        self.left_label = Gtk.Label()
        self.left_label.set_markup(Stopwatch.BUTTON_MARKUP % (_("Start")))
        self.left_button.add(self.left_label)
        self.left_button.get_style_context().add_class("clocks-go")
        grid.attach(self.left_button, 0, 1, 1, 1)

        self.right_button = Gtk.Button()
        self.right_button.set_size_request(200, -1)
        self.right_label = Gtk.Label()
        self.right_label.set_markup(Stopwatch.BUTTON_MARKUP % (_("Reset")))
        self.right_button.add(self.right_label)
        self.right_button.set_sensitive(False)
        grid.attach(self.right_button, 1, 1, 1, 1)

        self.left_button.connect("clicked", self._on_left_button_clicked)
        self.right_button.connect("clicked", self._on_right_button_clicked)

    def _on_left_button_clicked(self, widget):
        if self.state in (Stopwatch.State.RESET, Stopwatch.State.STOPPED):
            self.state = Stopwatch.State.RUNNING
            self.start()
            self.left_label.set_markup(Stopwatch.BUTTON_MARKUP % (_("Stop")))
            self.left_button.get_style_context().add_class("clocks-stop")
            self.right_button.set_sensitive(False)
        elif self.state == Stopwatch.State.RUNNING:
            self.state = Stopwatch.State.STOPPED
            self.stop()
            self.left_label.set_markup(Stopwatch.BUTTON_MARKUP % (_("Continue")))
            self.right_label.set_markup(Stopwatch.BUTTON_MARKUP % (_("Reset")))
            self.left_button.get_style_context().remove_class("clocks-stop")
            self.left_button.get_style_context().add_class("clocks-go")
            self.right_button.set_sensitive(True)

    def _on_right_button_clicked(self, widget):
        if self.state == Stopwatch.State.RUNNING:
            pass
        if self.state == Stopwatch.State.STOPPED:
            self.state = Stopwatch.State.RESET
            self.time_diff = 0
            self.left_label.set_markup(Stopwatch.BUTTON_MARKUP % (_("Start")))
            self.left_button.get_style_context().add_class("clocks-go")
            self.right_button.set_sensitive(False)
            self.set_time_label(0, 0)

    def get_time(self):
        timediff = time.time() - self.start_time + self.time_diff
        m, s = divmod(timediff, 60)
        return (m, s)

    def set_time_label(self, m, s):
        self.time_label.set_markup(Stopwatch.LABEL_MARKUP % (m, s))

    def start(self):
        if self.timeout_id == 0:
            self.start_time = time.time()
            self.timeout_id = GObject.timeout_add(100, self.count)

    def stop(self):
        GObject.source_remove(self.timeout_id)
        self.timeout_id = 0
        self.time_diff = self.time_diff + (time.time() - self.start_time)

    def reset(self):
        GObject.source_remove(self.timeout_id)
        self.timeout_id = 0
        self.time_diff = 0

    def count(self):
        (m, s) = self.get_time()
        self.set_time_label(m, s)
        return True
