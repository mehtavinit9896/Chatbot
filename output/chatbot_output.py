from __future__ import unicode_literals
from chatterbot.output.output_adapter import OutputAdapter


class ChatOutput(OutputAdapter):
    """
    An output adapter that allows a ChatterBot instance to send
    responses to a Gitter room.
    """

    def __init__(self, **kwargs):
        super(ChatOutput, self).__init__(**kwargs)
        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.directline_host = kwargs.get('directline_host', 'http://localhost:8080/ChatUI')
        self.proxies = {'http': 'http://zactn13002p1:8080','https': 'http://zactn13002p1:8080'}       

        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'charset': 'utf-8'
        }

        # Join the Gitter room
        #room_data = self.join_room(self.gitter_room)
        #self.room_id = room_data.get('id')

    def _validate_status_code(self, response):
        code = response.status_code
        if code not in [200, 201]:
            raise self.HTTPStatusException('{} status code recieved'.format(code))

    def join_room(self, room_name):
        """
        Join the specified Gitter room.
        """
        import requests

        endpoint = '{}'.format(self.directline_host)
        response = requests.post(
            endpoint,
            headers=self.headers,
            #json={'uri': room_name},
            #proxies= self.proxies
        )
        self.logger.info('{} status joining room {}'.format(
            response.status_code, endpoint
        ))
        self._validate_status_code(response)
        print (response.json())
        return response.json()

    def send_message(self, text):
        """
        Send a message to a Gitter room.
        """
        import requests
        print (text)
        endpoint = '{}/rest/ChatService/chatMessages/{}'.format(self.directline_host,text)
        response = requests.get(
            endpoint,
            headers=self.headers
            #json={'text': text}
            #proxies= self.proxies
        )
        self.logger.info('{} sending message to {}'.format(
            response.status_code, endpoint
        ))
        self._validate_status_code(response)
        return response.json()

    def process_response(self, statement, session_id=None):
        if(statement.text!=""):
            return statement
        self.send_message(statement.text)
        return statement

    class HTTPStatusException(Exception):
        """
        Exception raised when unexpected non-success HTTP
        status codes are returned in a response.
        """

        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)
