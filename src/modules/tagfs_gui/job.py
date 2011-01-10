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

import threading

class JobRunner(threading.Thread):
    
    def __init__(self, jobs, jobDescCallback):
        threading.Thread.__init__(self)

        self.jobDescCallback = jobDescCallback

        self.jobsLock = threading.Lock()
        self.jobs = jobs
        self.executedJob = None

    def run(self):
        while True:
            with self.jobsLock:
                self.executedJob = None

                if len(self.jobs) == 0:
                    break

                job = self.jobs.pop(0)

                self.executedJob = job

            try:
                self.jobDescCallback(job.description)

                job.run()

                # TODO catch job errors and show to user
            finally:
                with self.jobsLock:
                    self.executedJob = None

                self.jobDescCallback(None)

        # TODO use logger insteaf of print
        print 'JobRunner is done'

    def stop(self):
        with self.jobsLock:
            if not self.executedJob is None:
                self.executedJob.stop = True

            while len(self.jobs) > 0:
                self.jobs.pop()
