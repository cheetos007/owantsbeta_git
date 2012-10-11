from django.utils import simplejson as json
from django.utils.encoding import smart_str
from django.http import HttpResponse

class AJAXError(Exception):

    def __init__(self, msg, **kwargs):
        self.msg = msg
        self.extra = kwargs  # Any kwargs will be appended to the output.

    def get_response(self):
        error = {
            'message': smart_str(self.msg),
            'status': 'nok'
        }
        error.update(self.extra)

        response = HttpResponse()
        response.content = json.dumps(error, indent=4)
        return response