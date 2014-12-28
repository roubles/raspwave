//-----------------------------------------------------------------------------
//
//	Main.cpp
//
//	Minimal application to test OpenZWave.
//
//	Creates an OpenZWave::Driver and the waits.  In Debug builds
//	you should see verbose logging to the console, which will
//	indicate that communications with the Z-Wave network are working.
//
//	Copyright (c) 2010 Mal Lansell <mal@openzwave.com>
//
//
//	SOFTWARE NOTICE AND LICENSE
//
//	This file is part of OpenZWave.
//
//	OpenZWave is free software: you can redistribute it and/or modify
//	it under the terms of the GNU Lesser General Public License as published
//	by the Free Software Foundation, either version 3 of the License,
//	or (at your option) any later version.
//
//	OpenZWave is distributed in the hope that it will be useful,
//	but WITHOUT ANY WARRANTY; without even the implied warranty of
//	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//	GNU Lesser General Public License for more details.
//
//	You should have received a copy of the GNU Lesser General Public License
//	along with OpenZWave.  If not, see <http://www.gnu.org/licenses/>.
//
//-----------------------------------------------------------------------------

#include <unistd.h>
#include <stdlib.h>
#include <pthread.h>
#include <dirent.h>
#include <sys/socket.h>
#include <arpa/inet.h> //inet_addr
#include <errno.h>
#include "Options.h"
#include "Manager.h"
#include "Driver.h"
#include "Node.h"
#include "Group.h"
#include "Notification.h"
#include "value_classes/ValueStore.h"
#include "value_classes/Value.h"
#include "value_classes/ValueBool.h"
#include "command_classes/SensorBinary.h"
#include "platform/Log.h"

using namespace OpenZWave;

        bool temp = false;


static uint32 g_homeId = 0;
static bool   g_initFailed = false;

typedef struct
{
	uint32			m_homeId;
	uint8			m_nodeId;
	bool			m_polled;
	list<ValueID>	m_values;
}NodeInfo;

static list<NodeInfo*> g_nodes;
static pthread_mutex_t g_criticalSection;
static pthread_cond_t  initCond  = PTHREAD_COND_INITIALIZER;
static pthread_mutex_t initMutex = PTHREAD_MUTEX_INITIALIZER;

// #RASPWAVE
typedef struct {
    uint8 nodeId;
    uint8 event;
    char value[100];
    char state[100];
    uint8 commandClassId;
    uint64 fullHex;
} NotificationData;

typedef struct {
    NotificationData notificationData;
    char pathToRobot[200];
} RobotCall;

// #RASPWAVE ZWAVE SERVER
#define MAX_FDS          10
#define LISTENER_PORT    55556
#define LISTENER_INDEX   0
#define MAX_PACKET_DATA  1000

typedef struct packetData_t_ {
    int           bytes;
    char data[MAX_PACKET_DATA];
    int           fd;
} packetData_t;

typedef struct socketTable_t_ {
    int fdTable[MAX_FDS];
} socketTable_t;

static socketTable_t socketTable;


//-----------------------------------------------------------------------------
// <GetNodeInfo>
// Return the NodeInfo object associated with this notification
//-----------------------------------------------------------------------------
NodeInfo* GetNodeInfo
(
	Notification const* _notification
)
{
	uint32 const homeId = _notification->GetHomeId();
	uint8 const nodeId = _notification->GetNodeId();
	for( list<NodeInfo*>::iterator it = g_nodes.begin(); it != g_nodes.end(); ++it )
	{
		NodeInfo* nodeInfo = *it;
		if( ( nodeInfo->m_homeId == homeId ) && ( nodeInfo->m_nodeId == nodeId ) )
		{
			return nodeInfo;
		}
	}

	return NULL;
}

// #RASPWAVE
void* callRobot(void * p) {
    RobotCall* rc = (RobotCall*) p;

    char cmd[200] = {0};
    sprintf(cmd, "/usr/local/bin/raspscpt %s %d %d %d", rc->pathToRobot, rc->notificationData.nodeId, rc->notificationData.event, rc->notificationData.commandClassId);
    system(cmd);
    Log::Write(LogLevel_Info, rc->notificationData.nodeId, cmd);

    // Free up stuff
    delete rc;
    pthread_exit(NULL);
}

// #RASPWAVE
bool hasEnding (std::string const &fullString, std::string const &ending)
{
    if (fullString.length() >= ending.length()) {
        return (0 == fullString.compare (fullString.length() - ending.length(), ending.length(), ending));
    } else {
        return false;
    }
}

// #RASPWAVE
void callRobotsAtPath (string path, NotificationData* nd) {
    DIR *dir;
    struct dirent *ent;
    if ((dir = opendir (path.c_str())) != NULL) {
        /* print all the files and directories within directory */
        while ((ent = readdir (dir)) != NULL) {
            if (strcmp(ent->d_name, ".") == 0) {
                continue;
            }
            if (strcmp(ent->d_name, "..") == 0) {
                continue;
            } 
            if (strcmp(ent->d_name, "RobotUtils.py") == 0) {
                continue;
            } 
            if (hasEnding(ent->d_name, ".py") == false) {
                Log::Write(LogLevel_Info,"Skiping non python robot file: %s\n", ent->d_name);
                continue;
            }
            char *fullpath = (char*)malloc(strlen(path.c_str()) + strlen(ent->d_name) + 2);
            sprintf(fullpath, "%s/%s", path.c_str(), ent->d_name);

            // Build RobotCall
            RobotCall* rc = new RobotCall();
            rc->notificationData.nodeId = nd->nodeId;
            rc->notificationData.event = nd->event;
            rc->notificationData.commandClassId = nd->commandClassId;
            strcpy(rc->pathToRobot, fullpath);

            pthread_t threadId;
            pthread_create(&threadId, NULL, callRobot, (void*)rc);

            delete fullpath;
        }
        closedir (dir);
    } else {
        /* could not open directory */
        Log::Write(LogLevel_Info, "Folder does not exist: %s\n", path.c_str());
    }
}

// #RASPWAVE
void callUserHomeRobots (NotificationData* nd) {
    callRobotsAtPath("~/.raspwave/robots", nd);
}

// #RASPWAVE
void callEtcRobots (NotificationData* nd) {
    callRobotsAtPath("/etc/raspwave/robots", nd);
}

// #RASPWAVE
void* callAllRobots(void * p) {
    NotificationData* nd = (NotificationData*) p;

    callEtcRobots(nd);
    callUserHomeRobots(nd);

    delete nd;
    pthread_exit(NULL);
}

int SetBoolValue(int nodeid, int commandclass, bool value)
{
    bool res;

    pthread_mutex_lock( &g_criticalSection );
    for( list<NodeInfo*>::iterator it = g_nodes.begin(); it != g_nodes.end(); ++it ) {
        NodeInfo* nodeInfo = *it;
        Log::Write(LogLevel_Info, "Working on node: %d", nodeInfo->m_nodeId);
        if( nodeInfo->m_nodeId != nodeid ) continue;
        Log::Write(LogLevel_Info, "Still working on node: %d", nodeid);
        for( list<ValueID>::iterator it2 = nodeInfo->m_values.begin(); it2 != nodeInfo->m_values.end(); ++it2 ) {
            ValueID v = *it2;
            Log::Write(LogLevel_Info, "Working on value: %d", v.GetCommandClassId());
            if( v.GetCommandClassId() == commandclass) {
                res = Manager::Get()->SetValue(v, value);
                Log::Write(LogLevel_Info, "SetValue result=%d", res);
                return res;
            }
        }
    }
    pthread_mutex_unlock( &g_criticalSection );
    return 0; //return false
}

bool addSocketToTable(int fd) 
{
    int idx;

    // start at 1 since the listener is always index 0
    for (idx = 1; idx < MAX_FDS; idx++) {
        if (socketTable.fdTable[idx] == 0) {
            socketTable.fdTable[idx] = fd;
            Log::Write(LogLevel_Info, "%s adding socket=%d to table index=%d", __FUNCTION__, fd, idx);
            return true;
        }
    }

    Log::Write(LogLevel_Error, "%s table full could not add socket to table", __FUNCTION__);
    return false;
}

void removeSocketFromTable(int fd)
{
    int idx;

    Log::Write(LogLevel_Info, "%s closing connection fd=%d", __FUNCTION__, fd);
    close(fd);

    // start at 1 since the listener is always index 0
    for (idx = 1; idx < MAX_FDS; idx++) {
        if (socketTable.fdTable[idx] == fd) {
            socketTable.fdTable[idx] = 0;
            Log::Write(LogLevel_Info, "%s removing socket=%d from table at index=%d", __FUNCTION__, fd, idx);
            return;
        }
    }

}

void closeAllSockets(void)
{
    int idx;

    for (idx = 0; idx < MAX_FDS; idx++) {
        if (socketTable.fdTable[idx]) {
            close(socketTable.fdTable[idx]);
        }
    }
}

bool openListenerSocket(void)
{
    struct sockaddr_in sock;
    int                fd;
   
    fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (fd < 0) {
        Log::Write(LogLevel_Error, "%s cannot create listener socket", __FUNCTION__);
        return false;
    }

    sock.sin_family = AF_INET;
    sock.sin_addr.s_addr = htonl(INADDR_ANY);
    sock.sin_port = htons(LISTENER_PORT);

    if (bind(fd, (struct sockaddr *)&sock, sizeof(sock)) == -1) {
        Log::Write(LogLevel_Error, "%s bind failed", __FUNCTION__);
        close(fd);
        return false;
    }

    if (listen(fd, 5) == -1) {
        Log::Write(LogLevel_Error, "%s listen failed errno=%d", __FUNCTION__, errno);
        close(fd);
        return false;
    }

    socketTable.fdTable[LISTENER_INDEX] = fd;
   
    return true;

}

// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

void acceptConnection(fd_set *selectList, int *maxFd)
{
    struct sockaddr_storage remoteAddr;
    socklen_t               len;
    char                    remoteIP[INET6_ADDRSTRLEN];
    int                     newFd;  

    len = sizeof(remoteAddr);
    newFd = accept(socketTable.fdTable[LISTENER_INDEX], 
	                            (struct sockaddr*) (&remoteAddr), &len);
    if (newFd == -1) {
        Log::Write(LogLevel_Error, "%s accept connection failed", __FUNCTION__);
        return;
    }     
     
    // if the clients don't close, we don't want to accept another connection
    if (addSocketToTable(newFd) == false) {
        Log::Write(LogLevel_Error, "%s cannot accept connection, table full", __FUNCTION__);
        close(newFd);
        return;
    }
    
    // add accepted connection to master list
    FD_SET(newFd, selectList);
    // keep track of the max FD number
    if (newFd > *maxFd) {
        *maxFd = newFd;
    }
    
    inet_ntop(remoteAddr.ss_family, get_in_addr((struct sockaddr*)&remoteAddr), remoteIP, INET6_ADDRSTRLEN);

    Log::Write(LogLevel_Info, "selectserver: new connection from %s on socket %d", remoteIP, newFd);
}

void *handlePacket(void *arg)
{
    packetData_t *msg;
    int nodeid = 0;
    int commandclass = 0;
    char* command = NULL;
    char* value = NULL;

    msg = (packetData_t*)arg;

    Log::Write(LogLevel_Info, "recv data fd=%d:[%s]", msg->fd, msg->data);
    char *saveptr;
    char* ch = strtok_r(msg->data, ",", &saveptr);
    int i = 0;
    while (ch != NULL) {
        if (i == 0) {
            command = strdup(ch);
        }
        if (i == 1) {
            nodeid = atoi(ch);
        }
        if (i == 2) {
            commandclass = atoi(ch);
        }
        if (i == 3) {
            value = strdup(ch);
        }
        ch = strtok_r(NULL, ",", &saveptr);
        i++;
    }

    Log::Write(LogLevel_Info, "%s %d %d %s", command, nodeid, commandclass, value);
    int retVal = 0;
    if (strcasecmp("setboolvalue", command) == 0) {
        if( !strcasecmp( "true", value) ) {
            retVal = SetBoolValue(nodeid, commandclass, true);
        } else if( !strcasecmp( "false", value ) ) {
            retVal = SetBoolValue(nodeid, commandclass, false);
        } else {
            retVal = SetBoolValue(nodeid, commandclass, false);
        }
    } else {
        Log::Write(LogLevel_Error, "Unknown command: %s", command);
    }

    char ret[10] = {0};
    sprintf(ret, "%d", retVal);

    // just send some data back
    if (send(msg->fd, &ret, 10, 0) == -1) {
        Log::Write(LogLevel_Error, "send failed");
    }

    free(command);
    free(value);
    free(msg);

    return NULL;
}

void readDataOnConnection(int fd, fd_set *selectList)
{
    int             nbytes;
    pthread_t       threadId;
    packetData_t    *msg;

    msg = (packetData_t*)malloc(sizeof(packetData_t));

    memset(msg, 0, sizeof(packetData_t));
    nbytes = recv(fd, msg->data, MAX_PACKET_DATA-1, 0);

    if (nbytes <= 0) {
        if (nbytes == 0) {
            Log::Write(LogLevel_Info, "%s client closed connection", __FUNCTION__);
        } else {
            Log::Write(LogLevel_Error, "%s recv returned error", __FUNCTION__);
        }
        // remove socket from select list
        FD_CLR(fd, selectList);
        // this will also close the socket
        removeSocketFromTable(fd);
        return;
    }

    // null terminate
    msg->data[nbytes] = 0;
    msg->bytes = nbytes;
    msg->fd = fd;

    if (pthread_create(&threadId, NULL, handlePacket, (void*)msg) != 0) {
        Log::Write(LogLevel_Error, "%s could not create handlePacket thread", __FUNCTION__);
        free(msg);
    } else {
        pthread_detach(threadId);
    }

}

void *threadReadSocket(void *arg)
{
    fd_set                  localList;
    fd_set                  masterList;
    int                     maxFd = 0, i;
  
    memset(&socketTable, 0, sizeof(socketTable_t));

    if (openListenerSocket() == false) {
        printf("exiting cannot open listener socket");
        Log::Write(LogLevel_Error, "exiting cannot open listener socket");
        pthread_exit(0);
    }

    // open sockets for selecting
    FD_ZERO(&localList);
    FD_ZERO(&masterList);
    // add listener socket into master select list
    FD_SET(socketTable.fdTable[LISTENER_INDEX], &masterList);
    maxFd = socketTable.fdTable[LISTENER_INDEX];

    printf("listening for connections ...\n");
    Log::Write(LogLevel_Info, "listening for connections ...");

    while(1) {
        // copy the master, we do this since select changes the set 
        localList = masterList;
        if (select(maxFd+1, &localList, NULL, NULL, NULL) == -1) {
            Log::Write(LogLevel_Error, "%s select returned error", __FUNCTION__);
	    //closeAllSockets();
	    pthread_exit(0);
        }
    
        for(i = 0; i <= maxFd; i++) {
            if (FD_ISSET(i, &localList)) {     
                // check listener first
                if (i == socketTable.fdTable[LISTENER_INDEX]) {
                    acceptConnection(&masterList, &maxFd);
                } else {
                     // got some data
                     readDataOnConnection(i, &masterList);
                    
                }
            }
        }
    }
}

// #RASPWAVE
void* postNotification(void * p) {
    NotificationData* nd = (NotificationData*) p;

    char cmd[200] = {0};
    sprintf(cmd, "/etc/raspwave/pylib/postNotification.py %d %s %s %d %d %llu", nd->nodeId, nd->state, nd->value, nd->event, nd->commandClassId, nd->fullHex);
    system(cmd);
    Log::Write(LogLevel_Info, nd->nodeId, cmd);

    delete nd;
    pthread_exit(NULL);
}

void notifyEvent (Notification const* _notification) {
    // Build NotificationData
    ValueID valueId = _notification->GetValueID();
    NotificationData* nd = new NotificationData();
    nd->nodeId = valueId.GetNodeId();
    nd->commandClassId = valueId.GetCommandClassId();
    nd->fullHex = valueId.GetId();

    //Get event
    nd->event = _notification->GetEvent();
    if (nd->event == 0) {
        strcpy(nd->state, "close");
        strcpy(nd->value, "False");
    } else if (nd->event == 255) {
        strcpy(nd->state, "open");
        strcpy(nd->value, "True");
    } else {
        strcpy(nd->state, "unknown");
        strcpy(nd->value, "unknown");
    }

    pthread_t threadId;
    pthread_create(&threadId, NULL, postNotification, (void*)nd);
}

void notifyValue (Notification const* _notification) {
    ValueID valueId = _notification->GetValueID();
    if (valueId.GetCommandClassId() != SensorBinary::StaticGetCommandClassId()) {
        Log::Write(LogLevel_Info,"Ignoring notification because it is of command class: %d", valueId.GetCommandClassId());
        return;
    }

    // Build NotificationData
    NotificationData* nd = new NotificationData();
    nd->nodeId = valueId.GetNodeId();
    nd->commandClassId = valueId.GetCommandClassId();
    nd->fullHex = valueId.GetId();

    //Get value
    string value;
    Manager::Get()->GetValueAsString(valueId, &value);
    Log::Write(LogLevel_Info,"Got value: %s", value.c_str());
    strcpy(nd->value, value.c_str());

    //Normalization
    if (strcasecmp(nd->value, "true")) {
        nd->event = 0;
        strcpy(nd->state, "close");
    } else  if (strcasecmp(nd->value, "false")) {
        nd->event = 255;
        strcpy(nd->state, "open");
    } else {
        strcpy(nd->state, "unknown");
    }

    pthread_t threadId;
    pthread_create(&threadId, NULL, postNotification, (void*)nd);
}

//-----------------------------------------------------------------------------
// <OnNotification>
// Callback that is triggered when a value, group or node changes
//-----------------------------------------------------------------------------
void OnNotification
(
	Notification const* _notification,
	void* _context
)
{
        Log::Write(LogLevel_Info, "Got Notification: %d", _notification->GetType());
	// Must do this inside a critical section to avoid conflicts with the main thread
	pthread_mutex_lock( &g_criticalSection );

	switch( _notification->GetType() )
	{
		case Notification::Type_ValueAdded:
		{
			if( NodeInfo* nodeInfo = GetNodeInfo( _notification ) )
			{
				// Add the new value to our list
				nodeInfo->m_values.push_back( _notification->GetValueID() );
			}
			break;
		}

		case Notification::Type_ValueRemoved:
		{
			if( NodeInfo* nodeInfo = GetNodeInfo( _notification ) )
			{
				// Remove the value from out list
				for( list<ValueID>::iterator it = nodeInfo->m_values.begin(); it != nodeInfo->m_values.end(); ++it )
				{
					if( (*it) == _notification->GetValueID() )
					{
						nodeInfo->m_values.erase( it );
						break;
					}
				}
			}
			break;
		}

		case Notification::Type_ValueChanged:
		{
                        notifyValue(_notification);
			break;
		}

		case Notification::Type_Group:
		{
			// One of the node's association groups has changed
			if( NodeInfo* nodeInfo = GetNodeInfo( _notification ) )
			{
				nodeInfo = nodeInfo;		// placeholder for real action
			}
			break;
		}

		case Notification::Type_NodeAdded:
		{
			// Add the new node to our list
			NodeInfo* nodeInfo = new NodeInfo();
			nodeInfo->m_homeId = _notification->GetHomeId();
			nodeInfo->m_nodeId = _notification->GetNodeId();
			nodeInfo->m_polled = false;		
			g_nodes.push_back( nodeInfo );
		        if (temp == true) {
			    Manager::Get()->CancelControllerCommand( _notification->GetHomeId() );
                        }
			break;
		}

		case Notification::Type_NodeRemoved:
		{
			// Remove the node from our list
			uint32 const homeId = _notification->GetHomeId();
			uint8 const nodeId = _notification->GetNodeId();
			for( list<NodeInfo*>::iterator it = g_nodes.begin(); it != g_nodes.end(); ++it )
			{
				NodeInfo* nodeInfo = *it;
				if( ( nodeInfo->m_homeId == homeId ) && ( nodeInfo->m_nodeId == nodeId ) )
				{
					g_nodes.erase( it );
					delete nodeInfo;
					break;
				}
			}
			break;
		}

		case Notification::Type_NodeEvent:
		{
                        // #RASPWAVE
                        notifyEvent(_notification);
			break;
		}

		case Notification::Type_PollingDisabled:
		{
			if( NodeInfo* nodeInfo = GetNodeInfo( _notification ) )
			{
				nodeInfo->m_polled = false;
			}
			break;
		}

		case Notification::Type_PollingEnabled:
		{
			if( NodeInfo* nodeInfo = GetNodeInfo( _notification ) )
			{
				nodeInfo->m_polled = true;
			}
			break;
		}

		case Notification::Type_DriverReady:
		{
			g_homeId = _notification->GetHomeId();
			break;
		}

		case Notification::Type_DriverFailed:
		{
			g_initFailed = true;
			pthread_cond_broadcast(&initCond);
			break;
		}

		case Notification::Type_AwakeNodesQueried:
		case Notification::Type_AllNodesQueried:
		case Notification::Type_AllNodesQueriedSomeDead:
		{
			pthread_cond_broadcast(&initCond);
			break;
		}

		case Notification::Type_DriverReset:
		case Notification::Type_Notification:
		case Notification::Type_NodeNaming:
		case Notification::Type_NodeProtocolInfo:
		case Notification::Type_NodeQueriesComplete:
		default:
		{
		}
	}

	pthread_mutex_unlock( &g_criticalSection );
}

//-----------------------------------------------------------------------------
// <main>
// Create the driver and then wait
//-----------------------------------------------------------------------------
int main( int argc, char* argv[] )
{
	pthread_mutexattr_t mutexattr;

	pthread_mutexattr_init ( &mutexattr );
	pthread_mutexattr_settype( &mutexattr, PTHREAD_MUTEX_RECURSIVE );
	pthread_mutex_init( &g_criticalSection, &mutexattr );
	pthread_mutexattr_destroy( &mutexattr );

	pthread_mutex_lock( &initMutex );


	printf("Starting MinOZW with OpenZWave Version %s\n", Manager::getVersionAsString().c_str());

	// Create the OpenZWave Manager.
	// The first argument is the path to the config files (where the manufacturer_specific.xml file is located
	// The second argument is the path for saved Z-Wave network state and the log file.  If you leave it NULL 
	// the log file will appear in the program's working directory.
	//Options::Create( "../../../config/", "", "" );
	Options::Create( "/etc/raspwave/openzwave/config/", "/var/log/raspwave", "" );
	Options::Get()->AddOptionInt( "PollInterval", 500 );
	Options::Get()->AddOptionBool( "IntervalBetweenPolls", true );
	Options::Get()->AddOptionBool("ValidateValueChanges", true);
	Options::Get()->Lock();

	Manager::Create();

	// Add a callback handler to the manager.  The second argument is a context that
	// is passed to the OnNotification method.  If the OnNotification is a method of
	// a class, the context would usually be a pointer to that class object, to
	// avoid the need for the notification handler to be a static.
	Manager::Get()->AddWatcher( OnNotification, NULL );

	// Add a Z-Wave Driver
	// Modify this line to set the correct serial port for your PC interface.

#ifdef DARWIN
	string port = "/dev/cu.usbserial";
#elif WIN32
        string port = "\\\\.\\COM6";
#else
	string port = "/dev/ttyUSB0";
#endif
	if ( argc > 1 )
	{
		port = argv[1];
	}
	if( strcasecmp( port.c_str(), "usb" ) == 0 )
	{
		Manager::Get()->AddDriver( "HID Controller", Driver::ControllerInterface_Hid );
	}
	else
	{
		Manager::Get()->AddDriver( port );
	}

	// Now we just wait for either the AwakeNodesQueried or AllNodesQueried notification,
	// then write out the config file.
	// In a normal app, we would be handling notifications and building a UI for the user.
	pthread_cond_wait( &initCond, &initMutex );

	// Since the configuration file contains command class information that is only 
	// known after the nodes on the network are queried, wait until all of the nodes 
	// on the network have been queried (at least the "listening" ones) before
	// writing the configuration file.  (Maybe write again after sleeping nodes have
	// been queried as well.)
	if( !g_initFailed )
	{

		// The section below demonstrates setting up polling for a variable.  In this simple
		// example, it has been hardwired to poll COMMAND_CLASS_BASIC on the each node that 
		// supports this setting.
		pthread_mutex_lock( &g_criticalSection );
		for( list<NodeInfo*>::iterator it = g_nodes.begin(); it != g_nodes.end(); ++it )
		{
			NodeInfo* nodeInfo = *it;

			// skip the controller (most likely node 1)
			if( nodeInfo->m_nodeId == 1) continue;

			for( list<ValueID>::iterator it2 = nodeInfo->m_values.begin(); it2 != nodeInfo->m_values.end(); ++it2 )
			{
				ValueID v = *it2;
				if( v.GetCommandClassId() == 0x20 )
				{
//					Manager::Get()->EnablePoll( v, 2 );		// enables polling with "intensity" of 2, though this is irrelevant with only one value polled
					break;
				}
			}
		}
		pthread_mutex_unlock( &g_criticalSection );

                pthread_t handle;
                if (pthread_create(&handle, NULL, &threadReadSocket, NULL) != 0) {
                    perror("couldn't create sock thread\n");
                    return(1);
                }

		// If we want to access our NodeInfo list, that has been built from all the
		// notification callbacks we received from the library, we have to do so
		// from inside a Critical Section.  This is because the callbacks occur on other 
		// threads, and we cannot risk the list being changed while we are using it.  
		// We must hold the critical section for as short a time as possible, to avoid
		// stalling the OpenZWave drivers.
		// At this point, the program just waits for 3 minutes (to demonstrate polling),
		// then exits
                while(true)
		{
			pthread_mutex_lock( &g_criticalSection );
			// but NodeInfo list and similar data should be inside critical section
			pthread_mutex_unlock( &g_criticalSection );
			sleep(1);
		}

		Driver::DriverData data;
		Manager::Get()->GetDriverStatistics( g_homeId, &data );
		printf("SOF: %d ACK Waiting: %d Read Aborts: %d Bad Checksums: %d\n", data.m_SOFCnt, data.m_ACKWaiting, data.m_readAborts, data.m_badChecksum);
		printf("Reads: %d Writes: %d CAN: %d NAK: %d ACK: %d Out of Frame: %d\n", data.m_readCnt, data.m_writeCnt, data.m_CANCnt, data.m_NAKCnt, data.m_ACKCnt, data.m_OOFCnt);
		printf("Dropped: %d Retries: %d\n", data.m_dropped, data.m_retries);
	}

	// program exit (clean up)
	if( strcasecmp( port.c_str(), "usb" ) == 0 )
	{
		Manager::Get()->RemoveDriver( "HID Controller" );
	}
	else
	{
		Manager::Get()->RemoveDriver( port );
	}
	Manager::Get()->RemoveWatcher( OnNotification, NULL );
	Manager::Destroy();
	Options::Destroy();
	pthread_mutex_destroy( &g_criticalSection );
	return 0;
}
