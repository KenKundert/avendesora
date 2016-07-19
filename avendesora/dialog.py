# Account Select Dialog Box

# Requires the python bindings for the GTK3 library.

from inform import fatal, notify
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk as gtk
    from gi.repository import Gdk as gdk

    class ListDialog (gtk.Window):
        def __init__(self, options):
            gtk.Window.__init__(self)
            self.set_type_hint(gdk.WindowTypeHint.DIALOG)
            self.connect('key_press_event', self.on_hotkey)
            self.connect('destroy', self.close)

            self.model = gtk.ListStore(str)
            self.view = gtk.TreeView(self.model)
            self.view.connect('button_press_event', self.on_mouse)

            cell = gtk.CellRendererText()
            column = gtk.TreeViewColumn("Account", cell, text=0)
            self.view.append_column(column)

            self.choice = None
            self.options = options

            for account in options:
                row = self.model.append()
                self.model.set(row, 0, account)

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

            scroll = lambda path, dx: (path[0] + dx) % len(self.options)

            if key in ['j', 'Down']:
                self.view.set_cursor(scroll(path, 1))
            elif key in ['k', 'Up']:
                self.view.set_cursor(scroll(path, -1))
            elif key == 'Return':
                self.accept()
            elif key == 'Escape':
                self.close()

            return True

        def on_mouse(self, widget, event):
            if event.type == gdk.EventType._2BUTTON_PRESS:
                self.accept()


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


    def show_list_dialog(options):
        dialog = ListDialog(options)
        return dialog.run()

    def show_error_dialog(message):
        dialog = ErrorDialog(message)
        return dialog.run()

except ImportError:
    def show_list_dialog(options):
        msg = 'selection dialog not available, you must install python3-gobject.'
        notify(msg)
        fatal(msg)

    def show_error_dialog(message):
        msg = 'error dialog not available, you must install python3-gobject.'
        notify(msg)
        fatal(msg)

if __name__ == '__main__':
    print(show_list_dialog(['primary', 'secondary']))
    print(show_error_dialog('This is a test of the emergency broadcast system.'))
