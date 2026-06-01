import asyncio
import time

from django.http import JsonResponse

from pipelines.rpop_fetch.rpop_fetch import fetch

KCOMEBACKS_PIPELINE_PROCESS = None

class KcomebacksProcessor:

    def __init__(self):
        pass

    def run_kcomebacks_pipeline(self):
        process = True
        self.start_time = time.time()
        data = fetch()

        stop_time = time.time()
        #// TODO: add run to timeline table
        process = False

    def process_kcomebacks_fetch(self, request):
        #//TODO: return average time in response message, calculate remaining ETA when already running and total ETA when starting right now.
        if not self.running:
            # asyncronously run pipeline as to not delay the response
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self.run_kcomebacks_pipeline)

            return JsonResponse({"message": "Processing started..."}, status=200)
        else:
            return JsonResponse({"message": "Already running"}, status=400)

    def is_alive(self):
        return self.running



