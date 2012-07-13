"""
PyRC
An IRC client written in Python and Qt.

PyRC by Michael Allen C. Isaac is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
http://creativecommons.org/licenses/by-nc-sa/3.0/
"""

import asyncore, socket

from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from modInputFilter import txtInputFilter
from modIRCSocketThread import IRCSocketThread

from frmChannel import frmChannel

( Ui_frmMain, QMainWindow ) = uic.loadUiType( 'frmMain.ui' )

class frmMain( QMainWindow ):
    """frmMain inherits QMainWindow"""

    ui = None
    IRCSocket = None

    frmChannelArray = []
    frmPrivateArray = []

    #the window we wish to reside inside of
    mdiParent = None

    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )
        
        self.ui = Ui_frmMain()
        self.ui.setupUi( self )
        
        self.IRCSocket = IRCSocketThread()
        
        #when connecting a signal, omit any brackets ()
        self.IRCSocket.PacketEmitter.connect( self.processPacket )
        
        #tell the irc socket to connect to a server
        self.IRCSocket.connect( ('irc.freenode.net', 6667) )
        
        #start the socket's loop/thread
        self.IRCSocket.start()
        
        filter = txtInputFilter( self.ui.txtInput )
        filter.registerListener( self )
        
        self.ui.txtInput.installEventFilter( filter )
        

    def __del__ ( self ):
        self.ui = None
        

    #we might get stuffed in an MDI window.
    def setMdiParent( self, obj ):
        self.mdiParent = obj
        self.mdiParent.addSubWindow( self )
        

    def getMdiParent( self ):
        return self.mdiParent
        

    def closeChannelWindow( self, chn ):
        
        objChan = self.frmChannelArray[ self.getChannelWindowIndex( chn ) ]
        
        if (objChan):
            #we also should part the channel when its closed.
            self.send('PART ' + chn + ' :I click\'d the red X.')
            
            #delete it from the array of window objects
            del self.frmChannelArray[ self.getChannelWindowIndex( chn ) ]
        
        return

    def getChannelWindowIndex( self, chn ):
        #return the index of a channel within frmChannelArray
        x = 0
        while (x < len(self.frmChannelArray)):
            if(self.frmChannelArray[x].getChannel().lower() == chn.lower()):
                return x
            else:
                x = (x + 1)
            

    def getChannelWindow( self, chn ):
        #return the frmChannel object that matches the chn string
        #return [c for c in self.frmChannelArray if(c.getChannel().lower() == chn.lower())]
        try:
            return self.frmChannelArray[ self.getChannelWindowIndex( chn ) ]
        except:
            return None
        

    def createChannelWindow( self, chn ):
        c = frmChannel()
        
        c.setIRCSocket( self.IRCSocket ) 
        
        c.setChannel( chn )
        c.setWindowTitle( chn )
        
        c.onCloseEvent.connect( self.closeChannelWindow )
        
        c.setMdiParent( self.getMdiParent() )

        self.frmChannelArray.append( c )
        
        c.show()
        
        return
        
    
    def ShowMessageAsHTML( self, txt ):
        sb = self.ui.txtOutput.verticalScrollBar()
        
        self.ui.txtOutput.moveCursor(QTextCursor.End)
        self.ui.txtOutput.textCursor().insertHtml( txt + '<br>')
        
        sb.setValue( sb.maximum() )
        
    
    def ShowMessageAsText( self, txt ):
        sb = self.ui.txtOutput.verticalScrollBar()

        self.ui.txtOutput.moveCursor( QTextCursor.End )
        self.ui.txtOutput.textCursor().insertText( txt + '\n' )
        
        sb.setValue( sb.maximum() )
        

    def send( self, data ):
        self.IRCSocket.send( data + '\r\n' )
        return
        

    def processPacket( self, data ):
        
        QApplication.flush()
        
        #self.ShowMessageAsText( repr(data) )
        
        nick = self.IRCSocket.extractNick( data['p'] )
        
        self.ShowMessageAsText( '[%s(%s)] %s' % (data['c'], nick, data['m']) )
        
        if (data['c'] == '000'):
            pass
            
        elif (data['c'] == '002'): #this lines tells use a ton of shit, I should decode it.
            self.setWindowTitle( data['p'] )
            pass

        #elif (data['c'] == '004'):
        
        elif (data['c'] == '005'): #this lines tells use a ton of shit, I should decode it.
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
            chan = self.getChannelWindow( data['a'][2] )
            
            #get a list of names, 
            nameList = data['m'].split(' ')
            
            #empty dict
            bleh = {}
            
            #compile names in to dict's,
            #where the keys are names, and data are modes
            
            for name in nameList:
                if((name[0] == '@') or (name[0] == '+')):
                    bleh[name[1:]] = name[0]
                else:
                    bleh[name] = ''
                    
            #pass names to Channel
            
            chan.addNames( bleh )
            
        
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
        #elif (data['c'] == 'QUIT'):    #
        #elif (data['c'] == 'MODE'):    #
        #elif (data['c'] == 'TOPIC'):   #
        
        elif (data['c'] == 'PRIVMSG'): #
        
            #who joined the channel
            who = self.IRCSocket.extractNick( data['p'] )
            
            #argument 0 is the channel name, or nickname
            chn = data['a'][0]
            objChan = self.getChannelWindow( chn )
            
            #the user joined a room, and we should create a window for italic
            if(objChan):
                objChan.ShowMessageAsHTML( '&#60;<b><font color=purple>%s</font></b>&#62; %s' % (who, data['m']))
                
            
        
        elif (data['c'] == 'PING'):    #
            self.ShowMessageAsText( '*** PONG (' + data['a'][0] + ')\n' )
            self.send('PONG :' + data['a'][0] )
            
        
        elif (data['c'] == 'JOIN'):    #
            #what is our nickname
            me = self.IRCSocket.getNick()
            
            #who joined the channel
            who = self.IRCSocket.extractNick( data['p'] )
            
            #argument 0 is the channel
            chn = data['a'][0]
            objChan = self.getChannelWindow( chn )
            
            if(me.lower() == who.lower()):
                #the user joined a room, and we should create a window for italic
                self.createChannelWindow( chn )
            else:
                if(objChan):
                    objChan.ShowMessageAsHTML( '<font color=green><b>[  +  ]</b> %s joined %s.</font>' % (who, chn) )
                    objChan.addName( who )
                
            
        
        elif (data['c'] == 'PART'):    #
            #what is our nickname
            me = self.IRCSocket.getNick()
            
            #who joined the channel
            who = self.IRCSocket.extractNick( data['p'] )
            
            #argument 0 is the channel name
            chn = data['a'][0]
            objChan = self.getChannelWindow( chn )
            
            if(me.lower() == who.lower()):
                #the user joined a room, and we should create a window for italic
                if(objChan):
                    objChan.ShowMessageAsText( '\n*** You parted the channel ***\n' )
                    
            else:
                objChan.ShowMessageAsHTML( '<font color=red><b>[  -  ] %s parted %s.</font>' % (who, chn) )
                objChan.removeName( who )
            
                
        else:
            pass
            #self.ShowMessageAsText( repr(data) )
        

    def processInput( self, caller, txt ):
        #this function is required by the txtInputFilter class so that
        #this object will recieve input from the event filter.
        
        #if we're working with a QString convert it
        
        self.IRCSocket.send( txt + '\r\n' )
        self.ShowMessageAsHTML( '<br><b>&#60;sent&#62; ' + txt + '</b><br>'  )
        
        return 
        

