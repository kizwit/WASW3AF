'''
htaccessMethods.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''

import core.controllers.outputManager as om
import core.data.kb.knowledgeBase as kb
import core.data.kb.vuln as vuln
import core.data.constants.severity as severity
import core.data.constants.httpConstants as http_constants

from core.controllers.basePlugin.baseAuditPlugin import baseAuditPlugin


class htaccessMethods(baseAuditPlugin):
    '''
    Find misconfigurations in the "<LIMIT>" configuration of Apache.
    @author: Andres Riancho ( andres.riancho@gmail.com )
    '''
    
    def __init__(self):
        baseAuditPlugin.__init__(self)
        
        # Internal variables
        self._authURIs = []
        self._bad_methods = [ http_constants.UNAUTHORIZED, 
                    http_constants.NOT_IMPLEMENTED, http_constants.METHOD_NOT_ALLOWED]

    def audit(self, freq ):
        '''
        Tests an URL for htaccess misconfigurations.
        
        @param freq: A fuzzableRequest
        '''
        auth_URL_list = [ v.getURL() for v in kb.kb.getData( 'httpAuthDetect', 'auth' ) ]
        if freq.getURL() in auth_URL_list:
            # Try to get/post/put/index that uri and check that all
            # responses are 401
            self._check_methods( freq.getURL() )
        else:
            # Just in case grep plugin did not find this before
            # this only happends if the page wasnt requested
            response = self._uri_opener.GET( freq.getURL() , cache=True )
            if response.getCode() == http_constants.UNAUTHORIZED:
                self._check_methods( freq.getURL() )
                # not needed, the grep plugin will do this for us
                # kb.kb.save( 'httpAuthDetect', 'auth', response )

    def _check_methods( self, url ):
        '''
        Perform some requests in order to check if we are able to retrieve
        some data with methods that may be wrongly enabled.
        '''
        allowed_methods = []
        for method in ['GET', 'POST', 'ABCD', 'HEAD']:
            method_functor = getattr( self._uri_opener, method )
            try:
                response = apply( method_functor, (url,) , {} )
                code = response.getCode()
            except:
                pass
            else:
                if code not in self._bad_methods:
                    allowed_methods.append( method )
        
        if len(allowed_methods)>0:
            v = vuln.vuln()
            v.setPluginName(self.getName())
            v.setURL( url )
            v.setName( 'Misconfigured access control' )
            v.setSeverity(severity.MEDIUM)
            msg = 'The resource: "'+ url + '" requires authentication but the access'
            msg += ' is misconfigured and can be bypassed using these methods: ' 
            msg += ', '.join(allowed_methods) + '.'
            v.setDesc( msg )
            v['methods'] = allowed_methods
            kb.kb.append( self , 'auth' , v )
            om.out.vulnerability( v.getDesc(), severity=v.getSeverity() )             
                
    def getPluginDeps( self ):
        '''
        @return: A list with the names of the plugins that should be run before the
        current one.
        '''
        return ['grep.httpAuthDetect']
    
    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin finds .htaccess misconfigurations in the LIMIT configuration parameter.
        
        This plugin is based on a paper written by Frame and madjoker from 
        kernelpanik.org. The paper is called : "htaccess: bilbao method exposed"
        
        The idea of the technique (and the plugin) is to exploit common misconfigurations
        of .htaccess files like this one:
        
            <LIMIT GET>
                require valid-used
            </LIMIT>
        
        The configuration only allows authenticated users to perform GET requests, but POST
        requests (for example) can be performed by any user.
        '''
