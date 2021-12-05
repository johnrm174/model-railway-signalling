#-----------------------------------------------------------------------------------------------
# These functions provides a basic MQTT Client interface for the Model Railway Signalling Package, allowing
# multiple signalling applications (running on different computers) to share a single Pi-Sprog DCC interface
# and to share signal states and signal updated events across a MQTT broker network.
#  
# For example, you could run one signalling application on a computer without a Pi-Sprog (e.g. a Windows Laptop),
# configure that node to "publish" its DCC command feed to the network and then configure another node (this time hosted
# on a Raspberry Pi) to "subscribe" to the same DCC command feed and then forwarded to its local pi-Sprog DCC interface.
# 
# You can also use these features to split larger layouts into multiple signalling areas whilst still being able to 
# implement a level of automation between them - primarily being aware of the "state" of remote signals (for updating
# signals based on the one ahead) and being notified when the remore signals have been passed (for track occupancy)
# 
# To use these networking functions, you can either set up a local MQTT broker on one of the host computers
# on your local network or alternatively use an 'open source' broker out there on the internet - I've been
# using a test broker at "mqtt.eclipseprojects.io" (note this has no security or authentication).
# 
# If you do intend using an internet-based broker then it is important to configure it with an appropriate level
# of security. This package does support basic username/password authentication for connecting in to the broker
# but note that these are NOT ENCRYPTED when sending over the internet unless you are also using a SSL connection.#
#
# configure_networking - Configures the local MQTT broker client and establishes a connection to the broker
#   Mandatory Parameters:
#       broker_host:str - The fully qualified name/IP address of the MQTT broker host to be used
#       network_identifier:str - The name to use for our signalling network (can be any string)
#       node_identifier:str - The name to use for this particular node on the network (can be any string)
#   Optional Parameters:
#       broker_username:str - the username to log into the MQTT Broker (default = None)
#       broker_password:str - the password to log into the MQTT Broker (default = None)
#       publish_dcc_commands:bool - True to publish all DCC commands to the Broker (default = False)
#       mqtt_enhanced_debugging:bool - True to enable additional debug logging (default = False)
#
# subscribe_to_dcc_command_feed - Subcribes to the feed of DCC commands from another node on the network.
#                         All received DCC commands are automatically forwarded to the local Pi-Sprog interface.
#   Mandatory Parameters:
#       *nodes:str - The name of the node publishing the DCC command feed (multiple nodes can be specified)
#
# subscribe_to_signal_updates - Subscribe to a signal update feed for a specified node/signal 
#   Mandatory Parameters:
#       node:str - The name of the node publishing the signal state feed
#       sig_callback:name - Function to call when a signal state update is received from the remote node
#                    Note that the callback function returns (item_identifier, sig_callback_type.sig_passed)
#                    Where Item Identifier is a string in the following format "<node>-<sig_id>"
#       *sig_ids:int - The signals to subscribe to (multiple Signal_IDs can be specified)
#
# subscribe_to_signal_passed_events  - Subscribe to a signal passed event feed for a specified node/signal 
#   Mandatory Parameters:
#       node:str - The name of the node publishing the signal passed event feed
#       sig_callback:name - Function to call when a signal passed event is received from the remote node
#                    Note that the callback function returns (item_identifier, sig_callback_type.sig_passed)
#                    Where Item Identifier is a string in the following format "<node>-<sig_id>"
#       *sig_ids:int - The signals to subscribe to (multiple Signal_IDs can be specified)
#
# set_signals_to_publish_state - Enable a feed of signal state updates for a specified signal. These will then
#                be automatically published to remote subscribers each time the state of the signal is changed
#   Mandatory Parameters:
#       *sig_ids:int - The signals to publish (multiple Signal_IDs can be specified)
#
# set_signals_to_publish_passed_events -  Enable a feed of signal updated events for a specified signal. These
#         will then be automatically published to remote subscribers each time a signal passed event is raised
#   Mandatory Parameters:
#       *sig_ids:int - The signals to publish (multiple Signal_IDs can be specified)
#
#-----------------------------------------------------------------------------------------------
# Some Notes on QoS - we use QoS1 for all messages published to the server:
#      QoS0 - At most once: The message is delivered at most once, or it may not be delivered at all.
#             Its delivery across the network is not acknowledged. The message is not stored.
#             The message could be lost if the client is disconnected, or if the server fails.
#             QoS0 is the fastest mode of transfer. It is sometimes called "fire and forget".
#      QoS1 - At least once: The message is always delivered at least once.It might be delivered multiple
#             times if there is a failure before an acknowledgment is received by the sender. The message
#             must be stored locally at the sender, until the sender receives confirmation that the message
#             has been published by the receiver. The message is stored in case the message must be sent again.
#      QoS2 - Exactly once: The message is always delivered exactly once. The message must be stored locally
#             at the sender, until the sender receives confirmation that the message has been published by
#             the receiver. The message is stored in case the message must be sent again. QoS2 is the safest,
#             but slowest mode of transfer. A more sophisticated handshaking and acknowledgement sequence is
#             used than for QoS1 to ensure no duplication of messages occurs.
#-----------------------------------------------------------------------------------------------

import json
import logging
import time
import paho.mqtt.client
from . import pi_sprog_interface
from . import signals_common
from . import common

#-----------------------------------------------------------------------------------------------
# Define an empty dictionary for holding the basic configuration information we need to track
#-----------------------------------------------------------------------------------------------

node_config: dict = {}
node_config["network_identifier"] = None
node_config["node_identifier"] = None   
node_config["signals_to_publish_state_changes"] = []  
node_config["signals_to_publish_passed_events"] = []
node_config["subscribed_topics"] = []
node_config["enhanced_debugging"] = False
node_config["publish_dcc_commands"] = False
node_config["network_configured"] = False
node_config["connected_to_broker"] = False

# -------------------------------------------------------------------------
# Common Function to create a external signal identifier from the Sig_ID and
# the remote Node (that the signal exists on). This identifier string can then
# be used as the "key" to look up the signal in the dictionary of Signals
# -------------------------------------------------------------------------

def create_remote_signal_identifier(sig_id:int,node:str = None):
    return (node+"-"+str(sig_id))

#-----------------------------------------------------------------------------------------------
# Internal functions to create a signal object (containing basic state info) for a remote signal.
# As we are only able to query these signal objects wand use them as the "signal ahead" when we
# update a signal, we only need to hold the bare minimum of information
#-----------------------------------------------------------------------------------------------

def create_remote_signal_object(sig_callback = None):
    signal_object = {}
    signal_object["sigtype"] = signals_common.sig_type.remote_signal
    signal_object["sigstate"] = signals_common.signal_state_type.DANGER
    signal_object["extcallback"] = sig_callback
    return(signal_object)

#-----------------------------------------------------------------------------------------------
# Internal call-back Function to process mqtt log messages (only called if enhanced_debugging is set)
#-----------------------------------------------------------------------------------------------

def on_log(mqtt_client, obj, level, mqtt_log_message):
    global logging
    logging.debug("MQTT-Client: "+mqtt_log_message)
    return()

#-----------------------------------------------------------------------------------------------
# Internal call-back Functions to process broker disconnection / connection events
#-----------------------------------------------------------------------------------------------

def on_disconnect(mqtt_client, userdata, rc):
    global logging
    global node_config
    if rc==0:
        logging.info("MQTT-Client: Broker connection successfully terminated")
    else:
        logging.warning("MQTT-Client: Unexpected Disconnection from MQTT Broker")
    node_config["connected_to_broker"] = False
    return()

def on_connect(mqtt_client, userdata, flags, rc):
    global logging
    global node_config
    if rc == 0:
        logging.info("MQTT-Client: Connected to MQTT Broker")
        node_config["connected_to_broker"] = True
        # As we set up our broker connection with 'cleansession=true' a disconnection will have removed
        # all client connection information from the broked (including knowledge of the topics we have
        # subscribed to - we therefore need to re-subscribe to all topics with this new connection
        # Note that this means we will immediately receive all retained messages for those topics
        if len(node_config["subscribed_topics"]) > 0:
            logging.debug("MQTT-Client: Re-subscribing to all MQTT broker topics")
            for topic in node_config["subscribed_topics"]:
                mqtt_client.subscribe(topic)
    elif rc == 1:
        logging.error("MQTT-Client: Connection refused – incorrect protocol version")
    elif rc == 2:
        logging.error("MQTT-Client: Connection refused – invalid client identifier")
    elif rc == 3:
        logging.error("MQTT-Client: Connection refused – server unavailable")
    elif rc == 4:
        logging.error("MQTT-Client: Connection refused – bad username or password")
    elif rc == 5:
        logging.error("MQTT-Client: Connection refused – not authorised")
    return()

#-----------------------------------------------------------------------------------------------
# Internal call-back Function to process received messages (from topics we have subscribed to)
# Received DCC Commands are forwarded on to the Pi-Sprog Interface (and then out to the DCC bus)
#-----------------------------------------------------------------------------------------------

def on_message(mqtt_client, obj, msg):
    global logging
    global node_config
    global received_dcc_commands
    # Unpack the json message so we can extract the contents
    unpacked_json = json.loads(msg.payload)
    if node_config["enhanced_debugging"]:
        logging.debug("MQTT-Client: Successfully parsed received message:"+str(unpacked_json))
        
    # Process the messages according to the Topic they were received against - note that we
    # will only be subscribed to topics associated with our unique-to-us network identifier
    
    if msg.topic.startswith("dcc_accessory_short_event"):
        source_node,dcc_address,dcc_state = unpacked_json
        # We can't implement logic to process DCC commands only if "something has changed" in terms of the state of an address
        # as we may have Event Driven signals (e.g. TrainTech) which rely on sending different states to different addresses
        # to change the aspects (e.g. transition from CAUTION => PROCEED may be AddressX => TRUE and then PROCEED => CAUTION
        # may be AddressY => TRUE so toggling between them would not be detected as a "change". This does mean that following
        # disconnection/reconnection events we may get a flood od DCC messages that we have to process in turn
        if dcc_state: 
            logging.debug ("MQTT-Client: Received ASON command from \'"+source_node+"\' for DCC address: "+str(dcc_address))
        else:
            logging.debug ("MQTT-Client: Received ASOF command from \'"+source_node+"\' for DCC address: "+str(dcc_address))
        # Forward the received DCC command on to the Pi-Sprog Interface (for transmission on the DCC Bus)
        pi_sprog_interface.send_accessory_short_event(dcc_address,dcc_state)
        
    elif msg.topic.startswith("signal_updated_event"):
        sig_identifier,signal_state = unpacked_json
        # Only process the updated event if the state has changed - this is primarily to handle client re-connection
        # events (following an unexpected disconnection) where we will immediately receive all retained messages
        # on the topics we have re-subscribed to - even if we have already received them prior to the disconnection
        # Note that we receive the "Value" of the enumeration signal_state type rather than the descriptor
        if signals_common.signals[sig_identifier]["sigstate"] != signals_common.signal_state_type(signal_state): 
            signals_common.signals[sig_identifier]["sigstate"] = signals_common.signal_state_type(signal_state)
            logging.info ("Signal "+sig_identifier+": Received signal state from MQTT Broker")
            # Raise the callback in the main tkinter thread (as long as we know the main root window) to make
            # it all threadsafe - Or as a fallback raise a callback in the current mqtt event thread
            if common.root_window is not None:
                common.execute_function_in_tkinter_thread (lambda:signals_common.signals[sig_identifier]["extcallback"]
                                                (sig_identifier,signals_common.sig_callback_type.sig_updated))
            else:    
                signals_common.signals[sig_identifier]["extcallback"](sig_identifier,signals_common.sig_callback_type.sig_updated)

    elif msg.topic.startswith("signal_passed_event"):
        sig_identifier, = unpacked_json
        # A signal passed event is an event in time - therefore these are not sent to the broker as retained messages
        # and therefore we don't need to do anything specific to handle disconnection/re-connection events - if we've
        # missed a signal passed event whilst we've been disconnected then its just bad luck!
        logging.info ("Signal "+sig_identifier+": Received \'signal passed\' event from MQTT Broker")
        if common.root_window is not None:
            # Raise the callback in the main tkinter thread (as long as we know the main root window) to make
            # it all threadsafe - Or as a fallback raise a callback in the current mqtt event thread
            common.execute_function_in_tkinter_thread (lambda:signals_common.signals[sig_identifier]["extcallback"]
                                            (sig_identifier,signals_common.sig_callback_type.sig_passed))
        else:    
            signals_common.signals[sig_identifier]["extcallback"](sig_identifier,signals_common.sig_callback_type.sig_updated)

    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to configure the networking for this particular network "Node"
#-----------------------------------------------------------------------------------------------

def configure_networking (broker_host:str,
                          network_identifier:str,
                          node_identifier:str,
                          broker_username:str = None,
                          broker_password:str = None,
                          publish_dcc_commands:bool = False,
                          mqtt_enhanced_debugging:bool = False):
    global logging
    global node_config
    global mqtt_client
    logging.info("MQTT-Client: Connecting to Broker \'"+broker_host+"\'")
    # Do some basic exception handling around opening the broker connection
    try:
        mqtt_client = paho.mqtt.client.Client(clean_session=True)
        mqtt_client.on_message = on_message    
        mqtt_client.on_connect = on_connect    
        mqtt_client.on_disconnect = on_disconnect    
        if mqtt_enhanced_debugging: mqtt_client.on_log = on_log
        if broker_username is not None: mqtt_client.username_pw_set(username=broker_username,password=broker_password)
        mqtt_client.reconnect_delay_set(min_delay=1, max_delay=10)
        mqtt_client.connect(broker_host, keepalive = 10)
        mqtt_client.loop_start()
    except Exception as exception:
        logging.error("MQTT-Client: Failed to connect to broker - "+str(exception))
    else:
        node_config["enhanced_debugging"] = mqtt_enhanced_debugging
        node_config["network_identifier"] = network_identifier
        node_config["node_identifier"] = node_identifier
        node_config["publish_dcc_commands"] = publish_dcc_commands
        # Wait for connection acknowledgement (from on-connect callback function)
        timeout_start = time.time()
        while time.time() < timeout_start + 5:
            if node_config["connected_to_broker"]:
                node_config["network_configured"] = True
                break
        if not node_config["connected_to_broker"]:
            logging.error("MQTT-Client: Timeout connecting to broker - No messages will be published/received")
        # Pause just to ensure that MQTT is all fully up and running before we continue (and allow the client
        # to set up any subscriptions or publish any messages to the broker. We shouldn't need to do this but
        # I've experienced problems running on a Windows 10 platform if we don't include a short sleep
        time.sleep(0.1)
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to the published DCC commands from another "Node"
#-----------------------------------------------------------------------------------------------

def subscribe_to_dcc_command_feed (*nodes:str):    
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot subscribe to dcc commands")
    else:
        for node in nodes:
            logging.info("MQTT-Client: Subscribe to dcc command feed from \'"+node+"\'")
            # Subscribe to the 'dcc_accessory_short_event' topics from the specified node
            # Topics are in the following format: "dcc_accessory_short_event/<network-ID>/<node-ID>/<dcc-address>
            # We use a different topic for every dcc address so we can use "retained" messages to ensure when the
            # application starts up we will always receive the latest "state" of each dcc address from the broker
            # We wildcard the address (with a '+') to receive messages related to all DCC addresses for the node
            topic = "dcc_accessory_short_event/"+node_config["network_identifier"]+"/"+node+"/+"
            mqtt_client.subscribe(topic)
            # Add to the list of subscribed topics (so we can re-subscribe on reconnection)
            node_config["subscribed_topics"].append(topic)
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to signal updated published by another "Node"
#-----------------------------------------------------------------------------------------------

def subscribe_to_signal_updates (node:str, sig_callback, *sig_ids:int):    
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot subscribe to signal updates")
    else:
        for sig_id in sig_ids:
            logging.info("MQTT-Client: Subscribing to signal "+str(sig_id)+" updates from \'"+node+"\'")
            # The Sig-Identifier for a remote signal is a string combining the the Node-ID and Sig-ID.
            sig_identifier = create_remote_signal_identifier(sig_id,node)
            # Subscribe to the 'signal_updated_event' topic for the specified signal
            # Topic is in the following format: "signal_updated_event/<Network-ID>/<Sig-Identifier>"
            topic = "signal_updated_event/"+node_config["network_identifier"]+"/"+sig_identifier
            mqtt_client.subscribe(topic)
            # Add to the list of subscribed topics (so we can re-subscribe on reconnection)
            node_config["subscribed_topics"].append(topic)
            # We now "Create" a dummy signal object to hold the state of the signal.
            if not signals_common.sig_exists(sig_identifier):
                signal_object = create_remote_signal_object(sig_callback)
                signals_common.signals[sig_identifier] = signal_object
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to signal updated published by another "Node"
#-----------------------------------------------------------------------------------------------

def subscribe_to_signal_passed_events (node:str, sig_callback, *sig_ids:int):    
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot subscribe to signal passed events")
    else:
        for sig_id in sig_ids:
            logging.info("MQTT-Client: Subscribing to signal "+str(sig_id)+" passed events from \'"+node+"\'")
            # The Sig-Identifier for a remote signal is a string combining the the Node-ID and Sig-ID.
            sig_identifier = create_remote_signal_identifier(sig_id,node)
            # Subscribe to the 'signal_passed_event' topic for the specified signal
            # Topic is in the following format: "signal_passed_event/<Network-ID>/<Sig-Identifier>"
            topic = "signal_passed_event/"+node_config["network_identifier"]+"/"+sig_identifier
            mqtt_client.subscribe(topic)
            # Add to the list of subscribed topics (so we can re-subscribe on reconnection)
            node_config["subscribed_topics"].append(topic)
            # We now "Create" a dummy signal object to hold the state of the signal.
            if not signals_common.sig_exists(sig_identifier):
                signal_object = create_remote_signal_object(sig_callback)
                signals_common.signals[sig_identifier] = signal_object            
    return()

#-----------------------------------------------------------------------------------------------
# Public Function to set all signal state (aspect) updates to be "published" for a signal
#-----------------------------------------------------------------------------------------------

def set_signals_to_publish_state(*sig_ids:int):    
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot configure signals to publish state changes")
    else:
        for sig_id in sig_ids:
            logging.info("MQTT-Client: Configuring signal "+str(sig_id)+" to publish state changes")
            # Add the signal ID to the list of signals to publish
            if sig_id in node_config["signals_to_publish_state_changes"]:
                logging.warning("MQTT-Client: Signal "+str(sig_id)+" already configured to publish state changes")
            else:
                node_config["signals_to_publish_state_changes"].append(sig_id)
    return()

#-----------------------------------------------------------------------------------------------
# Public  Function to set all "signal passed" events to be "published" for a signal
#-----------------------------------------------------------------------------------------------

def set_signals_to_publish_passed_events(*sig_ids:int):    
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot configure signals to publish signal passed events")
    else:
        for sig_id in sig_ids:
            logging.info("MQTT-Client: Configuring signal "+str(sig_id)+" to publish signal passed events")
            # Add the signal ID to the list of signals to publish
            if sig_id in node_config["signals_to_publish_passed_events"]:
                logging.warning("MQTT-Client: Signal "+str(sig_id)+" already configured to publish signal passed events")
            else:
                node_config["signals_to_publish_passed_events"].append(sig_id)
    return() 

#-----------------------------------------------------------------------------------------------
# Externally Called Function to publish an Accessory Short CBUS On/Off Event
#-----------------------------------------------------------------------------------------------

def publish_accessory_short_event(address:int, active:bool):
    global logging
    global node_config
    global mqtt_client
    # Only publish the message if we have successfully configured the networking and are  
    # configured to publish DCC commands (otherwise we just drop out of the function)
    if node_config["network_configured"] and node_config["publish_dcc_commands"]:
        if active:
            logging.debug ("MQTT-Client: Publishing DCC command ASON with DCC address: "+str(address)+" to MQTT broker")
        else:
            logging.debug ("MQTT-Client: Publishing DCC command ASOF with DCC address: "+str(address)+" to MQTT broker")
        # Encode the Message into JSON format (the node identifier, the dcc address and the required state)
        message_payload = json.dumps([node_config["node_identifier"],address,active])
        # Publish to the appropriate topic: "dcc_accessory_short_event/<network-ID>/<node-ID>/<dcc-address>
        # We use a different topic for every dcc address so we can use "retained" messages to ensure when the
        # subscribing application starts up it will always receive the latest "state" of each dcc address
        message_topic = ( "dcc_accessory_short_event/"+node_config["network_identifier"]
                            +"/"+node_config["node_identifier"]+"/"+str(address) )
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Publishing JSON message to MQTT broker: "+message_payload)
        mqtt_client.publish(message_topic,message_payload,retain=True,qos=1)
    return()

#-----------------------------------------------------------------------------------------------
# Externally Called Function to Publish the state (displayed aspect) of a signal
#-----------------------------------------------------------------------------------------------

def publish_signal_state(sig_id:int):
    global logging
    global node_config
    global mqtt_client
    # Only publish the message if we have configured the MQTT network (successfully
    # established a connection to the broker) and set the signal to publish updates 
    if node_config["network_configured"] and sig_id in node_config["signals_to_publish_state_changes"]:
        logging.info ("Signal "+str(sig_id)+": Publishing signal state update to MQTT Broker")
        # The Sig-Identifier for a remote signal is a string combining the the Node-ID and Sig-ID.
        sig_identifier = create_remote_signal_identifier(sig_id,node_config["node_identifier"])
        # Encode the Message into JSON format (we send the "Value" of the enumeration signal_state type)
        message_payload = json.dumps( [ sig_identifier,signals_common.signals[str(sig_id)]["sigstate"].value ] ) 
        # Publish to the appropriate topic: "signal_updated_event/<network-ID>/<sig_identifier>"
        # We use a different topic for every signal so we can use "retained" messages to ensure when the
        # subscribing application starts up it will always receive the latest "state" of each signal
        message_topic = "signal_updated_event/"+node_config["network_identifier"]+"/"+sig_identifier
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Publishing JSON message to MQTT broker: "+message_payload)
        mqtt_client.publish(message_topic,message_payload,retain=True,qos=1)
    return()

#-----------------------------------------------------------------------------------------------
# Externally Called Function to Publish a "Signal Passed" Event
#-----------------------------------------------------------------------------------------------

def publish_signal_passed_event(sig_id:int):
    global logging
    global node_config
    global mqtt_client
    # Only publish the message if we have configured the MQTT network (successfully
    # established a connection to the broker) and set the signal to publish updates 
    if node_config["network_configured"] and sig_id in node_config["signals_to_publish_passed_events"]:
        logging.info ("Signal "+str(sig_id)+": Publishing signal passed event to MQTT Broker")
        # The Sig-Identifier for a remote signal is a string combining the the Node-ID and Sig-ID.
        sig_identifier = create_remote_signal_identifier(sig_id,node_config["node_identifier"])
        # Encode the Message into JSON format (we just send the compound signal identifier)
        message_payload = json.dumps([sig_identifier])
        # Publish to the appropriate topic: "signal_updated_event/<network-ID>/<sig_identifier>"
        # As these are transitory events - we do not publish to the Broker as "retained messages"
        message_topic = "signal_passed_event/"+node_config["network_identifier"]+"/"+sig_identifier
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Publishing JSON message to MQTT broker: "+message_payload)
        mqtt_client.publish(message_topic,message_payload,qos=1)
    return()

##################################################################################################################