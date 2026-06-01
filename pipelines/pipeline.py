import asyncio
import time

from pipelines.rpop_fetch.rpop_fetch import fetch as rpop_fetch


class Pipeline:
    pipeline_namespace = "this_pipeline"
    required_tables = []
    run_on_start = False
    cron_run_expression = None
    db_driver = None
    running = False
    start_time = None

    def execute(self):
        pass

    def __init__(self, db_driver):
        self.db_driver = db_driver
        for table in self.required_tables:
            self.db_driver.add_table(table)

        if self.run_on_start:
            self.execute()



class KcomebacksPipeline(Pipeline):
    pipeline_namespace = "kcomebacks"
    required_tables = []
    run_on_start = True
    cron_run_expression = "* */8 * * *"

    def execute(self):
        if not self.running:
            # asyncronously run pipeline as to not delay the response
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self.__execute_async())


    def __execute_async(self):
        process = True
        self.start_time = time.time()
        data = rpop_fetch()

        stop_time = time.time()
        # // TODO: add run to timeline table
        process = False



# def create_all(): create all pipelines

