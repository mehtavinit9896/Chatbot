from chatterbot.logic import LogicAdapter
from chatterbot.storage import StorageAdapter
from chatterbot import utils
from chatterbot import comparisons
from textblob import TextBlob
from chatterbot.conversation import Statement
import requests
import xml.etree.ElementTree as ET

class MainLogic(LogicAdapter):
    """
    This is an abstract class that represents the interface
    that all logic adapters should implement.

    :param statement_comparison_function: The dot-notated import path to a statement comparison function.
                                          Defaults to ``levenshtein_distance``.

    :param response_selection_method: The a response selection method.
                                      Defaults to ``get_first_response``.
    """

    def __init__(self, **kwargs):
        super(MainLogic, self).__init__(**kwargs)
        storage_adapter = kwargs.get('storage_adapter', 'chatterbot.storage.SQLStorageAdapter')
        self.storage = utils.initialize_class(storage_adapter, **kwargs)
		
    def can_process(self, statement):
        """
        Determines whether it is appropriate for this
        adapter to respond to the user input.
        """
        response = self.process(statement)
        return response.confidence
			
    def process(self, statement):
        """
        Takes a statement string.
        Returns the equation from the statement with the mathematical terms solved.
        """
		
        # Learn that the user's input was a valid response to the chat bot's previous output
        
        percent = self.compare_statements(statement, Statement('Account details for account id'))
        self.response_statement = Statement('Not Found')		
        if percent > 0.6 :
            input = TextBlob(statement.text)
            tokens = input.words
            i = 0
            for token in tokens:
                if token == 'Id' or token == 'id' :
                    i=tokens.index(token)
            account=tokens[i+1]
            import requests
            import xml.etree.ElementTree as ET
            url="http://tcrmw03zatcrh.vodacom.corp:7777/eai_enu/start.swe?WSDL&SWEExtSource=SecureWebService&SWEExtCmd=Execute&Username=UAT15&Password=Passw0rd1"
            #headers = {'content-type': 'application/soap+xml'}
            headers = {'content-type': 'text/xml','SOAPAction':'"document/http://siebel.com/asi/V0:SWICustomerPartyQueryById"'}
            body ="""<?xml version="1.0" encoding="UTF-8"?>
		            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v0="http://siebel.com/asi/V0">
	            		<soapenv:Header/>
			            <soapenv:Body>
			              <v0:SWICustomerPartyQueryById_Input>
				             <v0:PrimaryRowId>{}</v0:PrimaryRowId>
			              </v0:SWICustomerPartyQueryById_Input>
			            </soapenv:Body>
		            </soapenv:Envelope>""".format(account)
            response = requests.post(url,data=body,headers=headers)
            tree = ET.fromstring(response.content)
            name=tree.find('.//{http://www.siebel.com/xml/SWICustomerPartyIO}Name').text
            email=tree.find('.//{http://www.siebel.com/xml/SWICustomerPartyIO}EmailAddress').text
            city=tree.find('.//{http://www.siebel.com/xml/SWICustomerPartyIO}City').text			
            status=tree.find('.//{http://www.siebel.com/xml/SWICustomerPartyIO}AccountStatus').text
            out=Statement('\n'+'Name:'+str(name)+'\n'+'Email Address:'+str(email)+'\n'+'City:'+str(city)+'\n'+'Account Status:'+status)
            self.response_statement = Statement(out)
            
        self.response_statement.confidence = percent
        
        return self.response_statement
