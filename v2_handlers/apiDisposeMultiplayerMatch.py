import json

import tornado.web
import tornado.gen

from common.sentry import sentry
from common.web import requestsManager
from constants import exceptions
from objects import glob

class handler(requestsManager.asyncRequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    @sentry.captureTornado
    def asyncGet(self):
        response = {
            'message': 'bad request'
        }

        try:
            # Check args
            if not requestsManager.checkArguments(self.request.arguments, ['k', 'matchID']):
                response['message'] = 'invalid params'
                raise exceptions.invalidArgumentsException()

            # Check ci key
            key = self.get_argument('k')
            if key is None or key != glob.conf.config['server']['cikey']:
                response['message'] = 'Bad secret key. You are not allowed to access to this api'
                raise exceptions.invalidArgumentsException()

            matchID = self.get_argument('matchID')
            glob.matches.disposeMatch(int(matchID))
            statusCode = 200

        except exceptions.invalidArgumentsException:
            statusCode = 400
        finally:
            self.write(json.dumps(response))
            self.set_status(statusCode)
