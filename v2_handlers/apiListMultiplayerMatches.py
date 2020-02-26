import json
from datetime import datetime

import tornado.web
import tornado.gen

from common.sentry import sentry
from common.web import requestsManager
from constants import exceptions
from objects import glob
from common.ripple.userUtils import getSafeUsername
from common.constants.gameModes import getGamemodeFull


class handler(requestsManager.asyncRequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    @sentry.captureTornado
    def asyncGet(self):
        statusCode = 200
        response = []
        match_object = {
            'matchID': None,
            'matchName': None,
            'beatmapID': None,
            'beatmapName': None,
            'gameMode': None,
            'host': None,
            'createTime': None,
            'inProgress': None,
            'isStarting': None,
            'isTourney': None
        }

        matchList = glob.matches.matches

        for match in matchList:
            match_object['matchID'] = match
            match_object['matchName'] = matchList[match].matchName
            match_object['beatmapID'] = matchList[match].beatmapID
            match_object['beatmapName'] = matchList[match].beatmapName
            match_object['gameMode'] = getGamemodeFull(matchList[match].gameMode)
            match_object['host'] = getSafeUsername(matchList[match].hostUserID)
            match_object['createTime'] = datetime.utcfromtimestamp(matchList[match].createTime).strftime('%Y-%m-%d %H:%M:%S')
            match_object['inProgress'] = matchList[match].inProgress
            match_object['isStarting'] = matchList[match].isStarting
            match_object['isTourney'] = matchList[match].isTourney
            response.append(match_object)

        self.write(json.dumps(response))
        self.set_status(statusCode)

        
