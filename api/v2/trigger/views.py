from django.http import JsonResponse

from api.v2.trigger.processor import KCOMEBACKS_PIPELINE_PROCESS, KcomebacksProcessor


def trigger_kcomebacks_fetcher(request):
    if not KCOMEBACKS_PIPELINE_PROCESS:
        KCOMEBACKS_PIPELINE_PROCESS = KcomebacksProcessor()
    return KCOMEBACKS_PIPELINE_PROCESS.process_kcomebacks_fetch(request)

