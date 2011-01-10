import os.path

import gtk
import gtk.glade

from tag_utils import tag_io

from tagfs_gui import job

class TaggingsListStore(gtk.ListStore):

    def __init__(self, taggedDir):
        super(TaggingsListStore, self).__init__(str, str)

        self.taggedDir = taggedDir

        self.contextColumn = 0
        self.valueColumn = 1

        self.loadTaggings()

    def setContext(self, path, newContext):
        self.item.taggings[int(path)].context = newContext

        self._updateModelFromItem()

    def setValue(self, path, newValue):
        self.item.taggings[int(path)].value = newValue

        self._updateModelFromItem()

    def _updateModelFromItem(self):
        self.clear()

        for t in self.item.taggings:
            self.append([t.context, t.value])

    def loadTaggings(self):
        self.item = tag_io.parseDirectory(self.taggedDir)

        self._updateModelFromItem()

    def saveTaggings(self):
        tagFileName = os.path.join(self.taggedDir, tag_io.DEFAULT_TAG_FILE_NAME)

        tag_io.writeFile(self.item, tagFileName)

class LoadTaggingsJob(object):

    def __init__(self, saveAction, taggingsTreeView, taggingsListStore):
        self.description = 'Loading taggings...'
        self.saveAction = saveAction
        self.taggingsTreeView = taggingsTreeView
        self.taggingsListStore = taggingsListStore

    def run(self):
        # TODO do we have to care about synchronization?
        self.taggingsListStore.loadTaggings()

        self.taggingsTreeView.set_sensitive(True)
        self.saveAction.set_sensitive(True)

class EditApp(object):

    def initTaggingsTreeView(self, taggedPath):
        self.taggingsTreeView = self.gui.get_object('taggingsTreeView')

        self.taggingsListStore = TaggingsListStore(taggedPath)
        self.taggingsTreeView.set_model(self.taggingsListStore)

        def editedContext(cell, path, newText):
            self.taggingsListStore.setContext(path, newText)

        def editedValue(cell, path, newText):
            self.taggingsListStore.setValue(path, newText)

        numberOfColumns = 2

        columnEditCallbacks = numberOfColumns * [None]
        columnEditCallbacks[self.taggingsListStore.contextColumn] = editedContext
        columnEditCallbacks[self.taggingsListStore.valueColumn] =  editedValue

        columnTitles = 2 * [None]
        columnTitles[self.taggingsListStore.contextColumn] = 'context'
        columnTitles[self.taggingsListStore.valueColumn] = 'value'

        for i in range(0, numberOfColumns):
            r = gtk.CellRendererText()
            r.set_property('editable', True)
            r.connect('edited', columnEditCallbacks[i])

            c = gtk.TreeViewColumn(columnTitles[i], r, text = i)
            c.set_resizable(True)
            c.set_sort_column_id(i)

            self.taggingsTreeView.append_column(c)

    def initJobRunner(self):
        self.statusBar = self.gui.get_object('statusbar')

        jobRunnerContextId = self.statusBar.get_context_id('JobRunnerDescriptions')
        def setJobDescription(desc):
            if desc is None:
                self.statusBar.pop(jobRunnerContextId)
            else:
                self.statusBar.push(jobRunnerContextId, desc)

        self.jobRunner = job.JobRunner([LoadTaggingsJob(self.saveAction, self.taggingsTreeView, self.taggingsListStore)], setJobDescription)
        self.jobRunner.start()

    def __init__(self, taggedPath):
        self.gui = gtk.Builder()
        # TODO determine path
        # TODO join path to make os independent
        self.gui.add_from_file('src/glade/tagEditDialog.glade')
        self.gui.connect_signals(self)

        self.saveAction = self.gui.get_object('saveAction')

        # TODO implement tag file support
        self.initTaggingsTreeView(taggedPath)

        self.editWindow = self.gui.get_object('editWindow')
        self.editWindow.set_title('tagging ' + taggedPath)
        self.editWindow.show()

        self.initJobRunner()

    def quit(self):
        with self.jobRunner.jobsLock:
            while len(self.jobRunner.jobs) > 0:
                self.jobRunner.jobs.pop()

        self.editWindow.set_visible(False)

        gtk.main_quit()

    def on_saveAction_activate(self, w):
        # TODO display save errors
        self.taggingsListStore.saveTaggings()

        self.quit()

    def on_cancelAction_activate(self, w):
        self.quit()

def main(args):
    gtk.gdk.threads_init()

    # TODO show popup when no args are passed
    app = EditApp(args[1])

    gtk.main()

    return 0
