import gtk
import gtk.glade

class EditApp(object):

    def __init__(self, taggedPath):
        self.gui = gtk.Builder()
        self.gui.add_from_file('src/glade/tagEditDialog.glade')
        self.gui.connect_signals(self)

        self.editWindow = self.gui.get_object('editWindow')
        self.editWindow.show()

    def gtk_main_quit(self, w):
        gtk.main_quit()

def main():
    import sys

    # TODO show popup when no args are passed
    app = EditApp(sys.argv[0])

    gtk.main()

    return 0
