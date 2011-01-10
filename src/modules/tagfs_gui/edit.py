import gtk
import gtk.glade

from tag_utils import tag_io

class TaggingsListStore(gtk.ListStore):

    def __init__(self, taggedPath):
        super(TaggingsListStore, self).__init__(str, str)

        self.loadTaggingsFromPath(taggedPath)

    def loadTaggingsFromPath(self, taggedPath):
        # TODO allow tag file support
        self.item = tag_io.parseDirectory(taggedPath)
    
        # TODO fill model
        

class EditApp(object):

    def __init__(self, taggedPath):
        self.gui = gtk.Builder()
        self.gui.add_from_file('src/glade/tagEditDialog.glade')
        self.gui.connect_signals(self)

        self.taggingsListStore = TaggingsListStore(taggedPath)
        self.gui.get_object('taggingsTreeView').set_model(self.taggingsListStore)

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
