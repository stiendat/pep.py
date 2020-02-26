import json

import tornado.web
import tornado.gen

from common.sentry import sentry
from common.web import requestsManager
from constants import exceptions
from helpers import chatHelper
from objects import glob

class handler(requestsManager.asyncRequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    @sentry.captureTornado
    def asyncGet(self):
        response = {"message": "unknow error"}
        try:
            # Check args
            if not requestsManager.checkArguments(self.request.arguments, ['k', 'command', 'matchID']):
                response['message'] = 'missing params'
                raise exceptions.invalidArgumentsException()
            
            # Check secret key
            key = self.get_argument('k')
            if key is None or key != glob.conf.config['server']['cikey']:
                response['message'] = 'bad secret key. you are not allowed to access to this api'
                raise exceptions.invalidArgumentsException()
            
            command = self.get_argument('command')
            matchID = self.get_argument('matchID')
            channel = '%23multi_{}'.format(matchID)
            available_commands = {
                'invite': '!mp invite ',
                'move': '!mp move ',
                'lock': '!mp lock',
                'unlock': '!mp unlock',
                'map': '!mp map ',
                'mods': '!mp mods ',
                'scorev': '!mp scorev ',
                'set': '!mp set ',
                'team': '!mp team ',
                'kick': '!mp kick',
                'start': '!mp start',
                'abort': '!mp abort',
                'close': '!mp close'
            }

            # Get args for subcommand
            user = self.get_argument('user')
            slot = self.get_argument('slot')
            beatmapID = self.get_argument('beatmapID')
            mods = self.get_arguments('mod')
            scorev = self.get_argument('scorev')
            gameMode = self.get_argument('mode')
            teamColor = self.get_argument('teamColor')

            # Main msg for Fokabot
            msg = available_commands.get(command, None)
            
            # LOL
            if msg is None:
                response['message'] = 'Bad command'
                raise exceptions.invalidArgumentsException()
            elif command == 'invite':
                if user is None:
                    response['message'] = 'Missing username'
                    raise exceptions.invalidArgumentsException()
                else:
                    msg = msg + user
            elif command == 'move':
                if user is None:
                    response['message'] = 'Missing username'
                    raise exceptions.invalidArgumentsException()
                elif slot is None:
                    response['message'] = 'Missing slot position'
                    raise exceptions.invalidArgumentsException()
                else:
                    msg = msg + user + ' ' + slot
            elif command == 'map':
                if beatmapID is None:
                    response['message'] = 'Missing beatmapID'
                    raise exceptions.invalidArgumentsException()
                else:
                    msg = msg + beatmapID
            elif command == 'mods':
                if mods is None:
                    response['message'] = 'Missing mod'
                    raise exceptions.invalidArgumentsException()
                else:
                    for mod in mods:
                        msg = msg + mod + ' '
            elif command == 'scorev':
                if scorev is None:
                    response['message'] = 'Missing score version (scorev)'
                    raise exceptions.invalidArgumentsException()
                else:
                    msg = msg + scorev
            elif command == 'set':
                if gameMode is None:
                    response['message'] = 'Missing game type. Only support h2h and teamvs'
                    raise exceptions.invalidArgumentsException()
                elif gameMode == 'h2h':
                    msg = msg + '0'
                elif gameMode == 'teamvs':
                    msg = msg + '2'
                else:
                    response['message'] = 'Not supported game type'
                    raise exceptions.invalidArgumentsException()
            elif command == 'team':
                if user is None:
                    response['message'] = 'Missing username'
                    raise exceptions.invalidArgumentsException()
                elif teamColor is None:
                    response['message'] = 'Missing team color'
                    raise exceptions.invalidArgumentsException()
                elif teamColor == 'red':
                    msg = msg + user + ' red'
                elif teamColor == 'blue':
                    msg = msg + user + ' blue'
                else:
                    response['message'] = 'Bad team color. Only support red and blue'
                    raise exceptions.invalidArgumentsException()

            chatHelper.sendMessage(glob.BOT_NAME, channel.encode().decode("ASCII", "ignore"), msg)
            statusCode = 200
            response['message'] = 'Success'

        except exceptions.invalidArgumentsException:
            statusCode = 400
        finally:
            self.write(json.dumps(response))
            self.set_status(statusCode)