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
