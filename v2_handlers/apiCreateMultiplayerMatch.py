import json

import tornado.web
import tornado.gen

from common.sentry import sentry
from common.web import requestsManager
from constants import exceptions
from objects import glob
from common.constants.gameModes import getGameModeForMatchAPI
from common import generalUtils

class handler(requestsManager.asyncRequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    @sentry.captureTornado
    def asyncGet(self):
        statusCode = 400
        response = {
            'message': "invalid parameters"
        }

        try:
            # Check args
            if not requestsManager.checkArguments(self.request.arguments, ['k', 'matchName', 'gameMode', 'isTourney']):
                raise exceptions.invalidArgumentsException()

            # Check ci key
            key = self.get_argument('k')
            if key is None or key != glob.conf.config["server"]["cikey"]:
                response['message'] = 'Bad secret key. You are not allowed to access to this api.'
                raise exceptions.invalidArgumentsException()
            
            matchName = self.get_argument('matchName')
            gameMode = getGameModeForMatchAPI(self.get_argument('gameMode'))
            isTourney = self.get_argument('isTourney')

            if isTourney == 'True':
                isTourney = True
            elif isTourney == 'False':
                isTourney = False
            else:
                response['message'] = 'isTourney is requirement not optional. Only accepts True or False'
                raise exceptions.invalidArgumentsException()

            if gameMode is None:
                response['message'] = 'Oh my we only accepts gameMode std, taiko, ctb and mania'
                raise exceptions.invalidArgumentsException()

            matchID = glob.matches.createMatch(matchName, generalUtils.stringMd5(generalUtils.randomString(32)), 0, "Tournament", "", gameMode, -1, isTourney=isTourney)
            glob.matches.matches[matchID].sendUpdates()
            response = {
                "matchID": matchID
            }
            statusCode = 200
        except exceptions.invalidArgumentsException:
            statusCode = 400
        
        self.write(json.dumps(response))
        self.set_status(statusCode)
            
            


