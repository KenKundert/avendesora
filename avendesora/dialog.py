# Account Select Dialog Box

# Requires the python bindings for the GTK3 library.

from .config import get_setting
from .shlib import Run
from inform import Error


# dmenu selection utility interface
def dmenu_dialog(title, choices):
    executable = get_setting('dmenu_executable')
    #cmd = [executable, '-l', len(choices), '-i', '-p', title]
    cmd = [executable, '-l', len(choices), '-i']
    try:
        dmenu = Run(cmd, 'sOEW1', stdin='\n'.join(choices))
    except Error as e:
        e.reraise(culprit=executable)
    return dmenu.stdout.rstrip('\n')


# gtk selection utility interface
try:

    def show_list_dialog(title, choices):

        # import gi and define ListDialog inside show_list_dialog to prevent the
        # import from slowing down startup. This way it is only imported if it
        # is used.

        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk as gtk
        from gi.repository import Gdk as gdk

        class ListDialog (gtk.Window):
            def __init__(self, title, choices):
                gtk.Window.__init__(self)
                self.set_type_hint(gdk.WindowTypeHint.DIALOG)
                self.connect('key_press_event', self.on_hotkey)
                self.connect('destroy', self.close)

                self.model = gtk.ListStore(str)
                self.view = gtk.TreeView(self.model)
                self.view.connect('button_press_event', self.on_mouse)

                cell = gtk.CellRendererText()
                column = gtk.TreeViewColumn(title, cell, text=0)
                self.view.append_column(column)

                self.choice = None
                self.choices = choices

                for choice in choices:
                    row = self.model.append()
                    self.model.set(row, 0, choice)

                self.add(self.view)

            def run(self):
                self.show_all()
                gtk.main()
                return self.choice

            def accept(self):
                path, column = self.view.get_cursor()
                iter = self.model.get_iter(path[0])
                self.choice = self.model.get_value(iter, 0)
                self.close()

            def close(self, *args):
                self.destroy()
                # Consume all pending events - include the window destroy
                while gtk.events_pending():
                    gtk.main_iteration()
                gtk.main_quit()

            def on_hotkey(self, widget, event):
                key = gdk.keyval_name(event.keyval)
                selection = self.view.get_selection()
                model, iter = selection.get_selected()
                path = self.model.get_path(iter)

                def scroll(path, dx):
                    return (path[0] + dx) % len(self.choices)

                if key in ['j', 'Down']:
                    self.view.set_cursor(scroll(path, 1))
                elif key in ['k', 'Up']:
                    self.view.set_cursor(scroll(path, -1))
                elif key in ['l', 'Right', 'Return']:
                    self.accept()
                elif key in ['h', 'Left', 'Escape']:
                    self.close()

                return True

            def on_mouse(self, widget, event):
                if event.type == gdk.EventType._2BUTTON_PRESS:
                    self.accept()

        selector = get_setting('selection_utility')
        if selector == 'gtk':
            return ListDialog(title, choices).run()
        elif selector == 'dmenu':
            return dmenu_dialog(title, choices)
        raise Error('selection utility not found.', culprit=selector)

    def show_error_dialog(message):

        # Import gi and define ErrorDialog inside show_error_dialog() to prevent
        # the import from slowing down startup. This way it is only imported if
        # it is used.

        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk as gtk
        from gi.repository import Gdk as gdk

        class ErrorDialog (gtk.MessageDialog):
            def __init__(self, message, description=None):
                gtk.MessageDialog.__init__(
                    self,
                    type=gtk.MessageType.ERROR,
                    buttons=gtk.ButtonsType.OK,
                    message_format=message
                )
                if description:
                    self.format_secondary_text(description)

        dialog = ErrorDialog(message)
        return dialog.run()

except ImportError:
    def show_list_dialog(title, choices):
        selector = get_setting('selection_utility')
        if selector == 'gtk':
            msg = 'selection utility not available, you must install python-gobject.'
        elif selector == 'dmenu':
            return dmenu_dialog(title, choices)
        else:
            msg = 'selection utility not found.'
        raise Error(msg, culprit=selector)

    def show_error_dialog(message):
        msg = 'error dialog not available, you must install python-gobject.'
        raise Error(msg)

if __name__ == '__main__':
    print(show_list_dialog('Choose from', ['primary', 'secondary']))
    print(show_error_dialog('This is a test of the emergency broadcast system.'))
