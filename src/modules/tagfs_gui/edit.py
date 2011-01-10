#
# Copyright 2011 Markus Pielmeier
#
# This file is part of tagfs-gui.
#
# tagfs-gui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tagfs-gui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tagfs-gui.  If not, see <http://www.gnu.org/licenses/>.
#

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

class ContextsListStore(gtk.ListStore):
    
    def __init__(self, contexts):
        super(ContextsListStore, self).__init__(str)

        for c in contexts:
            self.append([c, ])

class ValuesListStore(gtk.ListStore):
    
    def __init__(self, values):
        super(ValuesListStore, self).__init__(str)

        for v in values:
            self.append([v, ])

class LoadTaggingsJob(object):

    def __init__(self, saveAction, taggingsTreeView, taggingsListStore):
        self.description = 'Loading taggings...'
        self.saveAction = saveAction
        self.taggingsTreeView = taggingsTreeView
        self.taggingsListStore = taggingsListStore

    def run(self):
        gtk.gdk.threads_enter()
        try:
            self.taggingsListStore.loadTaggings()

            self.taggingsTreeView.set_sensitive(True)
            self.saveAction.set_sensitive(True)
        finally:
            gtk.gdk.threads_leave()

class LoadContextsAndValuesJob(object):
    
    def __init__(self, taggedDir, contextsTreeView, valuesTreeView):
        self.description = 'Loading all taggings...'
        self.dbDir = os.path.join(taggedDir, '..')
        self.contextsTreeView = contextsTreeView
        self.valuesTreeView = valuesTreeView

    def initContextTreeView(self, db):
        c = gtk.TreeViewColumn('contexts', gtk.CellRendererText(), text = 0)
        c.set_sort_column_id(0)

        listStore = ContextsListStore(db.contexts)
        self.contextsTreeView.set_model(listStore)

        self.contextsTreeView.append_column(c)

        self.contextsTreeView.set_sensitive(True)

    def initValuesTreeView(self, db):
        c = gtk.TreeViewColumn('values', gtk.CellRendererText(), text = 0)
        c.set_sort_column_id(0)

        listStore = ValuesListStore(db.values)
        self.valuesTreeView.set_model(listStore)

        self.valuesTreeView.append_column(c)

        self.valuesTreeView.set_sensitive(True)

    def run(self):
        # TODO check stop flag during parsing
        db = tag_io.parseDatabaseDirectory(self.dbDir)

        gtk.gdk.threads_enter()
        try:
            self.initContextTreeView(db)
            self.initValuesTreeView(db)
        finally:
            gtk.gdk.threads_leave()

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

    def initJobRunner(self, taggedDir):
        self.statusBar = self.gui.get_object('statusbar')
        self.contextsTreeView = self.gui.get_object('contextsTreeView')
        self.valuesTreeView = self.gui.get_object('valuesTreeView')

        jobRunnerContextId = self.statusBar.get_context_id('JobRunnerDescriptions')
        def setJobDescription(desc):
            gtk.gdk.threads_enter()
            try:
                if desc is None:
                    self.statusBar.pop(jobRunnerContextId)
                else:
                    self.statusBar.push(jobRunnerContextId, desc)
            finally:
                gtk.gdk.threads_leave()

        self.jobRunner = job.JobRunner([LoadTaggingsJob(self.saveAction, self.taggingsTreeView, self.taggingsListStore), LoadContextsAndValuesJob(taggedDir, self.contextsTreeView, self.valuesTreeView)], setJobDescription)
        self.jobRunner.start()

    def getTagEditDialogGladeFile(self):
        paths = [
            os.path.join('src', 'glade', 'tagEditDialog.glade'),
            os.path.expanduser(os.path.join('~', '.local', 'share', 'tagfs-gui', 'tagEditDialog.glade'))
            ]

        for p in paths:
            if not os.path.exists(p):
                continue

            return p

        raise Exception('Can\'t find tagEditDialog.glade file')

    def __init__(self, taggedPath):
        self.gui = gtk.Builder()
        # TODO determine path
        # TODO join path to make os independent
        self.gui.add_from_file(self.getTagEditDialogGladeFile())
        self.gui.connect_signals(self)

        self.saveAction = self.gui.get_object('saveAction')

        # TODO implement tag file support
        self.initTaggingsTreeView(taggedPath)

        self.editWindow = self.gui.get_object('editWindow')
        self.editWindow.set_title('tagging ' + taggedPath)
        self.editWindow.show()

        self.initJobRunner(taggedPath)

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
