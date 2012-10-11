from django.utils.translation import ugettext as _
from decorator import decorator
from ajax.exceptions import AJAXError
from django.http import HttpResponse, Http404
from django.utils import simplejson as json
from django.utils.translation import ugettext as _
from django.conf import settings
from decorator import decorator


@decorator
def login_required(f, *args, **kwargs):
    if not args[0].user.is_authenticated():
        raise AJAXError(_('User must be authenticated.'), status_code = 403)

    return f(*args, **kwargs)



def json_response(response_type='application/json'):

    @decorator
    def inner_response(f, *args, **kwargs):
        """Wrap a view in JSON.

        This decorator runs the given function and looks out for ajax.AJAXError's,
        which it encodes into a proper HttpResponse object. If an unknown error
        is thrown it's encoded as a 500.

        All errors are then packaged up with an appropriate Content-Type and a JSON
        body that you can inspect in JavaScript on the client. They look like:

        {
            "message": "Error message here.", 
            "code": 500
        }

        Please keep in mind that raw exception messages could very well be exposed
        to the client if a non-AJAXError is thrown.
        """ 
        try:
            result = f(*args, **kwargs)
            if isinstance(result, AJAXError):
                raise result
            else:
                if not 'status' in result and isinstance(result, dict):
                    result['status'] = 'ok'
                result = HttpResponse(json.dumps(result, indent=4))
        except AJAXError, e:
            result = e.get_response()
        except Http404, e:
            result = AJAXError(e.__str__()).get_response()
        except Exception, e:
            import sys
            type, message, trace = sys.exc_info()
            if settings.DEBUG:
                import traceback 
                tb = [{'file': l[0], 'line': l[1], 'in': l[2], 'code': l[3]} for 
                    l in traceback.extract_tb(trace)]
                result = AJAXError(message, traceback=tb).get_response()
            else:
                result = AJAXError(message).get_response()
    
        result['Content-Type'] = response_type
        return result

    return inner_response