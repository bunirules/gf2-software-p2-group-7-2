"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
from pathlib import Path
import sys

import numpy as np
import wx
import wx.lib.dialogs
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from PIL import Image
from PIL import ImageOps

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, names=None, signals=None, swap=True): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, monitors):
        """Initialise canvas properties and useful variables.

        Arguments:
            parent -- parent window.
            monitors -- instance of the monitors.Monitors() class.
        """
        super().__init__(
            parent,
            -1,
            attribList=[
                wxcanvas.WX_GL_RGBA,
                wxcanvas.WX_GL_DOUBLEBUFFER,
                wxcanvas.WX_GL_DEPTH_SIZE,
                16,
                0,
            ],
        )
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # remember signals to draw when rendering
        self.name_list = None
        self.signal_list = None

        self.parent = parent

        # initialise monitors
        self.monitors = monitors

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    def render(self, names=None, signals=None, swap=True):
        """Handle all drawing operations.

        Keyword Arguments:
            names -- names of monitor points (default: {None})
            signals -- signals at the monitor points (default: {None})
            swap -- determines whether to run SwapBuffers (default: {True})
        """
        self.SetCurrent(self.context)

        # get dimensions of full plot area
        self.set_max_dims(names, signals)

        # get width and height of visible window
        self.width, self.height = self.GetClientSize()

        # limit pan to sensible region
        self.limit_pan()

        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw signals
        if signals is not None:
            self.name_list = names  # save name list for rendering
            self.signal_list = signals  # save signal list for rendering
            n = len(signals)

            # set vertical spacing for signals on canvas
            heights = np.linspace(30, 30 + 75 * (n - 1), n)

            # for each signal in the signal list
            for n, signal in enumerate(signals):
                if len(signal) > 0:
                    # draw 0 and 1 to show signal level
                    self.render_text("0", 10, heights[n] - 5)
                    self.render_text("1", 10, heights[n] + 15)
                # draw ticks every 10 timesteps
                for i in range(1, (len(signal)) // 10 + 1):
                    self.render_text(
                        f"{int(i*10)}", i * 100 + 10, heights[n] - 16
                    )
                    GL.glColor3f(0.0, 0.0, 0.0)  # ticks are black
                    GL.glBegin(GL.GL_LINE_STRIP)
                    x = (i * 100) + 20
                    y = heights[n]
                    y_next = heights[n] - 5
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x, y_next)
                    GL.glEnd()
                self.render_text(
                    names[n], -self.pan_x / self.zoom + 10, heights[n] + 35
                )
                if len(signal) >= 20:  # draw 0 and 1 at end of signal
                    self.render_text(
                        "0", len(signal) * 10 + 30, heights[n] - 5
                    )
                    self.render_text(
                        "1", len(signal) * 10 + 30, heights[n] + 15
                    )

                # draw signals
                GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
                GL.glBegin(GL.GL_LINE_STRIP)
                for i, output in enumerate(signal):
                    x = (i * 10) + 20
                    x_next = (i * 10) + 30
                    if output == 0:  # signal is low
                        y = heights[n]
                        y_next = heights[n]
                        GL.glVertex2f(x, y)
                        GL.glVertex2f(x_next, y_next)
                    elif output == 1:  # signal is high
                        y = heights[n] + 20
                        y_next = heights[n] + 20
                        GL.glVertex2f(x, y)
                        GL.glVertex2f(x_next, y_next)
                    elif output == 2:  # signal is rising
                        y = heights[n]
                        y_next = heights[n] + 20
                        GL.glVertex2f(x, y)
                        GL.glVertex2f(x_next, y_next)
                    elif output == 3:  # signal is falling
                        y = heights[n] + 20
                        y_next = heights[n]
                        GL.glVertex2f(x, y)
                        GL.glVertex2f(x_next, y_next)
                    elif output == 4:  # signal is blank
                        pass
                GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        if swap:
            GL.glFlush()
            self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event.

        Arguments:
            event -- Event which triggers the painting
        """
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        self.render(self.name_list, self.signal_list)

    def on_size(self, event):
        """Handle the canvas resize event.

        Arguments:
            event -- Event which causes the canvas to resize.
        """
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events.

        Arguments:
            event -- event which causes mouse to die
        """
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
        if event.GetWheelRotation() < 0:
            self.zoom *= 1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())
            )
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
        if event.GetWheelRotation() > 0:
            self.zoom /= 1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())
            )
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False

        self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        # print characters in text
        for character in text:
            if character == "\n":
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def set_max_dims(self, names, signals):
        """Find dimensions of full plot.

        Arguments:
            names -- list of monitor points
            signals -- list of signals at monitored points
        """
        # find full length of plot in x-direction
        try:
            self.max_x = len(signals[0]) * 10 + 45
        except Exception:
            try:
                self.max_x = 25 + max([len(name) for name in names])
            except Exception:
                self.max_x = 20
        self.max_x *= self.zoom

        # find full length of plot in y-direction
        try:
            self.max_y = 10 + 75 * len(signals)
        except Exception:
            self.max_y = 0
        self.max_y *= self.zoom

    def limit_pan(self):
        """Limits x and y positions to sensible range."""
        if self.pan_x > 0:  # limit x to not go too far left
            self.pan_x = 0
            self.init = False
        elif (
            self.width > self.max_x
        ):  # set x to zero if displaying full x-axis
            self.pan_x = 0
            self.init = False
        elif (
            self.width - self.pan_x > self.max_x and self.width < self.max_x
        ):  # limit x to not go too far right
            self.pan_x = self.width - self.max_x
            self.init = False

        if self.pan_y > 0:  # limit y to not go too far down
            self.pan_y = 0
            self.init = False
        elif (
            self.height > self.max_y
        ):  # set y to zero if displaying full y-axis
            self.pan_y = 0
            self.init = False
        elif (
            self.height - self.pan_y > self.max_y and self.height < self.max_y
        ):  # limit y to not go too far up
            self.pan_y = self.height - self.max_y
            self.init = False

        if (
            self.width < self.max_x
        ):  # show scrollbar if plot larger that visible x-axis
            self.parent.horizontal_scrollbar.SetScrollbar(
                -self.pan_x, self.width, self.max_x, self.width
            )
            self.parent.horizontal_scrollbar.Show()
        else:
            self.parent.horizontal_scrollbar.Hide()

        if (
            self.height < self.max_y
        ):  # show scrollbar if plot larger that visible y-axis
            self.parent.vertical_scrollbar.SetScrollbar(
                self.pan_y - self.height + self.max_y,
                self.height,
                self.max_y,
                self.height,
            )
            self.parent.vertical_scrollbar.Show()
        else:
            self.parent.vertical_scrollbar.Hide()

    def set_view(self, x=0, y=0, zoom=1):
        """Set view to given position.

        Keyword Arguments:
            x -- x coordinate (default: {0})
            y -- y coordinate (default: {0})
            zoom -- zoom value (default: {1})
        """
        self.init = False
        self.pan_x = x
        self.pan_y = y
        self.zoom = zoom
        self.render(self.name_list, self.signal_list)

    def save_image(self, full):
        """Get image data from canvas.

        Arguments:
            full -- whether full plot is wanted

        Returns:
            Image data to save
        """
        width, height = self.GetClientSize()
        if full:  # set canvas to full plot size
            x, y = self.pan_x, self.pan_y
            zoom = self.zoom

            self.pan_x, self.pan_y = 0, 0
            self.zoom = 1

            self.SetSize((self.max_x / zoom, self.max_y / zoom))
            self.init = False
            self.render(self.name_list, self.signal_list, swap=False)

        # get pixel data
        data = GL.glReadPixels(
            0,
            0,
            self.width,
            self.height,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
        )
        image = Image.frombytes("RGBA", (self.width, self.height), data)

        if full:  # go back to previous canvas layout
            self.pan_x = x
            self.pan_y = y
            self.zoom = zoom

            self.SetSize((width, height))
            self.init = False
            self.render(self.name_list, self.signal_list, swap=False)
        return ImageOps.flip(image)


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.
    path: path to circuit definition file
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout.

        Arguments:
            title -- title of the window.
            path -- path to circuit definition file
            names -- instance of the names.Names() class.
            devices -- instance of the devices.Devices() class.
            network -- instance of the network.Network() class.
            monitors -- instance of the monitors.Monitors() class.
        """
        super().__init__(parent=None, title=title, size=(1200, 600))

        # initialise network variables
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network

        self.cycles_completed = 0  # number of simulation cycles completed
        self.num_cycles_requested = (
            10  # number of simulation cycles requested by user
        )

        # store which signals are monitored and not monitored
        self.monitored_list = self.monitors.get_signal_names()[0]
        self.not_monitored_list = self.monitors.get_signal_names()[1]

        # list of all input names in network
        self.input_names_list = sorted(self.get_input_names())

        # list of all output names in network
        self.output_names_list = sorted(
            self.monitored_list + self.not_monitored_list
        )

        # list of all connection names in network
        self.conn_name_list = self.get_conn_names()

        # list of all switch IDs in network
        self.switch_list = self.devices.find_devices(self.devices.SWITCH)

        # list of all switch names in network
        self.switch_names = [
            self.names.get_name_string(switch) for switch in self.switch_list
        ]

        # list of the states of the switches in the network
        self.switch_states = [
            self.devices.get_device(switch).switch_state
            for switch in self.switch_list
        ]

        # store the signals and names that are being monitored
        self.signal_list = []
        self.name_list = []

        # initialise tracking variables
        self.add_monitor = ""  # monitor name to add
        self.zap_monitor = ""  # monitor name to remove
        self.switch_to_toggle = ""  # name of switch to toggle
        self.switch_to_toggle_state = None  # state of switch to toggle
        self.switch_to_toggle_selection = None  # index of switch to toggle
        self.input_for_swap = None  # input to swap connection for
        self.output_for_swap = None  # output to swap connection for

        # Configure the menu bar
        self.menuBar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(
            wx.ID_ABOUT, _(_("About"))
        )
        self.fileMenu.Append(
            wx.ID_OPEN, _(_("Open File"))
        )
        self.saveMenu = wx.Menu()
        self.saveMenu.Append(
            wx.ID_SAVE,
            _(_("Save Visible Plot Area")),
        )
        self.saveMenu.Append(
            wx.ID_SAVEAS, _(_("Save Full Plot"))
        )
        self.fileMenu.AppendSubMenu(
            self.saveMenu, _(_("Save Image"))
        )
        self.fileMenu.Append(
            wx.ID_EXIT, _(_("Exit"))
        )
        self.menuBar.Append(
            self.fileMenu, _(_("File"))
        )
        self.viewMenu = wx.Menu()
        self.viewMenu.Append(
            wx.ID_RESET, _(_("Reset View"))
        )
        self.menuBar.Append(
            self.viewMenu, _(_("View"))
        )
        self.SetMenuBar(self.menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, monitors)

        # Configure the widgets
        self.text_run = wx.StaticText(
            self,
            wx.ID_ANY,
            _(_("Cycles to run/continue for:")),
        )
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10", max=1000, min=1)
        self.run_button = wx.Button(
            self, wx.ID_ANY, _(_("Run"))
        )
        self.restart_button = wx.Button(
            self, wx.ID_ANY, _(_("Restart"))
        )
        self.text_add_mon = wx.StaticText(
            self,
            wx.ID_ANY,
            _(_("Select a monitor point to add:")),
        )
        self.add_box = wx.Choice(
            self,
            wx.ID_ANY,
            choices=self.not_monitored_list,
        )
        self.add_button = wx.Button(
            self, wx.ID_ANY, _(_("Add"))
        )
        self.text_zap_mon = wx.StaticText(
            self,
            wx.ID_ANY,
            _(
                _("Select a monitor point to remove:")
            ),
        )
        self.zap_box = wx.Choice(
            self,
            wx.ID_ANY,
            choices=self.monitored_list,
        )
        self.zap_button = wx.Button(
            self, wx.ID_ANY, _(_("Remove"))
        )
        self.text_switch = wx.StaticText(
            self,
            wx.ID_ANY,
            _(_("Select a switch to toggle:")),
        )
        self.switch_box = wx.Choice(self, wx.ID_ANY, choices=self.switch_names)
        self.toggle_0 = wx.ToggleButton(self, wx.ID_ANY, label="0")
        self.toggle_1 = wx.ToggleButton(self, wx.ID_ANY, label="1")
        self.replace_text_1 = wx.StaticText(
            self,
            wx.ID_ANY,
            _(_("Replace connection:")),
        )
        self.swap_conn_box = wx.Choice(
            self, wx.ID_ANY, choices=self.conn_name_list
        )
        self.replace_text_2 = wx.StaticText(
            self,
            wx.ID_ANY,
            _(_("with connection:")),
        )
        self.new_conn_box = wx.Choice(self, wx.ID_ANY, choices=[])
        self.replace_button = wx.Button(
            self, wx.ID_ANY, _(_("Replace"))
        )
        self.horizontal_scrollbar = wx.ScrollBar(
            self,
            1,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SB_HORIZONTAL,
        )
        self.vertical_scrollbar = wx.ScrollBar(
            self,
            1,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SB_VERTICAL,
        )


        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.restart_button.Bind(wx.EVT_BUTTON, self.on_restart_button)
        self.add_box.Bind(wx.EVT_CHOICE, self.on_add_box)
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_button)
        self.zap_box.Bind(wx.EVT_CHOICE, self.on_zap_box)
        self.zap_button.Bind(wx.EVT_BUTTON, self.on_zap_button)
        self.switch_box.Bind(wx.EVT_CHOICE, self.on_switch_box)
        self.toggle_0.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_0)
        self.toggle_1.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_1)
        self.swap_conn_box.Bind(wx.EVT_CHOICE, self.on_swap_conn)
        self.new_conn_box.Bind(wx.EVT_CHOICE, self.on_new_conn)
        self.replace_button.Bind(wx.EVT_BUTTON, self.on_replace_button)
        self.horizontal_scrollbar.Bind(
            wx.EVT_SCROLL, self.on_horizontal_scrollbar
        )
        self.vertical_scrollbar.Bind(wx.EVT_SCROLL, self.on_vertical_scrollbar)

        # Initialise sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer_right = wx.BoxSizer(wx.VERTICAL)
        run_buttons = wx.BoxSizer(wx.HORIZONTAL)
        add_widgets = wx.BoxSizer(wx.HORIZONTAL)
        remove_widgets = wx.BoxSizer(wx.HORIZONTAL)
        switch_toggles = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer_left = wx.FlexGridSizer(2, 2, 0, 0)

        # place widgets in sizers
        main_sizer.Add(
            side_sizer_left,
            5,
            wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.TOP,
            5,
        )
        side_sizer_left.AddGrowableCol(0, 5)
        side_sizer_left.AddGrowableRow(0, 5)
        side_sizer_left.Add(self.canvas, 5, wx.EXPAND | wx.LEFT | wx.TOP, 5)
        side_sizer_left.Add(
            self.vertical_scrollbar,
            0,
            wx.EXPAND | wx.RIGHT | wx.TOP | wx.RESERVE_SPACE_EVEN_IF_HIDDEN,
            5,
        )
        side_sizer_left.Add(
            self.horizontal_scrollbar,
            0,
            wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RESERVE_SPACE_EVEN_IF_HIDDEN,
            5,
        )

        main_sizer.Add(side_sizer_right, 0, wx.ALL, 5)
        side_sizer_right.Add(self.text_run, 0, wx.ALL, 5)
        side_sizer_right.Add(self.spin, 0, wx.ALL, 5)
        side_sizer_right.Add(run_buttons, 0, wx.ALL, 0)
        run_buttons.Add(self.run_button, 0, wx.ALL, 5)
        run_buttons.Add(self.restart_button, 0, wx.ALL, 5)
        side_sizer_right.Add(self.text_add_mon, 0, wx.ALL, 5)
        side_sizer_right.Add(add_widgets, 0, wx.ALL, 0)
        add_widgets.Add(self.add_box, 0, wx.ALL, 5)
        add_widgets.Add(self.add_button, 0, wx.ALL, 5)
        side_sizer_right.Add(self.text_zap_mon, 0, wx.ALL, 5)
        side_sizer_right.Add(remove_widgets, 0, wx.ALL, 0)
        remove_widgets.Add(self.zap_box, 0, wx.ALL, 5)
        remove_widgets.Add(self.zap_button, 0, wx.ALL, 5)
        side_sizer_right.Add(self.text_switch, 0, wx.ALL, 5)
        side_sizer_right.Add(self.switch_box, 0, wx.ALL, 5)
        side_sizer_right.Add(switch_toggles, 0, wx.ALL, 0)
        side_sizer_right.Add(self.replace_text_1, 0, wx.ALL, 5)
        side_sizer_right.Add(self.swap_conn_box, 0, wx.ALL, 5)
        side_sizer_right.Add(self.replace_text_2, 0, wx.ALL, 5)
        side_sizer_right.Add(self.new_conn_box, 0, wx.ALL, 5)
        side_sizer_right.Add(self.replace_button, 0, wx.ALL, 5)
        switch_toggles.Add(self.toggle_0, 0, wx.ALL, 5)
        switch_toggles.Add(self.toggle_1, 0, wx.ALL, 5)

        self.SetSizer(main_sizer)

        # prompt user to select file
        if path == "":
            self.on_open_file(file=False)

        self.Show()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item.

        Arguments:
            event -- Menu item pressed
        """
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        elif Id == wx.ID_ABOUT:
            wx.MessageBox(
                _("Logic Simulator\nCreated by")
                + " Robbie Hodgeon, Scott Irvine "
                + _("and")
                + " Sahil Sindhi\n2022",
                _("About Logsim"),
                wx.ICON_INFORMATION | wx.OK,
            )
        elif Id == wx.ID_SAVE:
            self.on_save_file(full=False)
        elif Id == wx.ID_SAVEAS:
            self.on_save_file(full=True)
        elif Id == wx.ID_OPEN:
            self.on_open_file()
        elif Id == wx.ID_RESET:
            self.canvas.set_view(x=0, y=0, zoom=1)

    def draw_signals(self, monitors_dict):
        """Draws monitored signals on the canvas.

        Arguments:
            monitors_dict -- points to monitor
        """
        for device_id, output_id in monitors_dict:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            self.name_list.append(monitor_name)  # add signal name to name list
            signal = monitors_dict[(device_id, output_id)]
            self.signal_list.append(signal)  # add signal values to signal list

        self.canvas.render(self.name_list, self.signal_list)  # draw signals

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Arguments:
            cycles -- number of cycles to run

        Returns:
            True if successful, False if not
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print(
                    _(
                        "Error! Network oscillating."
                    )
                )
                return False
        monitors_dict = self.monitors.monitors_dictionary
        self.draw_signals(monitors_dict)
        return True

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value.

        Arguments:
            event -- change of value of spin
        """
        spin_value = self.spin.GetValue()
        self.num_cycles_requested = spin_value

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button.

        Arguments:
            event -- pressing of button
        """
        # reset tracking variables and signal lists
        cycles = self.num_cycles_requested
        self.signal_list = []
        self.name_list = []
        self.switch_to_toggle = ""
        self.switch_to_toggle_selection = None

        # ensure switch box selection resets upon pressing run
        for _ in range(len(self.switch_names)):
            self.switch_box.Delete(0)
        for i in range(len(self.switch_names)):
            self.switch_box.Append(self.switch_names[i])
        self.switch_box.SetSelection(wx.NOT_FOUND)

        # run simulation for requested number of cycles
        if cycles is not None:  # if the number of cycles provided is valid
            if self.run_network(cycles):
                self.cycles_completed += cycles
            self.canvas.render(self.name_list, self.signal_list)
            self.canvas.pan_x = self.canvas.width - self.canvas.max_x
            self.canvas.render(self.name_list, self.signal_list)
            self.on_horizontal_scrollbar("")

    def on_restart_button(self, event):
        """Handle the event when the user clicks the restart button.

        Arguments:
            event -- pressing of button
        """
        # reset view
        self.canvas.set_view(x=0, y=0, zoom=1)

        # reset tracking variables and signal lists
        self.cycles_completed = 0
        self.signal_list = []
        self.name_list = []
        self.switch_to_toggle = ""
        self.switch_to_toggle_selection = None

        # ensure switch box selection resets upon pressing run
        for _ in range(len(self.switch_names)):
            self.switch_box.Delete(0)
        for i in range(len(self.switch_names)):
            self.switch_box.Append(self.switch_names[i])
        self.switch_box.SetSelection(wx.NOT_FOUND)

        # reset monitors and devices
        self.monitors.reset_monitors()
        self.devices.cold_startup()
        self.run_network(0)
        self.canvas.render(self.name_list, self.signal_list)

    def on_add_box(self, event):
        """Handle the event when user selects a monitor to add from the box.

        Arguments:
            event -- change of string in box
        """
        text_box_value = self.add_box.GetStringSelection()
        self.add_monitor = text_box_value

    def on_zap_box(self, event):
        """Handle the event when user selects a monitor to zap from the box.

        Arguments:
            event -- change of string in box
        """
        text_box_value = self.zap_box.GetStringSelection()
        self.zap_monitor = text_box_value

    def on_switch_box(self, event):
        """Handle the event when user selects a switch to toggle from the box.

        Arguments:
            event -- change of string in box
        """
        text_box_value = self.switch_box.GetStringSelection()
        self.switch_to_toggle = text_box_value
        self.switch_to_toggle_selection = self.switch_box.GetSelection()
        self.switch_to_toggle_state = self.switch_states[
            self.switch_box.GetSelection()
        ]
        # set switches to correct values
        if self.switch_to_toggle_state == 1:
            self.toggle_0.SetValue(False)
            self.toggle_1.SetValue(True)
        elif self.switch_to_toggle_state == 0:
            self.toggle_0.SetValue(True)
            self.toggle_1.SetValue(False)

    def on_add_button(self, event):
        """Handle the event when the user presses the add monitor button.

        Arguments:
            event -- pressing of button
        """
        if (
            self.add_monitor != ""
        ):  # if the user has currently selected a monitor to add
            new_monitor = self.devices.get_signal_ids(self.add_monitor)
            [device, port] = new_monitor
            monitor_error = self.monitors.make_monitor(
                device, port, self.cycles_completed
            )
            if monitor_error == self.monitors.NO_ERROR:
                self.signal_list = []
                self.name_list = []

                # remove selected monitor from choice of monitors to add
                for _ in range(len(self.not_monitored_list)):
                    self.add_box.Delete(0)
                self.not_monitored_list = self.monitors.get_signal_names()[1]
                for i in range(len(self.not_monitored_list)):
                    self.add_box.Append(self.not_monitored_list[i])

                # add selected monitor to choice of monitors to remove
                for _ in range(len(self.monitored_list)):
                    self.zap_box.Delete(0)
                self.monitored_list = self.monitors.get_signal_names()[0]
                for i in range(len(self.monitored_list)):
                    self.zap_box.Append(self.monitored_list[i])

                # draw monitored signals
                monitors_dict = self.monitors.monitors_dictionary
                self.draw_signals(monitors_dict)
        self.canvas.render(self.name_list, self.signal_list)
        self.add_monitor = ""
        self.add_box.SetSelection(wx.NOT_FOUND)
        self.zap_box.SetSelection(wx.NOT_FOUND)

    def on_zap_button(self, event):
        """Handle the event when the user presses the remove monitor button.

        Arguments:
            event -- pressing of button
        """
        if self.zap_monitor != "":
            zap_monitor = self.devices.get_signal_ids(self.zap_monitor)
            [device, port] = zap_monitor
            if self.monitors.remove_monitor(device, port):
                self.signal_list = []
                self.name_list = []

                # add selected monitor to choice of monitors to add
                for _ in range(len(self.not_monitored_list)):
                    self.add_box.Delete(0)
                self.not_monitored_list = self.monitors.get_signal_names()[1]
                for i in range(len(self.not_monitored_list)):
                    self.add_box.Append(self.not_monitored_list[i])

                # remove selected monitor from choice of monitors to remove
                for _ in range(len(self.monitored_list)):
                    self.zap_box.Delete(0)
                self.monitored_list = self.monitors.get_signal_names()[0]
                for i in range(len(self.monitored_list)):
                    self.zap_box.Append(self.monitored_list[i])

                # draw monitored signals
                monitors_dict = self.monitors.monitors_dictionary
                self.draw_signals(monitors_dict)
        self.canvas.render(self.name_list, self.signal_list)
        self.zap_monitor = ""
        self.add_box.SetSelection(wx.NOT_FOUND)
        self.zap_box.SetSelection(wx.NOT_FOUND)

    def on_toggle_0(self, event):
        """Handle the event when the user presses the toggle_0 button.

        Arguments:
            event -- Event which caused toggle to be activated
        """
        if self.toggle_0.GetValue():  # if 0 button is pressed
            self.toggle_1.SetValue(False)  # set 1 button to be unpressed
            if self.switch_to_toggle != "":  # if there is a switch selected
                switch_id = self.names.query(
                    self.switch_to_toggle
                )  # get switch ID
                if switch_id is not None:
                    if self.devices.set_switch(
                        switch_id, 0
                    ):  # set switch to 0
                        # update switch state in switch states list
                        self.switch_states[self.switch_to_toggle_selection] = 0
                    self.canvas.render(self.name_list, self.signal_list)
            self.canvas.render(self.name_list, self.signal_list)
        else:  # 0 button is unpressed
            self.toggle_0.SetValue(True)  # keep 0 button to pressed

    def on_toggle_1(self, event):
        """Handle the event when the user presses the toggle_1 button.

        Arguments:
            event -- Event which caused toggle to be activated
        """
        if self.toggle_1.GetValue():  # if 1 button is pressed
            self.toggle_0.SetValue(False)  # set 0 button to be unpressed
            if self.switch_to_toggle != "":  # if there is a switch selected
                switch_id = self.names.query(
                    self.switch_to_toggle
                )  # get switch ID
                if switch_id is not None:
                    if self.devices.set_switch(
                        switch_id, 1
                    ):  # set switch to 1
                        # update switch state in switch states list
                        self.switch_states[self.switch_to_toggle_selection] = 1
                    self.canvas.render(self.name_list, self.signal_list)
            self.canvas.render(self.name_list, self.signal_list)
        else:  # 1 button is unpressed
            self.toggle_1.SetValue(True)  # keep 1 button to be pressed

    def on_swap_conn(self, event):
        """Handle the event when the user selects an input to alter connection for"""
        _, text = self.swap_conn_box.GetString(
            self.swap_conn_box.GetCurrentSelection()
        ).split(" > ")
        self.input_for_swap = self.devices.get_signal_ids(text)
        options = self.get_new_conn_options(text)
        self.set_choices(self.new_conn_box, options)

        new_conn_box = wx.Choice(self, wx.ID_ANY, choices=options)
        self.new_conn_box.SetSize(new_conn_box.GetSize())
        self.new_conn_box.SetSelection(wx.NOT_FOUND)
        self.new_conn_box.SetMaxSize((250, 10000))
        new_conn_box.Destroy()
        self.Layout()

    def on_new_conn(self, event):
        """Handle the event when the user selects a new output to connect to an input"""
        text, _ = self.new_conn_box.GetString(
            self.new_conn_box.GetCurrentSelection()
        ).split(" > ")
        self.output_for_swap = self.devices.get_signal_ids(text)

    def on_replace_button(self, event):
        """Handle the event when the user presses the 'Replace connection' button"""
        message = ""
        undo = False
        if self.input_for_swap is not None:
            if self.output_for_swap is not None:
                # get all necessary IDs
                first_dev_id, first_port_id = self.input_for_swap
                new_dev_id, new_port_id = self.output_for_swap
                old_dev_id, old_port_id = self.network.get_connected_output(
                    first_dev_id, first_port_id
                )
                # attempt to replace the connection
                error = self.network.replace_connection(
                    first_dev_id,
                    first_port_id,
                    new_dev_id,
                    new_port_id,
                    old_dev_id,
                    old_port_id,
                )
                # if connection was successfully replaced
                if error == self.network.NO_ERROR:
                    message += (
                        _(
                            "Successfully swapped connection into "
                        )
                        + self.devices.get_signal_name(
                            first_dev_id, first_port_id
                        )
                        + _(
                            ".\nConnection changed from "
                        )
                        + self.swap_conn_box.GetString(
                            self.swap_conn_box.GetCurrentSelection()
                        )
                        + _(" to ")
                        + self.new_conn_box.GetString(
                            self.new_conn_box.GetCurrentSelection()
                        )
                        + _(".\n")
                    )
                    undo = True
                else:
                    message += _(
                        "Error! Could not swap connection: "
                        + self.network.error_message[error]
                        + ".\n"
                    )
            else:
                message += _(
                    "Please select a new connection to replace"
                    + " the connection you wish to remove.\n"
                )
        else:
            message += _(
                "Please select an existing connection to replace."
            )
        if undo:  # if the connection was successfully replaced
            # open dialog box with option to undo the connection replacement
            swap_conn_dialog = wx.MessageDialog(
                self,
                message,
                _(
                    "Connection swapped successfully"
                ),
                wx.OK | wx.CANCEL,
            )
            swap_conn_dialog.SetOKCancelLabels(
                _("OK"),
                _("Undo"),
            )
            action = swap_conn_dialog.ShowModal()
            # if user wants to undo the connection replacement
            if action == wx.ID_CANCEL:
                message = ""
                # attempt to replace the connection the other way around
                error = self.network.replace_connection(
                    first_dev_id,
                    first_port_id,
                    old_dev_id,
                    old_port_id,
                    new_dev_id,
                    new_port_id,
                )
                if error == self.network.NO_ERROR:
                    message += _(
                        "Successfully undid connection swap.\n"
                    )
                else:
                    message += _(
                        "Error! Could not undo connection swap: "
                        + self.network.error_message[error]
                        + ".\n"
                    )
                # dialog to show status of undo attempt
                undo_dialog = wx.MessageDialog(
                    self,
                    message,
                    _("Undo status message"),
                    wx.OK,
                )
                undo_dialog.ShowModal()
        else:  # connection was not successfully replaced
            swap_conn_dialog = wx.MessageDialog(
                self,
                message,
                _("Connection swap failed!"),
                wx.OK,
            )
            swap_conn_dialog.ShowModal()
        # reset variables and choice boxes
        self.input_for_swap = None
        self.output_for_swap = None
        self.set_choices(self.swap_conn_box, self.get_conn_names())
        self.set_choices(self.new_conn_box, [])
        self.swap_conn_box.SetSelection(wx.NOT_FOUND)
        self.new_conn_box.SetSelection(wx.NOT_FOUND)

    def on_horizontal_scrollbar(self, event):
        """Change canvas position after horizontal scrollbar is moved.

        Arguments:
            event -- Event which caused change in scrollbar
        """
        x = -self.horizontal_scrollbar.GetThumbPosition()
        self.canvas.set_view(x, self.canvas.pan_y, zoom=self.canvas.zoom)

    def on_vertical_scrollbar(self, event):
        """Change canvas position after vertical scrollbar is moved.

        Arguments:
            event -- Event which caused change in scrollbar
        """
        y = (
            self.vertical_scrollbar.GetThumbPosition()
            + self.canvas.height
            - self.canvas.max_y
        )
        self.canvas.set_view(self.canvas.pan_x, y, zoom=self.canvas.zoom)

    def on_open_file(self, file=True):
        """Create and show the Open FileDialog.

        Keyword Arguments:
            file -- whether a file is already loaded (default: {True})
        """
        dialog = wx.FileDialog(
            self,
            message=_(
                "Choose a circuit definition file"
            ),
            defaultDir=str(Path.cwd()),
            defaultFile="",
            wildcard="Text file (*.txt)|*.txt",
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST,
        )
        # get action done by user
        action = dialog.ShowModal()
        if action == wx.ID_OK:  # if file selected
            path = dialog.GetPath()
            print(
                _(
                    "You chose the following file:"
                )
                + f' "{path}"'
            )
            if Path(path).suffix == ".txt":
                # initialise network variables
                names = Names()
                devices = Devices(names)
                network = Network(names, devices)
                monitors = Monitors(names, devices, network)
                scanner = Scanner(path, names)
                parser = Parser(
                    names, devices, network, monitors, scanner
                )
                if parser.parse_network():
                    # set up gui for new circuit
                    self.names = names
                    self.devices = devices
                    self.network = network
                    self.monitors = monitors
                    self.scanner = scanner
                    self.parser = parser
                    self.new_file()
                    dialog.Destroy()
                else:
                    # show errors
                    parse_error_dialog = wx.lib.dialogs.ScrolledMessageDialog(
                        self,
                        parser.error_msg[2:],
                        _(
                            "Could not parse file! (Error message below)"
                            " Please select a different file."
                        ),
                    )
                    txt_ctrl = parse_error_dialog.text
                    txt_ctrl.SetFont(
                        wx.Font(
                            9,
                            wx.FONTFAMILY_TELETYPE,
                            wx.NORMAL,
                            wx.NORMAL,
                        )
                    )
                    parse_error_dialog.EnableCloseButton(False)
                    parse_error_dialog.ShowModal()
                    dialog.Destroy()
                    self.on_open_file(file=file)
            else:
                if file is False:
                    # require text file to be selected
                    if (
                        wx.MessageBox(
                            _(
                                "Could not load file! File type must be a text"
                                " file (*.txt)\nWould you like to open a"
                                " different file?"
                            ),
                            _(
                                "Error opening file"
                            ),
                            wx.ICON_ERROR | wx.YES_NO,
                        )
                        == wx.YES
                    ):
                        dialog.Destroy()
                        self.on_open_file(file=False)
                    else:
                        sys.exit()
                else:
                    # exit without opening a file
                    wx.MessageBox(
                        _(
                            "Could not load file! File type must be a text"
                            " file (*.txt)."
                        ),
                        _("Error opening file"),
                        wx.ICON_ERROR | wx.OK,
                    )
                    dialog.Destroy()
        elif action == wx.ID_CANCEL and file is False:
            # require file to be selected
            if (
                wx.MessageBox(
                    _(
                        "This program requires you to load a circuit"
                        " definition file.\nWould you like to select a file to"
                        " load?"
                    ),
                    _("File required"),
                    wx.ICON_ERROR | wx.YES_NO,
                )
                == wx.YES
            ):
                dialog.Destroy()
                self.on_open_file(file=False)
            else:
                sys.exit()
        else:
            dialog.Destroy()

    def on_save_file(self, full=False):
        """Create and show the Save FileDialog.

        Keyword Arguments:
            full -- determines size of image to save (default: {False})
        """
        dialog = wx.FileDialog(
            self,
            message=_("Save file as ..."),
            defaultDir=str(Path.cwd()),
            defaultFile="",
            wildcard="PNG (*.png)|*.png",
            style=wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT,
        )
        if dialog.ShowModal() == wx.ID_OK:  # if save requested
            path = dialog.GetPath()
            print(
                _(
                    "You chose the following filename:"
                )
                + f' "{path}"'
            )
            image = self.canvas.save_image(full)
            if Path(path).suffix == ".png":  # make sure file type is png
                image.save(path, "PNG")
            else:
                wx.MessageBox(
                    _(
                        "Could not save image! File type must be PNG."
                    ),
                    _("Error saving file"),
                    wx.ICON_ERROR | wx.OK,
                )
        dialog.Destroy()

    def get_input_names(self):
        """Return a list of all the input names in the network.

        Returns: input_names
            List of strings containing the names of every input port
            in the network.
        """
        input_names = []
        device_ids = self.devices.find_devices()
        for id in device_ids:
            device = self.devices.get_device(id)
            inputs = list(device.inputs)
            for input in inputs:
                name = self.devices.get_signal_name(id, input)
                input_names.append(name)
        return input_names

    def get_conn_names(self):
        """Return a list with the names of each connection in the network.

        Returns: conn_names
            list of strings containing 'output_name > input_name' for each
            connection in the network sorted alphabetically by input_name
        """
        conn_names = []
        input_names = sorted(self.get_input_names())
        for input_name in input_names:
            device_id, input_id = self.devices.get_signal_ids(input_name)
            conn_device, conn_output = self.network.get_connected_output(
                device_id, input_id
            )
            output_name = self.devices.get_signal_name(
                conn_device, conn_output
            )
            conn_name = " > ".join([output_name, input_name])
            conn_names.append(conn_name)
        return conn_names

    def get_new_conn_options(self, input_name):
        """_summary_

        Arguments:
            input_name -- string, the name of the input port selected to
                change the connection to.

        Returns: options
            list of strings containing all possible new outputs to connect
            into input_name in form 'new_output > input_name'
        """
        options = []
        device_id, input_id = self.devices.get_signal_ids(input_name)
        current_conn, current_port = self.network.get_connected_output(
            device_id, input_id
        )
        current_output_name = self.devices.get_signal_name(
            current_conn, current_port
        )
        for output in self.output_names_list:
            if output != current_output_name:
                new_option = " > ".join([output, input_name])
                options.append(new_option)
        return options

    def new_file(self):
        """Set up GUI for new file."""
        self.cycles_completed = 0  # number of simulation cycles completed
        self.num_cycles_requested = (
            10  # number of simulation cycles requested by user
        )

        # store which signals are monitored and not monitored
        self.monitored_list = self.monitors.get_signal_names()[0]
        self.not_monitored_list = self.monitors.get_signal_names()[1]

        # list of all input names in network
        self.input_names_list = sorted(self.get_input_names())

        # list of all output names in network
        self.output_names_list = sorted(
            self.monitored_list + self.not_monitored_list
        )

        # list of all connection names in network
        self.conn_name_list = self.get_conn_names()

        # list of all switch IDs in network
        self.switch_list = self.devices.find_devices(self.devices.SWITCH)

        # list of all switch names in network
        self.switch_names = [
            self.names.get_name_string(switch) for switch in self.switch_list
        ]

        # list of the states of the switches in the network
        self.switch_states = [
            self.devices.get_device(switch).switch_state
            for switch in self.switch_list
        ]

        # store the signals and names that are being monitored
        self.signal_list = []
        self.name_list = []

        # initialise tracking variables
        self.add_monitor = ""  # monitor name to add
        self.zap_monitor = ""  # monitor name to remove
        self.switch_to_toggle = ""  # name of switch to toggle
        self.switch_to_toggle_state = None  # state of switch to toggle
        self.switch_to_toggle_selection = None  # index of switch to toggle
        self.input_for_swap = None  # input to swap connection for
        self.output_for_swap = None  # output to swap connection for

        # Reset widget configuration
        self.spin.SetValue("10")
        self.set_choices(self.add_box, self.not_monitored_list)
        self.set_choices(self.zap_box, self.monitored_list)
        self.set_choices(self.switch_box, self.switch_names)
        self.set_choices(self.swap_conn_box, self.conn_name_list)

        add_box = wx.Choice(
            self,
            wx.ID_ANY,
            choices=self.not_monitored_list,
        )
        zap_box = wx.Choice(
            self,
            wx.ID_ANY,
            choices=self.monitored_list,
        )
        switch_box = wx.Choice(self, wx.ID_ANY, choices=self.switch_names)
        swap_conn_box = wx.Choice(self, wx.ID_ANY, choices=self.conn_name_list)

        # set dropdown size to match choices available
        if add_box.GetSize()[0] < zap_box.GetSize()[0]:
            self.add_box.SetSize(zap_box.GetSize())
            self.zap_box.SetSize(zap_box.GetSize())
        else:
            self.add_box.SetSize(add_box.GetSize())
            self.zap_box.SetSize(add_box.GetSize())

        self.switch_box.SetSize(switch_box.GetSize())

        self.swap_conn_box.SetSize(swap_conn_box.GetSize())

        add_box.Destroy()
        zap_box.Destroy()
        switch_box.Destroy()
        swap_conn_box.Destroy()

        self.SetMinSize((900, 480))
        self.add_box.SetMaxSize((155, 10000))
        self.zap_box.SetMaxSize((155, 10000))
        self.switch_box.SetMaxSize((250, 10000))
        self.swap_conn_box.SetMaxSize((250, 10000))
        self.new_conn_box.SetMaxSize((250, 10000))

        # set dropdowns to be empty
        self.add_box.SetSelection(wx.NOT_FOUND)
        self.zap_box.SetSelection(wx.NOT_FOUND)
        self.switch_box.SetSelection(wx.NOT_FOUND)
        self.swap_conn_box.SetSelection(wx.NOT_FOUND)
        self.new_conn_box.SetSelection(wx.NOT_FOUND)

        #self.draw_signals(self.monitors.monitors_dictionary)

    def set_choices(self, choicebox, choices):
        """Set choices in dropdowns.

        Arguments:
            choicebox -- wx.Choice widget
            choices -- list of strings to add as choices
        """
        choicebox.Clear()
        for item in choices:
            choicebox.Append(item)

