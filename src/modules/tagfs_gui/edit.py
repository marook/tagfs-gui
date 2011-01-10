import gtk
import gtk.glade

class EditApp(object):

    def __init__(self, taggedPath):
        self.gui = gtk.Builder()
        self.gui.add_from_file('src/glade/tagEditDialog.glade')
        self.gui.connect_signals(self)

        self.editWindow = self.gui.get_object('editWindow')
        self.editWindow.show()

    def on_saveAction_activate(self, w):
        pass

    def on_cancelAction_activate(self, w):
        gtk.main_quit()

def main(args):
    # TODO show popup when no args are passed
    app = EditApp(args[1])

    gtk.main()

    return 0
