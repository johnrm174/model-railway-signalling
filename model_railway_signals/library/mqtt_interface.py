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
# configure_networking - Configures the local client and opens a connection to the MQTT broker
#                    Returns whether the connection was successful (or timed out)
#                    NOTE THAT THE 'CONFIGURE_NETWORKING' FUNCTION IS NOW DEPRECATED
#                    Use the 'configure_mqtt_client' and 'mqtt_broker_connect' functions instead
#   Mandatory Parameters:
#       broker_host:str - The name/IP address of the MQTT broker host to be used
#       network_identifier:str - The name to use for this signalling network (any string)
#       node_identifier:str - The name to use for this node on the network (can be any string)
#   Optional Parameters:
#       broker_port:int - The network port for the broker host (default = 1883)
#       broker_username:str - the username to log into the MQTT Broker (default = None)
#       broker_password:str - the password to log into the MQTT Broker (default = None)
#       mqtt_enhanced_debugging:bool - 'True' to enable additional debug logging (default = False)
#
# configure_mqtt_client - Configures the local MQTT client and layout network node
#   Mandatory Parameters:
#       network_identifier:str - The name to use for this signalling network (any string)
#       node_identifier:str - The name to use for this node on the network (can be any string)
#   Optional Parameters:
#       mqtt_enhanced_debugging:bool - 'True' to enable additional debug logging (default = False)
#
# mqtt_broker_connect - Opens a connection to a local or remote MQTT broker
#                    Returns whether the connection was successful or not (True/False)
#   Mandatory Parameters:
#       broker_host:str - The name/IP address of the MQTT broker host to be used
#   Optional Parameters:
#       broker_port:int - The network port for the broker host (default = 1883)
#       broker_username:str - the username to log into the MQTT Broker (default = None)
#       broker_password:str - the password to log into the MQTT Broker (default = None)
#
#-----------------------------------------------------------------------------------------------

from . import common
import json
import logging
import time
import paho.mqtt.client

#-----------------------------------------------------------------------------------------------
# Define an empty dictionary for holding the basic configuration information we need to track
#-----------------------------------------------------------------------------------------------

node_config: dict = {}
node_config["network_identifier"] = ""
node_config["node_identifier"] = ""   
node_config["enhanced_debugging"] = False
node_config["network_configured"] = False
node_config["connected_to_broker"] = False
node_config["list_of_published_topics"] = []
node_config["list_of_subscribed_topics"] = []
node_config["callbacks"] = {}

#-----------------------------------------------------------------------------------------------
# The MQTT client is held globally:
#-----------------------------------------------------------------------------------------------

mqtt_client = None

# ---------------------------------------------------------------------------------------------
# Common Function to create a external item identifier from the Item_ID and the remote Node.
# This identifier can then be used as the "key" to look up the Item in the associated dictionary
# ---------------------------------------------------------------------------------------------

def create_remote_item_identifier(item_id:int,node:str = None):
    return (node+"-"+str(item_id))

# ---------------------------------------------------------------------------------------------
# Common Function to extract the the item-ID (int) and Node-ID (str) from a compound identifier
# and return them to the calling programme - Will return None if the conversion fails - hence
# this function can also be used for validating remote item identifiers
# ---------------------------------------------------------------------------------------------

def split_remote_item_identifier(item_identifier:str):
    return_value = None
    if isinstance(item_identifier,str):
        node_id = item_identifier.rpartition("-")[0]
        item_id = item_identifier.rpartition("-")[2]
        if node_id != "" and item_id.isdigit() and int(item_id) > 0 and int(item_id) < 99:
            return_value = [node_id,int(item_id)]                          
    return (return_value)

#-----------------------------------------------------------------------------------------------
# Internal call-back to process mqtt log messages (only called if enhanced_debugging is set)
#-----------------------------------------------------------------------------------------------

def on_log(mqtt_client, obj, level, mqtt_log_message):
    if node_config["enhanced_debugging"]: logging.debug("MQTT-Client: "+mqtt_log_message)
    return()

#-----------------------------------------------------------------------------------------------
# Internal call-back to process broker disconnection events
#-----------------------------------------------------------------------------------------------

def on_disconnect(mqtt_client, userdata, rc):
    global node_config
    if rc==0: logging.info("MQTT-Client: Broker connection successfully terminated")
    else: logging.warning("MQTT-Client: Unexpected disconnection from broker")
    node_config["connected_to_broker"] = False
    return()

#-----------------------------------------------------------------------------------------------
# Internal call-back to process broker connection / re-connection events
#-----------------------------------------------------------------------------------------------

def on_connect(mqtt_client, userdata, flags, rc):
    global node_config
    if rc == 0:
        logging.info("MQTT-Client: Successfully connected to MQTT Broker")
        # As we set up our broker connection with 'cleansession=true' a disconnection will have removed
        # all client connection information from the broker (including knowledge of the topics we have
        # subscribed to) - we therefore need to re-subscribe to all topics with this new connection
        # Note that this means we will immediately receive all retained messages for those topics
        if len(node_config["list_of_subscribed_topics"]) > 0:
            logging.debug("MQTT-Client: Re-subscribing to all MQTT broker topics")
            for topic in node_config["list_of_subscribed_topics"]:
                mqtt_client.subscribe(topic)
        # Pause just to ensure that MQTT is all fully up and running before we continue (and allow the client
        # to set up any subscriptions or publish any messages to the broker). We shouldn't need to do this but
        # I've experienced problems running on a Windows 10 platform if we don't include a short sleep
        time.sleep(0.1)
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
    # Unpack the json message so we can extract the contents (with exception handling)
    try:
        unpacked_json = json.loads(msg.payload)
    except Exception as exception:
        logging.error("MQTT-Client: Exception unpacking json - "+str(exception))
    else:
        # Make the callback (that was registered when the calling programme subscribed to the feed)
        # Note that we also need to test to see if the the topic is a partial match to cover the
        # case of subscribing to all subtopics for an specified item (with the '+' wildcard)
        if msg.topic in node_config["callbacks"]:
            logging.debug("MQTT-Client: Received: "+str(msg.topic)+"-"+str(unpacked_json))
            node_config["callbacks"][msg.topic] (unpacked_json)
        elif msg.topic.rpartition('/')[0]+"/+" in node_config["callbacks"]:
            logging.debug("MQTT-Client: Received: "+str(msg.topic)+"-"+str(unpacked_json))
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
    if msg.payload:
        if common.root_window is not None:
            common.execute_function_in_tkinter_thread (lambda:process_message(msg)) 
        else:
            process_message(msg)
    return()

#################################################################################################
# DEPRECATED Public API Function to configure the networking for this particular network "Node"
# Applications should use the configure_mqtt_client and mqtt_broker_connect functions instead
#################################################################################################

def configure_networking (broker_host:str,
                          network_identifier:str,
                          node_identifier:str,
                          broker_port:int = 1883,
                          broker_username:str = None,
                          broker_password:str = None,
                          mqtt_enhanced_debugging:bool = False):
    global node_config
    global mqtt_client
    logging.warning ("###########################################################################################")
    logging.warning ("MQTT Interface - The 'configure_networking' function is DEPRECATED - Use the seperate")
    logging.warning ("MQTT Interface - configure_mqtt_client and mqtt_broker_connect functions instead")
    logging.warning ("###########################################################################################")
    # Configure this module (to enable subscriptions to be configured even if not connected
    node_config["enhanced_debugging"] = mqtt_enhanced_debugging
    node_config["network_identifier"] = network_identifier
    node_config["node_identifier"] = node_identifier
    # Create a new instance of the MQTT client and configure / connect
    logging.info("MQTT-Client: Connecting to Broker \'"+broker_host+"\'")
    mqtt_client = paho.mqtt.client.Client(clean_session=True)
    mqtt_client.on_message = on_message    
    mqtt_client.on_connect = on_connect    
    mqtt_client.on_disconnect = on_disconnect    
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=10)
    if mqtt_enhanced_debugging: mqtt_client.on_log = on_log
    if broker_username is not None: mqtt_client.username_pw_set(username=broker_username,password=broker_password)
    node_config["network_configured"] = True
    # Do some basic exception handling around opening the broker connection
    try:
        mqtt_client.connect_async(broker_host,port=broker_port,keepalive = 10)
        mqtt_client.loop_start()
    except Exception as exception:
        logging.error("MQTT-Client: Error connecting to broker: "+str(exception)+" - No messages will be published/received")
    else:
        # Wait for connection acknowledgement (from on-connect callback function)
        timeout_start = time.time()
        while time.time() < timeout_start + 5:
            if node_config["connected_to_broker"]:
                break
        if not node_config["connected_to_broker"]:
            logging.warning("MQTT-Client: Timeout connecting to broker - No messages will be published/received")
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to configure the MQTT client for this particular network and node
#-----------------------------------------------------------------------------------------------

def configure_mqtt_client (network_identifier:str,
                           node_identifier:str,
                           enhanced_debugging:bool = False):
    global node_config, mqtt_client
    logging.debug("MQTT-Client: Configuring MQTT Client for "+network_identifier+":"+node_identifier)
    # Configure this module (to enable subscriptions to be configured even if not connected)
    node_config["enhanced_debugging"] = enhanced_debugging
    node_config["network_identifier"] = network_identifier
    node_config["node_identifier"] = node_identifier
    node_config["network_configured"] = True
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to connect and/or re-connect to an external MQTT broker instance
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
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Network not configured - Cannot connect to broker)")
    else:
        # Handle the case where we are already connected to the broker
        if node_config["connected_to_broker"]: mqtt_broker_disconnect()
        # Do some basic exception handling around opening the broker connection
        logging.debug("MQTT-Client: Connecting to Broker "+broker_host+":"+str(broker_port))
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
            mqtt_client.connect_async(broker_host,port=broker_port,keepalive = 10)
            mqtt_client.loop_start()
        except Exception as exception:
            logging.error("MQTT-Client: Error connecting to broker: "+str(exception))
        else:
            # Wait for connection acknowledgement (from on-connect callback function)
            timeout_start = time.time()
            while time.time() < timeout_start + 2:
                if node_config["connected_to_broker"]: break
                time.sleep(0.001)
            if not node_config["connected_to_broker"]:
                logging.error("MQTT-Client: Timeout connecting to broker")
    return(node_config["connected_to_broker"])

#-----------------------------------------------------------------------------------------------
# Public API Function to disconnect from an external MQTT broker instance
#-----------------------------------------------------------------------------------------------

def mqtt_broker_disconnect():
    global node_config
    global mqtt_client
    if node_config["connected_to_broker"]:
        logging.debug("MQTT-Client: Clearing message queues before disconnect")
        # Clean out the message queues on the broker by publishing null messages (empty strings)
        # to each of the topics that we have sent messages to during the lifetime of the session
        for topic in node_config["list_of_published_topics"]:
            logging.debug("MQTT-Client: Publishing: "+str(topic)+"-NULL")
            mqtt_client.publish(topic,payload=None,retain=True,qos=1)
        # Wait for everything to be published to the broker (with a sleep) and disconnect
        time.sleep(0.25)
        logging.debug("MQTT-Client: Disconnecting from broker")
        mqtt_client.disconnect()
        # Wait for disconnection acknowledgement (from on-disconnect callback function)
        timeout_start = time.time()
        while time.time() < timeout_start + 2:
            if not node_config["connected_to_broker"]: break
            time.sleep(0.001)
        if node_config["connected_to_broker"]:
            logging.error("MQTT-Client: Timeout disconnecting from broker")
        else:
            mqtt_client.loop_stop()
            mqtt_client = None
    return(node_config["connected_to_broker"])

#-----------------------------------------------------------------------------------------------
# Externally called function to perform a gracefull shutdown of the MQTT networking
# in terms of clearing out the publish topic queues (by sending null messages)
#-----------------------------------------------------------------------------------------------

def mqtt_shutdown():
    global node_config
    if node_config["connected_to_broker"]:
        mqtt_broker_disconnect()
        node_config["network_configured"] = False
        node_config["connected_to_broker"] = False
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
    logging.debug("MQTT-Client: Subscribing to topic '"+topic+"'")
    # Only subscribe if connected to the broker(if the client is disconnected
    # from the broker then all subscriptions will already have been terminated)
    if node_config["connected_to_broker"]: mqtt_client.subscribe(topic)
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
            logging.debug("MQTT-Client: Publishing: "+str(topic)+"-"+str(payload))
        # Publish the message to the broker
        mqtt_client.publish(topic,payload,retain=retain,qos=1)
        # Add to the list of published topics so we can 'Clean up'
        # the MQTT broker by publishing empty messages on shutdown
        if topic not in node_config["list_of_published_topics"]:
            node_config["list_of_published_topics"].append(topic)
    return()

#-----------------------------------------------------------------------------------------------
# Non public  Function to unsubscribe to a particular message type from the broker. Called by
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
