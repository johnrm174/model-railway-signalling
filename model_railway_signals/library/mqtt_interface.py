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
node_config["network_identifier"] = None
node_config["node_identifier"] = None   
node_config["enhanced_debugging"] = False
node_config["network_configured"] = False
node_config["connected_to_broker"] = False
node_config["list_of_published_topics"] = []
node_config["list_of_subscribed_topics"] = []
node_config["callbacks"] = {}

# ---------------------------------------------------------------------------------------------
# Common Function to create a external item identifier from the Item_ID and the remote Node.
# This identifier can then be used as the "key" to look up the Item in the associated dictionary
# ---------------------------------------------------------------------------------------------

def create_remote_item_identifier(item_id:int,node:str = None):
    return (node+"-"+str(item_id))

# ---------------------------------------------------------------------------------------------
# Common Function to extract the the item-ID (int) and Node-ID (str) from a compound identifier
# and return them to the calling programme - Will return None if the conversion fails
# ---------------------------------------------------------------------------------------------

def split_remote_item_identifier(item_identifier:str):
    try:
        node_id = item_identifier.rpartition("-")[0]
        item_id = int(item_identifier.rpartition("-")[2])
        return_value = [node_id,item_id]
    except:
        return_value = None
    return (return_value) 

#-----------------------------------------------------------------------------------------------
# Internal call-back to process mqtt log messages (only called if enhanced_debugging is set)
#-----------------------------------------------------------------------------------------------

def on_log(mqtt_client, obj, level, mqtt_log_message):
    global logging
    logging.debug("MQTT-Client: "+mqtt_log_message)
    return()

#-----------------------------------------------------------------------------------------------
# Internal call-back to process broker disconnection events
#-----------------------------------------------------------------------------------------------

def on_disconnect(mqtt_client, userdata, rc):
    global logging
    global node_config
    if rc==0: logging.info("MQTT-Client: Broker connection terminated")
    else: logging.warning("MQTT-Client: Unexpected disconnection from broker")
    node_config["connected_to_broker"] = False
    return()

#-----------------------------------------------------------------------------------------------
# Internal call-back to process broker connection / re-connection events
#-----------------------------------------------------------------------------------------------

def on_connect(mqtt_client, userdata, flags, rc):
    global logging
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
    global logging
    # Unpack the json message so we can extract the contents (with exception handling)
    try:
        unpacked_json = json.loads(msg.payload)
    except Exception as exception:
        logging.error("MQTT-Client: Exception unpacking json - "+str(exception))
    else:
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Successfully parsed message:"+str(unpacked_json))
        # Make the callback (that was registered when the calling programme subscribed to the feed)
        # Note that we also need to test to see if the the topic is a partial match to cover the
        # case of subscribing to all subtopics for an specified item (with the '+' wildcard)
        if msg.topic in node_config["callbacks"]:
            node_config["callbacks"][msg.topic] (unpacked_json)
        elif msg.topic.rpartition('/')[0]+"/+" in node_config["callbacks"]:
            node_config["callbacks"][msg.topic.rpartition('/')[0]+"/+"] (unpacked_json)
        else:
             logging.warning("MQTT-Client: unhandled message topic:"+str(msg.topic))
    return()

#--------------------------------------------------------------------------------------------------------
# Internal function to handle messages received from the MQTT Broker. Note that we "pass" the
# execution for processing the function back into the main Tkinter thread (assuming we know the
# root window (if not, then as a fallback we raise a callback in the current mqtt event thread)
#--------------------------------------------------------------------------------------------------------

def on_message(mqtt_client,obj,msg):
    global logging
    global node_config
    # Only process the message if there is a payload - If there is no payload then the message is
    # a "null message" - sent to purge retained messages from the broker on application exit
    if msg.payload:
        if common.root_window is not None:
            common.execute_function_in_tkinter_thread (lambda:process_message(msg)) 
        else:
            process_message(msg)
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to configure the networking for this particular network "Node"
#-----------------------------------------------------------------------------------------------

def configure_networking (broker_host:str,
                          network_identifier:str,
                          node_identifier:str,
                          broker_port:int = 1883,
                          broker_username:str = None,
                          broker_password:str = None,
                          mqtt_enhanced_debugging:bool = False):
    global logging
    global node_config
    global mqtt_client
    logging.info("MQTT-Client: Connecting to Broker \'"+broker_host+"\'")
    mqtt_client = paho.mqtt.client.Client(clean_session=True)
    mqtt_client.on_message = on_message    
    mqtt_client.on_connect = on_connect    
    mqtt_client.on_disconnect = on_disconnect    
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=10)
    if mqtt_enhanced_debugging: mqtt_client.on_log = on_log
    if broker_username is not None: mqtt_client.username_pw_set(username=broker_username,password=broker_password)
    # Do some basic exception handling around opening the broker connection
    try:
        mqtt_client.connect(broker_host,port=broker_port,keepalive = 10)
        mqtt_client.loop_start()
    except Exception as exception:
        logging.error("MQTT-Client: Error connecting to broker: "+str(exception)+" - No messages will be published/received")
    else:
        node_config["enhanced_debugging"] = mqtt_enhanced_debugging
        node_config["network_identifier"] = network_identifier
        node_config["node_identifier"] = node_identifier
        # Wait for connection acknowledgement (from on-connect callback function)
        timeout_start = time.time()
        while time.time() < timeout_start + 5:
            if node_config["connected_to_broker"]:
                node_config["network_configured"] = True
                break
        if not node_config["connected_to_broker"]:
            logging.warning("MQTT-Client: Timeout connecting to broker - No messages will be published/received")
            
    return()

#-----------------------------------------------------------------------------------------------
# Externally called function to perform a gracefull shutdown of the MQTT networking
# in terms of clearing out the publish topic queues (by sending null messages)
#-----------------------------------------------------------------------------------------------

def mqtt_shutdown():
    global logging
    # Only shut down the mqtt networking if we configured it in the first place
    if node_config["network_configured"]:
        logging.info("MQTT-Client: Clearing message queues and shutting down")
        # Clean out the message queues on the broker by publishing null messages (empty strings)
        # to each of the topics that we have sent messages to during the lifetime of the session
        for topic in node_config["list_of_published_topics"]:
            publish_message(topic,payload=None,retain=True)
        # Wait for everything to be published to the broker (with a sleep) and disconnect
        time.sleep(0.25)
        mqtt_client.disconnect()
        # Wait for disconnection acknowledgement (from on-disconnect callback function)
        timeout_start = time.time()
        while time.time() < timeout_start + 5:
            if not node_config["connected_to_broker"]:
                break
        if node_config["connected_to_broker"]:
            logging.error("MQTT-Client: Timeout disconnecting broker - Shutting down anyway")
        mqtt_client.loop_stop()
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
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot subscribe to MQTT messages")
    else:
        # The Identifier for a remote object is a string combining the the Node-ID and Object-ID
        item_identifier = create_remote_item_identifier(item_id,item_node)
        logging.info("MQTT-Client: Subscribing to '"+message_type+"' from '"+item_identifier+"'")
        # Topic format: "<Message-Type>/<Network-ID>/<Item_Identifier>/<optional-subtopic>"
        topic = message_type+"/"+node_config["network_identifier"]+"/"+item_identifier
        if subtopics: topic = topic+"/+"
        mqtt_client.subscribe(topic)
        # Add to the list of subscribed topics (so we can re-subscribe on reconnection)
        node_config["list_of_subscribed_topics"].append(topic)
        # Save the callback details for when we receive a message on the topic
        node_config["callbacks"][topic] = callback
        return()

#-----------------------------------------------------------------------------------------------
# Externally Called Function to Publish a message to the MQTT broker. This function takes
# in a string that defines the application-specific message type and converts this into
# a fully qualified MQTT topic. Data items are passed in as a list and converted to json
#-----------------------------------------------------------------------------------------------

def send_mqtt_message (message_type:str,item_id,data:dict,log_message:str=None,retain:bool=False,subtopic=None):
    # Only publish the broker if networking has been configured
    if node_config["network_configured"]:
        item_identifier = create_remote_item_identifier(item_id,node_config["node_identifier"])
        # Topic format: "<Message-Type>/<Network-ID>/<Item_Identifier>/<optional-subtopic>"
        topic = message_type+"/"+node_config["network_identifier"]+"/"+item_identifier
        if subtopic is not None: topic = topic+"/"+subtopic
        data["sourceidentifier"] = item_identifier
        payload = json.dumps(data)
        publish_message (topic,payload,log_message,retain)
    return()

#-----------------------------------------------------------------------------------------------
# Internal Function to Publish a json message to a fully qualified topic
#-----------------------------------------------------------------------------------------------

def publish_message (topic:str,payload:str,log_message:str=None,retain:bool=False):
    global logging
    global mqtt_client
    global node_config
    if log_message is not None: logging.info(log_message)
    if node_config["enhanced_debugging"]:
        if payload is None: logging.debug("MQTT-Client: Publishing NULL message to MQTT broker")
        else: logging.debug("MQTT-Client: Publishing JSON message to MQTT broker: "+payload)
    # Publish the message to the broker
    mqtt_client.publish(topic,payload,retain=retain,qos=1)
    # Add to the list of published topics if this is a retained message so we
    # can 'Clean up' the MQTT broker by publishing empty messages on shutdown
    if topic not in node_config["list_of_published_topics"]:
        node_config["list_of_published_topics"].append(topic)
    return()

##################################################################################################################