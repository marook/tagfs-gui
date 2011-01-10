import os.path

import gtk
import gtk.glade

from tag_utils import tag_io

class TaggingsListStore(gtk.ListStore):

    def __init__(self, taggedDir):
        super(TaggingsListStore, self).__init__(str, str)

        self.taggedDir = taggedDir

        self.loadTaggings()

    def loadTaggings(self):
        # TODO allow tag file support
        self.item = tag_io.parseDirectory(self.taggedDir)
    
        for t in self.item.taggings:
            self.append([t.context, t.value])

    def saveTaggings(self):
        tagFileName = os.path.join(self.taggedDir, tag_io.DEFAULT_TAG_FILE_NAME)

        tag_io.writeFile(self.item, tagFileName)

class EditApp(object):

    def initTaggingsTreeView(self, taggedPath):
        v = self.gui.get_object('taggingsTreeView')

        columnTitles = ['context', 'value']

        for i in range(0, 2):
            c = gtk.TreeViewColumn(columnTitles[i], gtk.CellRendererText(), text = i)
            c.set_resizable(True)
            c.set_sort_column_id(i)

            v.append_column(c)

        self.taggingsListStore = TaggingsListStore(taggedPath)
        v.set_model(self.taggingsListStore)

    def __init__(self, taggedPath):
        self.gui = gtk.Builder()
        # TODO determine path
        # TODO join path to make os independent
        self.gui.add_from_file('src/glade/tagEditDialog.glade')
        self.gui.connect_signals(self)

        self.initTaggingsTreeView(taggedPath)

        self.editWindow = self.gui.get_object('editWindow')
        self.editWindow.set_title('tagging ' + taggedPath)
        self.editWindow.show()

    def quit(self):
        gtk.main_quit()

    def on_saveAction_activate(self, w):
        self.taggingsListStore.saveTaggings()

        self.quit()

    def on_cancelAction_activate(self, w):
        self.quit()

def main(args):
    # TODO show popup when no args are passed
    app = EditApp(args[1])

    gtk.main()

    return 0
