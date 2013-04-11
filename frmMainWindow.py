"""
PyRC
An IRC client written in Python and Qt.

PyRC by Michael Allen C. Isaac is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
http://creativecommons.org/licenses/by-nc-sa/3.0/
"""

import sys
import pprint

from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

( Ui_frmMainWindow, QMainWindow ) = uic.loadUiType( 'frmMainWindow.ui' )

from modInputFilter import InputFilter
from modIRCSocketThread import IRCSocketThread

def joinIter(i, c):
    return c.join(i)

class objChannel( object ):

    def __init__ ( self, parent = None ):
        #string containing the name of the IRC Channel
        self.channel = None

        #buffer
        self.message_buffer = ''

        #topic of the channel
        self.topic = ''

        #names on the channel, we use a dict for name/mode data, where the nicknames are keys, and the data is user modes (@+)
        self.names = {}

        return

    def addName( self, name ):
        self.names[name] = ''
        pass


    def removeName( self, name ):
        #this is the prefixed name of the user.
        if (name in list(self.names)):
            del self.names[name]
        return


    def addNames( self, nnames = {} ):
        #merge names with the existing
        self.names.update( nnames )
        return


    def getNames( self ):
        return self.names


    def getDestinationID( self ):
        return self.channel


    def getChannel( self ):
        return self.channel


    def setChannel( self, chn ):
        self.channel = chn


    def ShowMessageAsHTML( self, txt ):
        self.message_buffer += '<br />' + txt


    def ShowMessageAsText( self, txt ):
        self.message_buffer += '\n' + txt


    def ShowMessageInTable( self, colOne, colTwo ):
        #I'd rather use div tags here, but the QTextBrower component is broken, it wont handle width: or float: styles
        t = '''
            <table>
            <tr>
                <td align="right" style="width:0px;float:left;">
                    $colOne
                </td>
                <td align="left" style="width:0px;float:left;">
                    $colTwo
                </td>
            </tr>
            </table>
            ''' #% str(pxSize * 18)

        self.message_buffer += ( t.replace('$colOne', colOne).replace('$colTwo', colTwo))


    def getMessageBuffer(self):
        return self.message_buffer


class frmMainWindow ( QMainWindow ):
    """frmMainWindow inherits QMainWindow"""

    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )

        #array of channel objects
        self.objChannelArray = []

        #array of private message users
        self.objPrivateArray = []

        #array of buffer IDs, Server(), Users, #Channels, etc. Dict which points to objects with a .getMessageBuffer() function
        self.dictDestination = {}

        # string that identifies our object
        self.destinationID = ''
        self.message_buffer = ''

        self.destinationID = 'Server'

        self.ui = Ui_frmMainWindow()
        self.ui.setupUi( self )

        self.ffilter = InputFilter( self.ui.txtInput )
        self.ffilter.registerListener( self )

        self.ui.txtInput.installEventFilter( self.ffilter )

        self.fontInfo = QFontInfo( self.ui.txtOutput.textCursor().charFormat().font() )

        self.ui.listDestination.itemClicked.connect(self.listDestination_OnClick)

        self.AddDestinationObject( self )

        self.IRCSocket = IRCSocketThread()
        self.IRCSocket.PacketEmitter.connect( self.processPacket )
        self.IRCSocket.connect( ('irc.freenode.net', 6667) )

        #start the socket's loop/thread
        self.IRCSocket.start()

        #Select the first destination
        self.ui.listDestination.setCurrentRow(0)

        pass


    def getDestinationID(self):
        return self.destinationID


    def listDestination_OnClick( self, data ):
        self.UpdateMainDisplay()

        dID = self.GetWorkingDestinationObject().getDestinationID()

        if( dID[0] == '#' ):
            self.UpdateNames( self.getChannelObject( dID ) )
        else:
            self.ui.listNames.clear()


    def UpdateNames( self, objChan ):
        self.ui.listNames.clear()

        #objChan = self.getChannelObject( chn )

        if( objChan ):
            namez = objChan.getNames()

            for n in list(namez.keys()):
                #add the data first because it will contain a mode character if any
                self.ui.listNames.addItem( n )


    def AddDestinationObject( self, obj ):
        #add a buffer object by id, used to update the left panel
        if(hasattr( obj, 'getDestinationID' )):

            #we need to make sure it has the right functions
            self.dictDestination[ obj.getDestinationID() ] = obj
            self.ui.listDestination.addItem( obj.getDestinationID() )
        else:
            print('ERROR -- AddDestinationObject object passed does not contain getID()')
            sys.exit(0)


    def GetDestinationObject(self, dID ):
        #return the object if there is one, otherwise return none.
        return self.dictDestination[ dID ]


    def RemoveDestinationObject(self, dID ):
        try:
            del self.dictDestination[ dID ]
        except Exception:
            pass


    def GetWorkingDestinationObject( self ):
        return self.GetDestinationObject( self.ui.listDestination.currentItem().text() )


    def processPacket( self, data ):
        #remove any HTML from the data we display
        data['m'] = self.sanitizeHtml( data['m'] )

        #debugging
        print(pprint.PrettyPrinter(indent = 4).pformat( data ))
        if (data['c'] == '000'):   #unknown
            pass
        elif (data['c'] == '002'): #tells which server we're on.
            self.setWindowTitle( data['p'] )
            pass
        elif (data['c'] == '004'): #unknown
            pass
        elif (data['c'] == '005'):
            #these lines tell us all about server settings,
            #including supported modes, channels, and encoding.
            who = self.IRCSocket.extractNick( data['p'] )
            self.ShowMessageAsHTML( '[%s(%s)] %s' % (data['c'], who, repr( data['a'] ) ) )
            pass
        #elif (data['c'] == '200'): #RPL_TRACELINK           "Link <version & debug level> <destination> <next server>"
        #elif (data['c'] == '201'): #RPL_TRACECONNECTING     "Try. <class> <server>"
        #elif (data['c'] == '202'): #RPL_TRACEHANDSHAKE      "H.S. <class> <server>"
        #elif (data['c'] == '203'): #RPL_TRACEUNKNOWN        "???? <class> [<client IP address in dot form>]"
        #elif (data['c'] == '204'): #RPL_TRACEOPERATOR       "Oper <class> <nick>"
        #elif (data['c'] == '205'): #RPL_TRACEUSER           "User <class> <nick>"
        #elif (data['c'] == '206'): #RPL_TRACESERVER         "Serv <class> <int>S <int>C <server> <nick!user|*!*>@<host|server>"
        #elif (data['c'] == '208'): #RPL_TRACENEWTYPE        "<newtype> 0 <client name>"
        #elif (data['c'] == '211'): #RPL_STATSLINKINFO       "<linkname> <sendq> <sent messages> <sent bytes> <received messages> <received bytes> <time open>"
        #elif (data['c'] == '212'): #RPL_STATSCOMMANDS       "<command> <count>"
        #elif (data['c'] == '213'): #RPL_STATSCLINE          "C <host> * <name> <port> <class>"
        #elif (data['c'] == '214'): #RPL_STATSNLINE          "N <host> * <name> <port> <class>"
        #elif (data['c'] == '215'): #RPL_STATSILINE          "I <host> * <host> <port> <class>"
        #elif (data['c'] == '216'): #RPL_STATSKLINE          "K <host> * <username> <port> <class>"
        #elif (data['c'] == '218'): #RPL_STATSYLINE          "Y <class> <ping frequency> <connect frequency> <max sendq>"
        #elif (data['c'] == '219'): #RPL_ENDOFSTATS          "<stats letter> :End of /STATS report"
        #elif (data['c'] == '221'): #RPL_UMODEIS             "<user mode string>"
        #elif (data['c'] == '241'): #RPL_STATSLLINE          "L <hostmask> * <servername> <maxdepth>"
        #elif (data['c'] == '242'): #RPL_STATSUPTIME         ":Server Up %d days %d:%02d:%02d"
        #elif (data['c'] == '243'): #RPL_STATSOLINE          "O <hostmask> * <name>"
        #elif (data['c'] == '244'): #RPL_STATSHLINE          "H <hostmask> * <servername>"
        #elif (data['c'] == '251'): #RPL_LUSERCLIENT         ":There are <integer> users and <integer> invisible on <integer> servers"
        #elif (data['c'] == '252'): #RPL_LUSEROP             "<integer> :operator(s) online"
        #elif (data['c'] == '253'): #RPL_LUSERUNKNOWN        "<integer> :unknown connection(s)"
        #elif (data['c'] == '254'): #RPL_LUSERCHANNELS       "<integer> :channels formed"
        #elif (data['c'] == '255'): #RPL_LUSERME             ":I have <integer> clients and <integer> servers"
        #elif (data['c'] == '256'): #RPL_ADMINME             "<server> :Administrative info"
        #elif (data['c'] == '257'): #RPL_ADMINLOC1           ":<admin info>"
        #elif (data['c'] == '258'): #RPL_ADMINLOC2           ":<admin info>"
        #elif (data['c'] == '259'): #RPL_ADMINEMAIL          ":<admin info>"
        #elif (data['c'] == '261'): #RPL_TRACELOG            "File <logfile> <debug level>"
        #elif (data['c'] == '300'): #RPL_NONE                Dummy reply number. Not used.
        #elif (data['c'] == '301'): #RPL_AWAY                "<nick> :<away message>"
        #elif (data['c'] == '302'): #RPL_USERHOST            ":[<reply>{<space><reply>}]"
        #elif (data['c'] == '303'): #RPL_ISON                ":[<nick> {<space><nick>}]"
        #elif (data['c'] == '305'): #RPL_UNAWAY              ":You are no longer marked as being away"
        #elif (data['c'] == '306'): #RPL_NOWAWAY             ":You have been marked as being away"
        #elif (data['c'] == '311'): #RPL_WHOISUSER           "<nick> <user> <host> * :<real name>"
        #elif (data['c'] == '312'): #RPL_WHOISSERVER         "<nick> <server> :<server info>"
        #elif (data['c'] == '313'): #RPL_WHOISOPERATOR       "<nick> :is an IRC operator"
        #elif (data['c'] == '314'): #RPL_WHOWASUSER          "<nick> <user> <host> * :<real name>"
        #elif (data['c'] == '315'): #RPL_ENDOFWHO            "<name> :End of /WHO list"
        #elif (data['c'] == '317'): #RPL_WHOISIDLE           "<nick> <integer> :seconds idle"
        #elif (data['c'] == '318'): #RPL_ENDOFWHOIS          "<nick> :End of /WHOIS list"
        #elif (data['c'] == '319'): #RPL_WHOISCHANNELS       "<nick> :{[@|+]<channel><space>}"
        #elif (data['c'] == '321'): #RPL_LISTSTART           "Channel :Users Name"
        #elif (data['c'] == '322'): #RPL_LIST                "<channel> <# visible> :<topic>"
        #elif (data['c'] == '323'): #RPL_LISTEND             ":End of /LIST"
        #elif (data['c'] == '324'): #RPL_CHANNELMODEIS       "<channel> <mode> <mode params>"
        #elif (data['c'] == '328'): #RPL_URLDATA?            "<channel> :<url>
        #elif (data['c'] == '331'): #RPL_NOTOPIC             "<channel> :No topic is set"
        #elif (data['c'] == '332'): #RPL_TOPIC               "<channel> :<topic>"
        #elif (data['c'] == '333'): #RPL_TOPICSETBY?
        #elif (data['c'] == '341'): #RPL_INVITING            "<channel> <nick>"
        #elif (data['c'] == '342'): #RPL_SUMMONING           "<user> :Summoning user to IRC"
        #elif (data['c'] == '351'): #RPL_VERSION             "<version>.<debuglevel> <server> :<comments>"
        #elif (data['c'] == '352'): #RPL_WHOREPLY            "<channel> <user> <host> <server> <nick> <H|G>[*][@|+] :<hopcount> <real name>"}
        elif (data['c'] == '353'): #RPL_NAMREPLY            "<channel> :[[@|+]<nick> [[@|+]<nick> [...]]]"

            #names are delimited with a space in the message data;  data['m']
            #this can happen multipule times for a singlge channel

            #locate the channel
            objChan = self.getChannelObject( data['a'][2] )

            #get a list of names,
            nameList = data['m'].split(' ')

            #empty dict
            bleh = {}

            #compile names in to dict's,
            for name in nameList:
                if((name[0] == '@') or (name[0] == '+')):
                    #keys are names, modes are data
                    bleh[name[1:]] = name[0]
                else:
                    bleh[name] = ''

            #pass names to Channel

            objChan.addNames( bleh )


        #elif (data['c'] == '364'): #RPL_LINKS               "<mask> <server> :<hopcount> <server info>"
        #elif (data['c'] == '365'): #RPL_ENDOFLINKS          "<mask> :End of /LINKS list"}
        #elif (data['c'] == '366'): #RPL_ENDOFNAMES          "<channel> :End of /NAMES list"
        #elif (data['c'] == '367'): #RPL_BANLIST             "<channel> <banid>"
        #elif (data['c'] == '368'): #RPL_ENDOFBANLIST        "<channel> :End of channel ban list"
        #elif (data['c'] == '369'): #RPL_ENDOFWHOWAS         "<nick> :End of WHOWAS"
        #elif (data['c'] == '371'): #RPL_INFO                ":<string>"
        #elif (data['c'] == '372'): #RPL_MOTD                ":- <text>"
        #elif (data['c'] == '374'): #RPL_ENDOFINFO           ":End of /INFO list"
        #elif (data['c'] == '375'): #RPL_MOTDSTART           ":- <server> Message of the day - "
        #elif (data['c'] == '376'): #RPL_ENDOFMOTD           ":End of /MOTD command"
        #elif (data['c'] == '381'): #RPL_YOUREOPER           ":You are now an IRC operator"
        #elif (data['c'] == '382'): #RPL_REHASHING           "<config file> :Rehashing"
        #elif (data['c'] == '391'): #RPL_TIME                "<server> :<string showing server's local time>"
        #elif (data['c'] == '392'): #RPL_USERSSTART          ":UserID Terminal Host"
        #elif (data['c'] == '393'): #RPL_USERS               ":%-8s %-9s %-8s"
        #elif (data['c'] == '394'): #RPL_ENDOFUSERS          ":End of users"
        #elif (data['c'] == '395'): #RPL_NOUSERS             ":Nobody logged in"

        #elif (data['c'] == '401'): #ERR_NOSUCHNICK          "<nickname> :No such nick/channel"
        #elif (data['c'] == '402'): #ERR_NOSUCHSERVER        "<server name> :No such server"
        #elif (data['c'] == '403'): #ERR_NOSUCHCHANNEL       "<channel name> :No such channel"
        #elif (data['c'] == '404'): #ERR_CANNOTSENDTOCHAN    "<channel name> :Cannot send to channel"
        #elif (data['c'] == '405'): #ERR_TOOMANYCHANNELS     "<channel name> :You have joined too many channels"
        #elif (data['c'] == '406'): #ERR_WASNOSUCHNICK       "<nickname> :There was no such nickname"
        #elif (data['c'] == '407'): #ERR_TOOMANYTARGETS      "<target> :Duplicate recipients. No message delivered"
        #elif (data['c'] == '409'): #ERR_NOORIGIN            ":No origin specified"
        #elif (data['c'] == '411'): #ERR_NORECIPIENT         ":No recipient given (<command>)"
        #elif (data['c'] == '412'): #ERR_NOTEXTTOSEND        ":No text to send"
        #elif (data['c'] == '413'): #ERR_NOTOPLEVEL          "<mask> :No toplevel domain specified"
        #elif (data['c'] == '414'): #ERR_WILDTOPLEVEL        "<mask> :Wildcard in toplevel domain"
        #elif (data['c'] == '421'): #ERR_UNKNOWNCOMMAND      "<command> :Unknown command"
        #elif (data['c'] == '422'): #ERR_NOMOTD              ":MOTD File is missing"
        #elif (data['c'] == '423'): #ERR_NOADMININFO         "<server> :No administrative info available"
        #elif (data['c'] == '424'): #ERR_FILEERROR           ":File error doing <file op> on <file>"
        #elif (data['c'] == '431'): #ERR_NONICKNAMEGIVEN     ":No nickname given"
        #elif (data['c'] == '432'): #ERR_ERRONEUSNICKNAME    "<nick> :Erroneus nickname"
        #elif (data['c'] == '433'): #ERR_NICKNAMEINUSE       "<nick> :Nickname is already in use"
        #elif (data['c'] == '436'): #ERR_NICKCOLLISION       "<nick> :Nickname collision KILL"
        #elif (data['c'] == '441'): #ERR_USERNOTINCHANNEL    "<nick> <channel> :They aren't on that channel"
        #elif (data['c'] == '442'): #ERR_NOTONCHANNEL        "<channel> :You're not on that channel"
        #elif (data['c'] == '443'): #ERR_USERONCHANNEL       "<user> <channel> :is already on channel"
        #elif (data['c'] == '444'): #ERR_NOLOGIN             "<user> :User not logged in"
        #elif (data['c'] == '445'): #ERR_SUMMONDISABLED      ":SUMMON has been disabled"
        #elif (data['c'] == '446'): #ERR_USERSDISABLED       ":USERS has been disabled"
        #elif (data['c'] == '451'): #ERR_NOTREGISTERED       ":You have not registered"
        #elif (data['c'] == '461'): #ERR_NEEDMOREPARAMS      "<command> :Not enough parameters"
        #elif (data['c'] == '462'): #ERR_ALREADYREGISTRED    ":You may not reregister"
        #elif (data['c'] == '463'): #ERR_NOPERMFORHOST       ":Your host isn't among the privileged"
        #elif (data['c'] == '464'): #ERR_PASSWDMISMATCH      ":Password incorrect"
        #elif (data['c'] == '465'): #ERR_YOUREBANNEDCREEP    ":You are banned from this server"
        #elif (data['c'] == '467'): #ERR_KEYSET              "<channel> :Channel key already set"
        #elif (data['c'] == '471'): #ERR_CHANNELISFULL       "<channel> :Cannot join channel (+l)"
        #elif (data['c'] == '472'): #ERR_UNKNOWNMODE         "<char> :is unknown mode char to me"
        #elif (data['c'] == '473'): #ERR_INVITEONLYCHAN      "<channel> :Cannot join channel (+i)"
        #elif (data['c'] == '474'): #ERR_BANNEDFROMCHAN      "<channel> :Cannot join channel (+b)"
        #elif (data['c'] == '475'): #ERR_BADCHANNELKEY       "<channel> :Cannot join channel (+k)"
        #elif (data['c'] == '481'): #ERR_NOPRIVILEGES        ":Permission Denied- You're not an IRC operator"
        #elif (data['c'] == '482'): #ERR_CHANOPRIVSNEEDED    "<channel> :You're not channel operator"
        #elif (data['c'] == '483'): #ERR_CANTKILLSERVER      ":You cant kill a server!"
        #elif (data['c'] == '491'): #ERR_NOOPERHOST          ":No O-lines for your host"
        #elif (data['c'] == '501'): #ERR_UMODEUNKNOWNFLAG    ":Unknown MODE flag"
        #elif (data['c'] == '502'): #ERR_USERSDONTMATCH      ":Cant change mode for other users"
        #elif (data['c'] == '512'): #                        ":Authorization required to use this nickname"

        #elif (data['c'] == 'MODE'):    #
        #elif (data['c'] == 'TOPIC'):   #

        elif (data['c'] == 'NICK'):   #
            #[NICK(pythonTestClient)] AWESOME

            me = self.IRCSocket.getNick()

            who = self.IRCSocket.extractNick( data['p'] )

            newnick = data['m']

            if (who.lower() == me.lower()):
                x = 0

                self.IRCSocket.setNick( newnick )

                while (x < len(self.objChannelArray)):
                    self.objChannelArray[x].removeName( who )
                    self.objChannelArray[x].addName( newnick )
                    x = (x + 1)


        elif (data['c'] == 'QUIT'):     #

            who = self.IRCSocket.extractNick( data['p'] )

            #when someone quits the server, remove their name
            #all open channels.

            x = 0
            while (x < len(self.objChannelArray)):
                self.objChannelArray[x].removeName( who )
                x = (x + 1)


        elif (data['c'] == 'PRIVMSG'):  #

            #who joined the channel
            #no defined at the top of the fucntion
            who = self.IRCSocket.extractNick( data['p'] )

            #argument 0 is the channel name, or nickname

            whoto = data['a'][0]

            objChan = self.getChannelObject( whoto )


            if(objChan):
                #objChan.ShowMessageAsHTML( '&#60;<font color=purple>%s</font>&#62; %s' % (who, data['m']))
                objChan.ShowMessageInTable( ('<font color=purple>%s</font>' % self.padThis(who)), data['m'])
            else:
                #this would be the private message handler for direct messages
                self.ShowMessageAsHTML('[ --> ] &#60;<font color=green>%s</font>&#62; %s' % ( who, data['m'] ))


        elif (data['c'] == 'PING'):    #
            self.ShowMessageAsHTML( '\n*** PONG (' + data['a'][0] + ')\n' )
            self.send('PONG :' + data['a'][0] )


        elif (data['c'] == 'JOIN'):    #
            #what is our nickname
            me = self.IRCSocket.getNick()

            #who joined the channel
            who = self.IRCSocket.extractNick( data['p'] )

            #argument 0 is the channel
            chn = data['a'][0]
            objChan = self.getChannelObject( chn )

            if(me.lower() == who.lower()):
                #the user joined a room, and we should create a window for italic
                self.createChannelObject( chn )
            else:
                if(objChan):
                    objChan.ShowMessageInTable( ('<font color=green>%s</font>' % self.padThis('[+]')), ('%s joined %s.' % (who, chn)) )
                    objChan.addName( who )
                    self.UpdateNames( objChan )




        elif ((data['c'] == 'PART') or (data['c'] == 'QUIT')):    #
            #what is our nickname
            me = self.IRCSocket.getNick()

            #who joined the channel
            who = self.IRCSocket.extractNick( data['p'] )

            #argument 0 is the channel name
            chn = data['a'][0]
            objChan = self.getChannelObject( chn )

            if(me.lower() == who.lower()):
                #the user joined a room, and we should create a window for italic
                if(objChan):
                    objChan.ShowMessageAsHTML( '\n*** You parted the channel ***\n' )

            else:
                objChan.ShowMessageInTable( ('<font color=red>%s</font>' % self.padThis('[-]')), ('%s left %s.' % (who, chn)) )
                objChan.removeName( who )
                self.UpdateNames( objChan )


        else:
            who = self.IRCSocket.extractNick( data['p'] )
            self.ShowMessageAsHTML( '[%s(%s)] %s' % (data['c'], who, data['m']) )
            pass

        QApplication.flush()
        self.UpdateMainDisplay()


    def padThis( self, what):
        return what.rjust(16, ' ').replace(' ', '&nbsp;')


    def sanitizeHtml( self, html ):
        #because we will be using an HTML based display component;
        #it is necessary to replace control characters <> with HTML escape codes.

        html = html.replace('<', '&#60;')
        html = html.replace('>', '&#62;')

        return html


    def ShowMessageAsHTML( self, txt ):
        self.message_buffer += '<br />' + txt


    def ShowMessageAsText( self, txt ):
        self.message_buffer += '\n' + txt


    def ShowMessageInTable( self, colOne, colTwo ):
        #I'd rather use div tags here, but the QTextBrower component is broken, it wont handle width: or float: styles
        t = '''
            <table>
            <tr>
                <td align="right" style="width:0px;float:left;">
                    $colOne
                </td>
                <td align="left" style="width:0px;float:left;">
                    $colTwo
                </td>
            </tr>
            </table>
            ''' #% str(pxSize * 18)

        self.message_buffer += (t.replace('$colOne', colOne).replace('$colTwo', colTwo))


    def getMessageBuffer(self):
        return self.message_buffer


    def UpdateMainDisplay( self ):
        #buffer ID we'll use to display text
        #dID = self.ui.listDestination.currentItem().text()
        #if(dID is not None):
            #objWithBuffer = self.GetDestinationObject(dID)
            #self.ui.txtOutput.setHtml( objWithBuffer.getMessageBuffer() )
            #sb = self.ui.txtOutput.verticalScrollBar()
            #sb.setValue( sb.maximum() )

        try:
            self.ui.txtOutput.setHtml( self.GetWorkingDestinationObject().getMessageBuffer() )
            sb = self.ui.txtOutput.verticalScrollBar()
            sb.setValue( sb.maximum() )
        except Exception:
            return


    def closeChannelObject( self, chn ):

        objChan = self.objChannelArray[ self.getChannelObjectIndex( chn ) ]

        if (objChan):
            #we also should part the channel when its closed.
            self.send('PART ' + chn + ' :I click\'d the red X.')

            #delete it from the array of window objects
            del self.objChannelArray[ self.getChannelObjectIndex( chn ) ]

        return


    def getChannelObjectIndex( self, chn ):
        #return the index of a channel within objChannelArray
        x = 0
        while (x < len(self.objChannelArray)):
            if(self.objChannelArray[x].getChannel().lower() == chn.lower()):
                return x
            else:
                x = (x + 1)


    def getChannelObject( self, chn ):
        #return the objChannel object that matches the chn string
        #return [c for c in self.objChannelArray if(c.getChannel().lower() == chn.lower())]
        try:
            return self.objChannelArray[ self.getChannelObjectIndex( chn ) ]
        except:
            return None


    def createChannelObject( self, chn ):
        c = objChannel()
        c.setChannel( chn )

        self.objChannelArray.append( c )
        self.AddDestinationObject( c )

        return


    def send( self, data ):
        self.IRCSocket.send( data + '\r\n' )
        return


    def processCommand( self, cline ):

        objDest = self.GetWorkingDestinationObject()

        #if the command was empty, skip it
        if((cline == '') or (objDest is None)):
            return

        cmd = cline.split(' ')
        cmd[0] = cmd[0].lower()

        if(cmd[0] == 'msg'):
            who = cmd[1]
            what = joinIter(cmd[2:], ' ')

            self.send('PRIVMSG %s :%s' % (who, what))
            objDest.ShowMessageInTable(self.padThis('<-- MSG(%s)' % (who)), what)
        elif(cmd[0] == 'id'):
            what = joinIter(cmd[1:], ' ')
            self.send('PRIVMSG NickServ :IDENTIFY %s' % (what))
            objDest.ShowMessageInTable('[IDENTIFY]', '******')
        else:
            self.send(joinIter(cmd[0:], ' '))
            pass

        return


    def processInput( self, caller, txt ):
        #this function is required by the txtInputFilter class so that this object will recieve input from the event filter.
        txt = self.sanitizeHtml( txt )

        if (self.IRCSocket):
            if(txt):
                if(txt[0] == '/'):
                    self.processCommand(txt[1:])
                    #this should turn into a command handler at some point
                    #self.IRCSocket.send( txt[1:] + '\r\n' )

                    #try and display the command we've sent on the current destination objects's buffer
                    #try:
                    #    self.GetWorkingDestinationObject().ShowMessageInTable( '%s' % (self.padThis('[command]')), txt[1:] )
                    #except Exception:
                    #    pass

                    #self.ShowMessageInTable( '%s' % (self.padThis('[command]')), txt[1:] )
                else:
                    #if our current destination object's id begins with a #, then its a channel
                    dID = self.GetWorkingDestinationObject().getDestinationID()

                    if( dID[0] == '#' ):
                        objChan = self.getChannelObject( dID )
                        self.IRCSocket.send('PRIVMSG %s :%s' % (objChan.getChannel(), txt))
                        objChan.ShowMessageInTable(('<font color=purple><b>%s</b></font>' % self.padThis(self.IRCSocket.getNick())), txt)
            else:
                return

        self.UpdateMainDisplay()
        self.ui.txtInput.setPlainText('')
        return


    def __del__ ( self ):
        self.ui = None
