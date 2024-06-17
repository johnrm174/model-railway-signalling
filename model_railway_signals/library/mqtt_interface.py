#-----------------------------------------------------------------------------------------------
# These functions provides a basic MQTT Client interface for the Model Railway Signalling Package, 
# allowing multiple signalling applications (running on different computers) to share a single 
# Pi-Sprog DCC interface and to share layout state and events across a MQTT broker network.
#  
# For example, you could run one signalling application on a computer without a Pi-Sprog (e.g. 
# a Windows Laptop), configure that node to "publish" its DCC command feed to the network and 
# then configure another node (this time hosted on a Raspberry Pi) to "subscribe" to the same 
# DCC command feed and then forwarded to its local pi-Sprog DCC interface.
# 
# You can also use these features to split larger layouts into multiple signalling areas whilst 
# still being able to implement a level of automation between them. Functions are provided to 
# publishing and subscribing to the "state" of signals (for updating signals based on the one 
# ahead), the "state" of track occupancy sections (for "passing" trains between signalling 
# applications) and "signal passed" events (also for track occupancy). MQTT networking is also 
# at the heart of the Block Instruments feature - allowing the different "signalling areas" to
# communicate prototypically via signalbox bell codes and block section status.
# 
# To use these networking functions, you can either set up a local MQTT broker on one of the host 
# computers on your local network or alternatively use an 'open source' broker out there on the 
# internet - I've been using a test broker at "mqtt.eclipseprojects.io" (note this has no security 
# or authentication).
# 
# If you do intend using an internet-based broker then it is important to configure it with an 
# appropriate level of security. This package does support basic username/password authentication 
# for connecting in to the broker but note that these are NOT ENCRYPTED when sending over the 
# internet unless you are also using a SSL connection.
#-----------------------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
#
#   configure_mqtt_client - Configures the local MQTT client and layout network node
#     Mandatory Parameters:
#         network_identifier:str - The name to use for this signalling network (any string)
#         node_identifier:str - The name to use for this node on the network (can be any string)
#     Optional Parameters:
#         mqtt_enhanced_debugging:bool - 'True' to enable additional debug logging (default = False)
#         publish_shutdown:bool - Publish a shutdown message on appication exit (default = False)
#         act_on_shutdown:bool - Make a callback if a shutdown message is received (default = False)
#         shutdown_callback - Callback to make on reciept of a shutdown message (default = None)
#
#   mqtt_broker_connect - Opens a connection to a local or remote MQTT broker
#                    Returns whether the connection was successful or not (True/False)
#     Mandatory Parameters:
#         broker_host:str - The name/IP address of the MQTT broker host to be used
#     Optional Parameters:
#         broker_port:int - The network port for the broker host (default = 1883)
#         broker_username:str - the username to log into the MQTT Broker (default = None)
#         broker_password:str - the password to log into the MQTT Broker (default = None)
#
#   mqtt_broker_disconnect() - disconnect from the MQTT broker
#
# Classes and functions used by the other library modules:
#
#   split_remote_item_identifier(item_identifier:str) - validates and decodes a remote item identifier
#                       Returns [source_node:str, item_id:int] if valid or 'None' if invalid
#
#   subscribe_to_mqtt_messages - subscribe to a specific message type from a library object on a remote node.
#     Mandatory Parameters:
#         message_type:str - The 'signalling message type' to subscribe to 
#         item_node:str - The remote node (on the signalling network) for the Item
#         item_id:str - The Item ID to subscribe to (for the object on the remote node)
#         callback:int - The function to call (with the message) on reciept of messages
#     Optional Parameters:
#         subtopics:bool - Whether to subscribe to all subtopics (for DCC commands) - default False
#
#   unsubscribe_from_message_type (message_type:str) - unsubscribe from a message type (all items on all nodes)
#
#   send_mqtt_message - Sends a message out to the MQTT Broker (for consumption by other nodes)
#     Mandatory Parameters:
#         message_type:str - The 'signalling message type' to send 
#         item_id:int - The Item ID (to identify the sending item)
#         data:dict - The data to send (a dict of key/value pairs)
#     Optional Parameters:
#         log_message:str - The log message to output when the message is sent - default None
#         retain:bool - Whether the message should be 'retained' by the broker- default False
#         subtopic:str - The optional subtopic to send the message - default None
#
#   mqtt_shutdown() - Perform an orderly disconnection and shutdown (on application exit)
#
#-----------------------------------------------------------------------------------------------

import json
import logging
import time
import paho.mqtt.client
import threading
import socket

from . import common

#-----------------------------------------------------------------------------------------------
# Define an empty dictionary for holding the basic configuration information we need to track
#-----------------------------------------------------------------------------------------------

node_config: dict = {}
node_config["mqtt_client_debug"] = False                # Set to True to debug the PAHO MQTT client
node_config["heartbeat_frequency"] = 4.0                # Constant of 4 seconds
node_config["network_identifier"] = ""                  # Set by configure_mqtt_client (user defined)
node_config["node_identifier"] = ""                     # Set by configure_mqtt_client (user defined)
node_config["enhanced_debugging"] = False               # Set by configure_mqtt_client (user defined)
node_config["act_on_shutdown"] = False                  # Set by configure_mqtt_client (user defined)
node_config["publish_shutdown"] = False                 # Set by configure_mqtt_client (user defined)
node_config["shutdown_callback"] = None                 # Set by configure_mqtt_client (user defined)
node_config["local_ip_address"] = ""                    # Set by the 'on_connect' function
node_config["connected_to_broker"] = False              # Set by the 'on_connect' / 'on_disconnect functions
node_config["terminate_heartbeat_thread"] = False       # Used to coordinate disconnect between threads
node_config["heartbeat_thread_terminated"] = True       # Used to coordinate disconnect between threads
node_config["list_of_published_topics"] = []
node_config["list_of_subscribed_topics"] = []
node_config["callbacks"] = {}

#-----------------------------------------------------------------------------------------------
# The MQTT client is held globally:
#-----------------------------------------------------------------------------------------------

mqtt_client = None

#-----------------------------------------------------------------------------------------------
# Internal dict to hold details of the heartbeats received from other nodes
# The dict contains entries comprising {["node"]: time_stamp_of_last_heartbeat}
#-----------------------------------------------------------------------------------------------

heartbeats = {}

#-----------------------------------------------------------------------------------------------
# API function used by the editor to get the list of connected nodes and when they were last seen
#-----------------------------------------------------------------------------------------------

def get_node_status():
    return (heartbeats)

#-----------------------------------------------------------------------------------------------
# Common function used by the main thread to wait for responses in other threads. When the 
# specified function returns True within the timeout period, the function exits and returns
# True. If the end of the timeout period is reached beforehand then the function returns False 
#-----------------------------------------------------------------------------------------------

def wait_for_response(timeout:float, test_for_response_function):
    response_received = False
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
        response_received = test_for_response_function()
        if response_received: break
        time.sleep(0.001)
    return(response_received)

#-----------------------------------------------------------------------------------------------
# Find the local IP address (to include in the heartbeat messages):
# This will return the assigned IP address if we are connected to a network
#-----------------------------------------------------------------------------------------------

def find_local_ip_address():
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        test_socket.connect(('10.255.255.255', 1))
        ip_address = test_socket.getsockname()[0]
        logging.debug("MQTT-Client: Local IP address is "+ip_address)
    except:
        logging.error("MQTT-Client: Could not retrieve local IP address")
        ip_address = "<unknown>"
    finally:
        test_socket.close()
    return(ip_address)

#-----------------------------------------------------------------------------------------------
# Internal thread to send out heartbeat messages from the node when connected. The thread is
# started by the 'mqtt_broker_connect' function and terminated by the 'mqtt_broker_disconnect'
# function (by setting the 'terminate_heartbeat_thread' flag to True). The flag is then reset
# to False on the next 'mqtt_broker_connect' (prior to starting a new Thread)
#-----------------------------------------------------------------------------------------------

def publish_heartbeat_message():
    if node_config["connected_to_broker"]:
        # Topic format for the heartbeat message: "<Message-Type>/<Network-ID>"
        topic = "heartbeat"+"/"+node_config["network_identifier"]
        # Payload for the heartbeat message is a dictionary comprising the source node
        heartbeat_message = {"node":node_config["node_identifier"],"ip":node_config["local_ip_address"]}
        payload = json.dumps(heartbeat_message)
        try: mqtt_client.publish(topic,payload,retain=False,qos=1)
        except: pass
    return()

def thread_to_send_heartbeat_messages():
    global node_config
    if node_config["enhanced_debugging"]: logging.debug("MQTT-Client: Heartbeat thread started")
    node_config["heartbeat_thread_terminated"] = False
    while not node_config["terminate_heartbeat_thread"]:
        # The PAHO MQTT client may not be thread safe so publish the message from the main Tkinter thread
        common.execute_function_in_tkinter_thread(publish_heartbeat_message)
        # Wait before we send out the next heartbeat
        last_heartbeat_time = time.time()
        while (time.time() < last_heartbeat_time + node_config["heartbeat_frequency"]
                                 and not node_config["terminate_heartbeat_thread"]):
            time.sleep(0.001)
    if node_config["enhanced_debugging"]: logging.debug("MQTT-Client: Heartbeat Thread Terminated")
    node_config["heartbeat_thread_terminated"] = True
    return()

# ---------------------------------------------------------------------------------------------
# Common Function to create a external item identifier from the Item_ID and the remote Node.
# This identifier can then be used as the "key" to look up the Item in the associated dictionary
# ---------------------------------------------------------------------------------------------

def create_remote_item_identifier(item_id:int,node:str = None):
    return (node+"-"+str(item_id))

# ---------------------------------------------------------------------------------------------
# API and Common Function to extract the the item-ID (int) and Node-ID (str) from a compound
# identifierand return them to the calling programme - Will return None if the conversion
# fails - hence this function can also be used for validating remote item identifiers
# ---------------------------------------------------------------------------------------------

def split_remote_item_identifier(item_identifier:str):
    return_value = None
    if isinstance(item_identifier,str) and "-" in item_identifier:
        node_id = item_identifier.rpartition("-")[0]
        item_id = item_identifier.rpartition("-")[2]
        if node_id != "" and item_id.isdigit() and int(item_id) > 0 and int(item_id) < 100:
            return_value = [node_id,int(item_id)]                          
    return (return_value)

#-----------------------------------------------------------------------------------------------
# Internal call-back to process mqtt log messages (only called if enhanced_debugging is set)
#-----------------------------------------------------------------------------------------------

def on_log(mqtt_client, obj, level, mqtt_log_message):
    if node_config["mqtt_client_debug"]: logging.debug("MQTT-Client: "+mqtt_log_message)
    return()

#-----------------------------------------------------------------------------------------------
# Internal call-back to process broker disconnection events
#-----------------------------------------------------------------------------------------------

def on_disconnect(mqtt_client, userdata, rc):
    global node_config
    node_config["connected_to_broker"] = False
    if rc==0: logging.info("MQTT-Client - Broker connection successfully terminated")
    else: logging.warning("MQTT-Client: Unexpected disconnection from broker")
    node_config["connected_to_broker"] = False
    return()

#-----------------------------------------------------------------------------------------------
# Internal call-back to process broker connection / re-connection events
#-----------------------------------------------------------------------------------------------

def on_connect(mqtt_client, userdata, flags, rc):
    global node_config
    if rc == 0:
        logging.info("MQTT-Client - Successfully connected to MQTT Broker")
        # find the assigned IP address of the machine we are running on (for the heartbeat messages)
        node_config["local_ip_address"] = find_local_ip_address()
        # Pause just to ensure that MQTT is all fully up and running before we continue (and allow the client
        # to set up any subscriptions or publish any messages to the broker). We shouldn't need to do this but
        # I've experienced problems running on a Windows 10 platform if we don't include a short sleep
        time.sleep(0.1)
        # As we set up our broker connection with 'cleansession=true' a disconnection will have removed
        # all client connection information from the broker (including knowledge of the topics we have
        # subscribed to) - we therefore need to re-subscribe to all topics with this new connection
        # Note that this means we will immediately receive all retained messages for those topics
        if len(node_config["list_of_subscribed_topics"]) > 0:
            for topic in node_config["list_of_subscribed_topics"]:
                if node_config["enhanced_debugging"]: logging.debug("MQTT-Client: Subscribing to '"+topic+"' from Broker")
                mqtt_client.subscribe(topic)
        # Re subscribe to all heartbeat and shutdown messages on the specified network
        # Topic format for these messages is: "<Message-Type>/<Network-ID>"
        heartbeat_topic = "heartbeat"+"/"+node_config["network_identifier"]
        if node_config["enhanced_debugging"]: logging.debug("MQTT-Client: Subscribing to: '"+heartbeat_topic+"' from Broker")
        mqtt_client.subscribe(heartbeat_topic)
        shutdown_topic = "shutdown"+"/"+node_config["network_identifier"]
        if node_config["enhanced_debugging"]: logging.debug("MQTT-Client: Subscribing to: '"+shutdown_topic+"' from Broker")
        mqtt_client.subscribe(shutdown_topic)
        # Set the flag to report a successful connection
        node_config["connected_to_broker"] = True
    elif rc == 1: logging.error("MQTT-Client: Connection refused – incorrect protocol version")
    elif rc == 2: logging.error("MQTT-Client: Connection refused – invalid client identifier")
    elif rc == 3: logging.error("MQTT-Client: Connection refused – server unavailable")
    elif rc == 4: logging.error("MQTT-Client: Connection refused – bad username or password")
    elif rc == 5: logging.error("MQTT-Client: Connection refused – not authorised")
    return()

#--------------------------------------------------------------------------------------------------------
# Internal function to process messages received from the MQTT Broker - unpacking the message and then
# making the registered callback to pass the message back to the main application. Note that this function
# is executed in the main tkinter thread (as long as we know the main root window) to make it threadsafe
# If we don't know the main root window then the function is executed in the current mqtt event thread.
#--------------------------------------------------------------------------------------------------------

def process_message(msg):
    global heartbeats
    # Unpack the json message so we can extract the contents (with exception handling)
    try:
        unpacked_json = json.loads(msg.payload)
    except Exception as exception:
        logging.error("MQTT-Client: Exception unpacking json - "+str(exception))
    else:
        # If it is a heartbeat message then we just update the list of connected nodes
        if msg.topic.startswith("heartbeat"):
            heartbeats[unpacked_json["node"]] = [unpacked_json["ip"], int(time.time())]
        # If it is a shutdown message we only act on it if configured to do so
        elif msg.topic.startswith("shutdown"):
            if node_config["act_on_shutdown"] and node_config["shutdown_callback"] is not None:
                logging.info("MQTT-Client - Shutdown message received - Triggering application shutdown")
                node_config["shutdown_callback"]()
            elif node_config["enhanced_debugging"]:
                logging.debug("MQTT-Client: Ignoring Shutdown message (not configured to shutdown)")
        # Make the callback (that was registered when the calling programme subscribed to the feed)
        # Note that we also need to test to see if the the topic is a partial match to cover the
        # case of subscribing to all subtopics for an specified item (with the '+' wildcard)
        elif msg.topic in node_config["callbacks"]:
            node_config["callbacks"][msg.topic] (unpacked_json)
        elif msg.topic.rpartition('/')[0]+"/+" in node_config["callbacks"]:
            node_config["callbacks"][msg.topic.rpartition('/')[0]+"/+"] (unpacked_json)
        else:
            logging.warning("MQTT-Client: unhandled message topic: "+str(msg.topic))
    return()

#--------------------------------------------------------------------------------------------------------
# Internal function to handle messages received from the MQTT Broker. Note that we "pass" the
# execution for processing the function back into the main Tkinter thread (assuming we know the
# root window (if not, then as a fallback we raise a callback in the current mqtt event thread)
#--------------------------------------------------------------------------------------------------------

def on_message(mqtt_client,obj,msg):
    global node_config
    # Only process the message if there is a payload - If there is no payload then the message is
    # a "null message" - sent to purge retained messages from the broker on application exit
    if msg.payload: common.execute_function_in_tkinter_thread (lambda:process_message(msg)) 
    return()

#-----------------------------------------------------------------------------------------------
# API Function to configure the MQTT client for this particular network and node
#-----------------------------------------------------------------------------------------------

def configure_mqtt_client (network_identifier:str,
                           node_identifier:str,
                           enhanced_debugging:bool = False,
                           publish_shutdown:bool = False,
                           act_on_shutdown:bool = False,
                           shutdown_callback=None):
    global node_config
    # Validate the parameters we have been given
    if not isinstance(network_identifier, str):
        logging.error("MQTT-Client: configure_mqtt_client - Network Identifier must be specified as a string")
    elif not isinstance(node_identifier, str):
        logging.error("MQTT-Client: configure_mqtt_client - Node Identifier must be specified as a string")
    elif not isinstance(enhanced_debugging, bool):
        logging.error("MQTT-Client: configure_mqtt_client - Enhanced debugging flag must be specified as a boolean")
    elif not isinstance(publish_shutdown, bool):
        logging.error("MQTT-Client: configure_mqtt_client - Publish shutdown flag must be specified as a boolean")
    elif not isinstance(act_on_shutdown, bool):
        logging.error("MQTT-Client: configure_mqtt_client - Act on shutdown flag must be specified as a boolean")
    else:
        logging.debug("MQTT-Client: Configuring Network - Name: '"+network_identifier+"' Node: '"+node_identifier+"'")
        # Configure this module (to enable subscriptions to be configured even if not connected)
        node_config["enhanced_debugging"] = enhanced_debugging
        node_config["network_identifier"] = network_identifier
        node_config["node_identifier"] = node_identifier
        node_config["publish_shutdown"] = publish_shutdown
        node_config["act_on_shutdown"] = act_on_shutdown
        node_config["shutdown_callback"] = shutdown_callback
    return()

#-----------------------------------------------------------------------------------------------
# API Function to connect and/or re-connect to an external MQTT broker instance
# Returns True if connection was successful (otherwise False)
#
# A few notes about disconnecting and then re-connecting from the broker:
#
# The main application allows the user to disconnect/reconnect at will (a likely use case when
# configuring the application for networking for the first time). From reading the PAHO MQTT
# documentation, disconnect() should perform a clean disconnect from the broker, and my
# assumption was therefore that you should be able to disconnect and all connect() with
# updated settings to establish a new connection (note I couldn't use reconnect() as I
# wanted to allow the broker host/port settings to be updated).
#
# However, I found that after a few disconnect/reconnect cycles (in relatively quick succession)
# the connect() function just timed out (and would time out each subsequent time it was called).
#
# My workaround was to completely kill off the currrent mqtt client (stop the loop) following
# a successful disconnect and then create a new class instance for the new session - hoping the
# old instance will get garbage collected in due course.
#
# I don't like this soultion, but it works. I've seen an occasional disconnect timeout, but in
# this case the old session remains active and a reconnection (with the new settings) isn't
# attempted. the next time disconnect/reconnect is initialted it all works.
#
# The second intermittent issue I had was either the disconnect() or loop_stop() calls hanging
# if I didn't clear out the message queues prior to disconnect - although as this code includes
# a sleep, it could be some sort of timing issue - I've never been able to reliably reproduce
# so can't be sure - all I know is the code as-is seems to hang together relaibly
#-----------------------------------------------------------------------------------------------

def mqtt_broker_connect (broker_host:str,
                         broker_port:int = 1883,
                         broker_username:str = None,
                         broker_password:str = None):
    global mqtt_client
    def connect_acknowledgement(): return(node_config["connected_to_broker"])
    # Validate the parameters we have been given
    if not isinstance(broker_host, str):
        logging.error("MQTT-Client: configure_mqtt_client - Broker Host must be specified as a string")
    elif not isinstance(broker_port, int):
        logging.error("MQTT-Client: configure_mqtt_client - Broker Port must be specified as an integer")
    elif broker_username is not None and not isinstance(broker_username, str):
        logging.error("MQTT-Client: configure_mqtt_client - Broker Username must be specified as None or a string")
    elif broker_password is not None and not isinstance(broker_password, str):
        logging.error("MQTT-Client: configure_mqtt_client - Broker Password must be specified as None or a string")
    else:
        # Handle the case where we are already connected to the broker
        if node_config["connected_to_broker"]: mqtt_broker_disconnect()
        # Do some basic exception handling around opening the broker connection
        logging.debug("MQTT-Client: Connecting to Broker at "+broker_host+":"+str(broker_port))
        # Create a new mqtt broker instance
        if mqtt_client is None: mqtt_client = paho.mqtt.client.Client(clean_session=True)
        mqtt_client.on_message = on_message    
        mqtt_client.on_connect = on_connect    
        mqtt_client.on_disconnect = on_disconnect    
        mqtt_client.reconnect_delay_set(min_delay=1, max_delay=10)
        mqtt_client.on_log = on_log
        # Configure the basic username/password authentication (if required)
        if broker_username is not None:
            mqtt_client.username_pw_set(username=broker_username,password=broker_password)
        try:
            # All the info out there suggests you should connect to the broker before starting the loop
            # but I've found that, for the 'file load' use case, the client doesn't connect until the code
            # (associated with the file load) finishes processing and returns into the tkinter main loop.
            mqtt_client.loop_start()
            time.sleep(0.1)
            mqtt_client.connect_async(broker_host,port=broker_port,keepalive = 10)
        except Exception as exception:
            logging.error("MQTT-Client: Error connecting to broker: "+str(exception))
        else:
            # Wait for connection acknowledgement (from on-connect callback function)
            if wait_for_response(5.0, connect_acknowledgement):
                if node_config["heartbeat_thread_terminated"]:
                    # Reset the broker disconnect initiated flag
                    node_config["terminate_heartbeat_thread"] = False
                    # Start the heartbeat thread
                    heartbeat_thread = threading.Thread (target=thread_to_send_heartbeat_messages)
                    heartbeat_thread.setDaemon(True)
                    heartbeat_thread.start()
            else:
                logging.error("MQTT-Client: Timeout connecting to broker")
    return(node_config["connected_to_broker"])

#-----------------------------------------------------------------------------------------------
# API Function to disconnect from an external MQTT broker instance
# Returns True if disconnection was successful (otherwise False)
#-----------------------------------------------------------------------------------------------

def mqtt_broker_disconnect():
    global node_config
    global mqtt_client
    def disconnect_acknowledgement(): return (not node_config["connected_to_broker"])
    def heartbeat_thread_terminated(): return (node_config["heartbeat_thread_terminated"])
    if node_config["connected_to_broker"]:
        # Set the flag to tell the heartbeat thread to terminate
        node_config["terminate_heartbeat_thread"] = True
        logging.debug("MQTT-Client: Initiating broker disconnect")
        # Wait until we get confirmation the Heartbeat thread has terminated
        if not wait_for_response(0.5, heartbeat_thread_terminated):
            logging.error("MQTT-Client: Heartbeat thread failed to terminate")        
        # Clean out the message queues on the broker by publishing null messages (empty strings)
        # to each of the topics that we have sent messages to during the lifetime of the session
        if len(node_config["list_of_published_topics"])>0:
            logging.debug("MQTT-Client: Purging retained messages")
        for topic in node_config["list_of_published_topics"]:
            if node_config["enhanced_debugging"]: logging.debug("MQTT-Client: Publishing: "+str(topic)+"-NULL")
            mqtt_client.publish(topic,payload=None,retain=False,qos=1)
        # Wait for everything to be published to the broker (with a sleep) and disconnect
        # I'd rather use a PAHO MQTT check and timeout but there doesn't seem to be one
        time.sleep(0.25)
        logging.debug("MQTT-Client: Disconnecting from broker")
        mqtt_client.disconnect()
        # Wait for disconnection acknowledgement (from on-disconnect callback function)
        if wait_for_response(1.0, disconnect_acknowledgement):
            mqtt_client.loop_stop()
            mqtt_client = None
        else:
            logging.error("MQTT-Client: Timeout disconnecting from broker")
    return(not node_config["connected_to_broker"])

#-----------------------------------------------------------------------------------------------
# Externally called function to perform a graceful shutdown of MQTT networking on Application
# Exit in terms of clearing out the publish topic queues (by sending null messages). If configured
# The function also sends out a 'shutdown' message to other network nodes for them to act on.
#-----------------------------------------------------------------------------------------------

def mqtt_shutdown():
    global node_config
    if node_config["connected_to_broker"]:
        # Publish a shutdown command to other nodes if configured  to do so
        if node_config["publish_shutdown"]:
            # Topic format for the shutdown message: "<Message-Type>/<Network-ID>"
            topic = "shutdown"+"/"+node_config["network_identifier"]
            # Payload for the shutdown message is a dictionary comprising the source node
            shutdown_message = {"node":node_config["node_identifier"]}
            payload = json.dumps(shutdown_message)
            if node_config["enhanced_debugging"]: logging.debug("MQTT-Client: Publishing: "+str(topic)+str(payload))
            mqtt_client.publish(topic,payload,retain=False,qos=1)
            time.sleep(0.1)
        mqtt_broker_disconnect()
    return()

#-----------------------------------------------------------------------------------------------
# Externally Called Function to subscribe to topics published by the MQTT broker. This function
# takes in a string that defines the application-specific message type and converts this into
# a fully qualified MQTT topic (using the Node and item ID). The registered callback will return
# the content of the received messages. The optional subtopic flag enables you to subscribe
# to all sub-topics from a particular item. This is used in the Model Railway Signalling Package
# for subscribing to all DCC address messages (where each DCC address is a seperate subtopic)
#-----------------------------------------------------------------------------------------------

def subscribe_to_mqtt_messages (message_type:str,item_node:str,item_id:int,callback,subtopics:bool=False):
    global node_config
    global mqtt_client
    # The Identifier for a remote object is a string combining the the Node-ID and Object-ID
    item_identifier = create_remote_item_identifier(item_id,item_node)
    # Topic format: "<Message-Type>/<Network-ID>/<Item_Identifier>/<optional-subtopic>"
    topic = message_type+"/"+node_config["network_identifier"]+"/"+item_identifier
    if subtopics: topic = topic+"/+"
    # Only subscribe if connected to the broker(if the client is disconnected
    # from the broker then all subscriptions will already have been terminated)
    if node_config["connected_to_broker"]:
        if node_config["enhanced_debugging"]: logging.debug("MQTT-Client: Subscribing to '"+topic+"' from Broker")
        mqtt_client.subscribe(topic)
    elif node_config["enhanced_debugging"]: logging.debug("MQTT-Client: Adding subscription topic '"+topic+"'")
    # Add to the list of subscribed topics (so we can re-subscribe on reconnection)
    node_config["list_of_subscribed_topics"].append(topic)
    # Save the callback details for when we receive a message on the topic
    node_config["callbacks"][topic] = callback
    return()

#-----------------------------------------------------------------------------------------------
# Externally Called Function to Publish a message to the MQTT broker. This function takes
# in a string that defines the application-specific message type and converts this into
# a fully qualified MQTT topic. Data items are passed in as a list and converted to json
# An optional 'info' log message can also be passed in (logged just prior to publishing)
#-----------------------------------------------------------------------------------------------

def send_mqtt_message (message_type:str,item_id:int,data:dict,log_message:str=None,retain:bool=False,subtopic=None):
    # Only publish the broker if we are connected
    if node_config["connected_to_broker"]:
        item_identifier = create_remote_item_identifier(item_id,node_config["node_identifier"])
        # Topic format: "<Message-Type>/<Network-ID>/<Item_Identifier>/<optional-subtopic>"
        topic = message_type+"/"+node_config["network_identifier"]+"/"+item_identifier
        if subtopic is not None: topic = topic+"/"+subtopic
        data["sourceidentifier"] = item_identifier
        payload = json.dumps(data)
        if log_message is not None: logging.debug(log_message)
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Publishing: "+str(topic)+str(payload))
        # Publish the message to the broker
        mqtt_client.publish(topic,payload,retain=retain,qos=1)
        # Add to the list of published topics so we can 'Clean up'
        # the MQTT broker by publishing empty messages on shutdown
        if topic not in node_config["list_of_published_topics"]:
            node_config["list_of_published_topics"].append(topic)
    return()

#-----------------------------------------------------------------------------------------------
# Externally called Function to unsubscribe to a particular message type from the broker. Called by
# the higher-level 'reset_mqtt_configuration' functions for instruments, signals and sections to
# clear out the relevant subscrptions in support of the editor - where a configuration change
# to MQTT networking will trigger a reset of all subscriptions followed by a re-configuration
#-----------------------------------------------------------------------------------------------

def unsubscribe_from_message_type(message_type:str):
    global node_config
    # Topic format: "<Message-Type>/<Network-ID>/<Item_Identifier>/<optional-subtopic>"
    # Finally, remove all instances of the message type from the internal subscriptions list
    # Note we don't iterate through the list to remove items as it will change under us
    new_list_of_subscribed_topics = []
    for subscribed_topic in node_config["list_of_subscribed_topics"]:
        if subscribed_topic.startswith(message_type):
            if node_config["enhanced_debugging"]:
                logging.debug("MQTT-Client: Unsubscribing from topic '"+subscribed_topic+"'")
            # Only unsubscribe if connected to the broker(if the client is disconnected
            # from the broker then all subscriptions will already have been terminated)
            if node_config["connected_to_broker"]: mqtt_client.unsubscribe(subscribed_topic)
        else:
            new_list_of_subscribed_topics.append(subscribed_topic)
        node_config["list_of_subscribed_topics"] = new_list_of_subscribed_topics
    return()

##################################################################################################################
