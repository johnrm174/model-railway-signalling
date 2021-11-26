#-----------------------------------------------------------------------------------------------
# This module provides a basic MQTT Client interface for the Model Railway Signalling Package, allowing
# multiple signalling applications (running on different computers)to share a single Pi-Sprog DCC interface.
# For example, you could run a signalling application on a computer without a Pi-Sprog (e.g. a Windows Laptop)
# and then configure that node to "publish" the DCC commands to be picked up by a Raspberry Pi Pi-Sprog Node
# where the commands will then be forwarded to the pi-Sprog interface and out to the DCC bus.
#
# To use these networking functions, you can either set up a local MQTT broker on one of the host computers
# on your local network or alternatively use an 'open source' broker out there on the internet - I've been
# using a test broker at "mqtt.eclipseprojects.io" (note this has no security or authentication).
#
# If you do intend using an internet-based broker then it is important to configure it with an appropriate level
# of security. This package does support basic username/password authentication when connecting in to the broker
# but note that these are NOT ENCRYPTED when sending over the internet unless you are also using a SSL connection.
#
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
#                         All received commands are automatically forwarded to the local Pi-Sprog interface.
#   Mandatory Parameters:
#       node:str - The name of the node to subscribe to
#
#-----------------------------------------------------------------------------------------------

import json
import logging
import paho.mqtt.client
from . import pi_sprog_interface
from . import signals_common
from . import common

#-----------------------------------------------------------------------------------------------
# Define an empty dictionary for holding the basic configuration information we need to track
#-----------------------------------------------------------------------------------------------

node_config: dict = {}
node_config["network_configured"] = False
node_config["network_identifier"] = None
node_config["node_identifier"] = None   
node_config["signals_to_publish_state_changes"] = []  
node_config["signals_to_publish_passed_events"] = []
node_config["enhanced_debugging"] = False
node_config["publish_dcc_commands"] = False

# Dictionary of signal states that we have published - we maintain our
# own local copy so we only transmit an update if something has changed
tx_sig_states = {}

#-----------------------------------------------------------------------------------------------
# Internal functions to create a signal object (containing basic state info) for a remote signal.
# As we are only able to query these signal objects wand use them as the "signal ahead" when we
# update a signal, we only need to hold the bare minimum of information
#-----------------------------------------------------------------------------------------------

def create_remote_signal_object(sig_callback = None):
    signal_object = {}
    signal_object["sigtype"] = signals_common.sig_type.remote_signal
    signal_object["sigstate"] = signals_common.signal_state_type.DANGER
    signal_object["sigclear"] = False
    signal_object["override"] = False
    signal_object["releaseonyel"] = False
    signal_object["releaseonred"] = False
    signal_object["extcallback"] = sig_callback
    return(signal_object)

def convert_to_remote_signal_object(object_to_convert):
    signal_object = {}
    signal_object["sigtype"] = object_to_convert["sigtype"]
    signal_object["sigstate"] = object_to_convert["sigstate"]
    signal_object["sigclear"] = object_to_convert["sigclear"]
    signal_object["override"] = object_to_convert["override"]
    signal_object["releaseonyel"] = object_to_convert["releaseonyel"]
    signal_object["releaseonred"] = object_to_convert["releaseonred"]
    signal_object["extcallback"] = object_to_convert["extcallback"]
    return (signal_object)

#-----------------------------------------------------------------------------------------------
# Internal call-back Function to process mqtt log messages (only called if enhanced_debugging is set)
#-----------------------------------------------------------------------------------------------

def on_log(mqtt_client, obj, level, mqtt_log_message):
    global logging
    logging.debug("MQTT-Client: "+mqtt_log_message)
    return()

#-----------------------------------------------------------------------------------------------
# Internal call-back Function to process received messages (from topics we have subscribed to)
# Received DCC Commands are forwarded on to the Pi-Sprog Interface (and then out to the DCC bus)
#-----------------------------------------------------------------------------------------------

def on_message(mqtt_client, obj, msg):
    global logging
    global node_config
    try:
        # Unpack the json message so we can extract the contents
        unpacked_json = json.loads(msg.payload)
    except Exception:
        logging.error("MQTT-Client: Couldn't parse received message: "+ str(msg.payload))
    else:
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Successfully parsed received message:"+str(unpacked_json))
            
        # Process the messages according to the Topic they were received against - note that we
        # will only be subscribed to topics associated with our unique-to-us network identifier
        
        if msg.topic.startswith("dcc_accessory_short_event"):
            source_node = unpacked_json[0]
            address = unpacked_json[1]
            active = unpacked_json[2]
            if active: 
                logging.debug ("MQTT-Client: Received ASON command from \'"+source_node+"\' for DCC address: "+str(address))
            else:
                logging.debug ("MQTT-Client: Received ASOF command from \'"+source_node+"\' for DCC address: "+str(address))
            # Forward the received DCC command on to the Pi-Sprog Interface (for transmission on the DCC Bus)
            pi_sprog_interface.send_accessory_short_event(address,active)
            
        elif msg.topic.startswith("signal_updated_event"):
            sig_identifier = unpacked_json[0]
            # Update our signal object - note that we receive the "Value" of the enumeration signal_state type
            received_sig_state={}
            received_sig_state["sigstate"] = signals_common.signal_state_type(unpacked_json[1])
            received_sig_state["sigclear"] = unpacked_json[2]
            received_sig_state["override"] = unpacked_json[3]
            received_sig_state["releaseonyel"] = unpacked_json[4]
            received_sig_state["releaseonred"] = unpacked_json[5]
            # Fill in the blanks so we can compare and update our internal object
            received_sig_state["sigtype"] = signals_common.signals[sig_identifier]["sigtype"]
            received_sig_state["extcallback"] = signals_common.signals[sig_identifier]["extcallback"]
            # Only make a callback if the state has changed since the last time we received something
            if signals_common.signals[sig_identifier] != received_sig_state:
                logging.debug ("MQTT-Client: Received signal state change for signal "+sig_identifier)
                signals_common.signals[sig_identifier] = received_sig_state
                # Raise the callback in the main tkinter thread as long as we know the main root window
                # Or as a fallback raise a callback in the current mqtt event thread
                if common.root_window is not None:
                    common.execute_function_in_tkinter_thread (lambda:signals_common.signals[sig_identifier]["extcallback"]
                                                    (sig_identifier,signals_common.sig_callback_type.sig_updated))
                else:    
                    signals_common.signals[sig_identifier]["extcallback"](sig_identifier,signals_common.sig_callback_type.sig_updated)

        elif msg.topic.startswith("signal_passed_event"):
            sig_identifier = unpacked_json[0]
            logging.debug ("MQTT-Client: Received signal passed event for signal "+sig_identifier)
            if common.root_window is not None:
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
    # Save all the information we need in a dictionary
    # Do some basic exception handling around opening the broker connection
    try:
        mqtt_client = paho.mqtt.client.Client()
        mqtt_client.on_message = on_message    
        if mqtt_enhanced_debugging: mqtt_client.on_log = on_log
        if broker_username is not None: mqtt_client.username_pw_set(username=broker_username,password=broker_password)
        mqtt_client.connect(broker_host)
        mqtt_client.loop_start()
    except Exception:
        logging.error("MQTT-Client: Couldn't connect to broker - Networking is disabled")
    else:
        node_config["enhanced_debugging"] = mqtt_enhanced_debugging
        node_config["network_identifier"] = network_identifier
        node_config["node_identifier"] = node_identifier
        node_config["publish_dcc_commands"] = publish_dcc_commands
        node_config["network_configured"] = True
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to the published DCC commands from another "Node"
#-----------------------------------------------------------------------------------------------

def subscribe_to_dcc_command_feed (node:str):    
    global logging
    global node_config
    global mqtt_client
    logging.info("MQTT-Client: Subscribe to dcc commands from \'"+node+"\'")
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot subscribe to dcc commands")
    else:
        # Subscribe to all the 'dcc_accessory_short_event' topics from a specified node on our network
        # These are in the following format: "dcc_accessory_short_event/<network-ID>/<node-ID>/<dcc-address>
        # We use a different topic for every dcc address so we can use "retained" messages to ensure when the
        # application starts up we will always receive the latest "state" of each dcc address from the broker
        # We wildcard the address (with a '+') to receive messages related to all DCC addresses for the node
        topics = "dcc_accessory_short_event/"+node_config["network_identifier"]+"/"+node+"/+"
        try:
            mqtt_client.subscribe(topics)
        except Exception:
            logging.error("MQTT-Client: Error subscribing to DCC command feed")
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
            logging.info("MQTT-Client: Subscribe to signal "+str(sig_id)+" updates from \'"+node+"\'")
            # Subscribe to the 'signal_updated_event' topic for the specified signal
            # These are in the following format: "signal_passed_event/<network-ID>/<signal-Identifier>
            # where the <signal-identifier> is the unique combination of the Node-ID and Sig-ID
            sig_identifier = signals_common.remote_signal_identifier(sig_id,node)
            topics = "signal_updated_event/"+node_config["network_identifier"]+"/"+sig_identifier
            try:
                mqtt_client.subscribe(topics)
            except Exception:
                logging.error("MQTT-Client: Error subscribing to signal updates feed")
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
            logging.info("MQTT-Client: Subscribe to signal "+str(sig_id)+" passed events from \'"+node+"\'")
            # Subscribe to the 'signal_passed_event' topic for the specified signal
            # These are in the following format: "signal_passed_event/<network-ID>/<signal-Identifier>
            # where the <signal-identifier> is the unique combination of the Node-ID and Sig-ID
            sig_identifier = signals_common.remote_signal_identifier(sig_id,node)
            topics = "signal_passed_event/"+node_config["network_identifier"]+"/"+sig_identifier
            try:
                mqtt_client.subscribe(topics)
            except Exception:
                logging.error("MQTT-Client: Error subscribing to signal passed events feed")
            # We now "Create" a dummy signal object to hold the state of the signal.
            # The identifier of the signal is a string combining the node and signal IDs.
            if not signals_common.sig_exists(sig_identifier):
                signal_object = create_remote_signal_object(sig_callback)
                signals_common.signals[sig_identifier] = signal_object
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to set signal updated events to be "published" for each subsequent state change
#-----------------------------------------------------------------------------------------------

def set_signals_to_publish_state(*sig_ids:int):    
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot configure signals to publish state changes")
    else:
        for sig_id in sig_ids:
            logging.info("MQTT-Client: Configure signal "+str(sig_id)+" to publish state changes")
            # Add the signal ID to the list of signals to publish
            if sig_id in node_config["signals_to_publish_state_changes"]:
                logging.warning("MQTT-Client: Signal "+str(sig_id)+" already configured to publish state changes")
            else:
                node_config["signals_to_publish_state_changes"].append(sig_id)
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to set signal updated events to be "published" for each subsequent state change
#-----------------------------------------------------------------------------------------------

def set_signals_to_publish_passed_events(*sig_ids:int):    
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot configure signals to publish signal passed events")
    else:
        for sig_id in sig_ids:
            logging.info("MQTT-Client: Configure signal "+str(sig_id)+" to publish signal passed events")
            # Add the signal ID to the list of signals to publish
            if sig_id in node_config["signals_to_publish_passed_events"]:
                logging.warning("MQTT-Client: Signal "+str(sig_id)+" already configured to publish signal passed events")
            else:
                node_config["signals_to_publish_passed_events"].append(sig_id)
    return()

#-----------------------------------------------------------------------------------------------
# Externally Called Function to send an Accessory Short CBUS On/Off Event
#-----------------------------------------------------------------------------------------------

def publish_accessory_short_event(address:int, active:bool):
    global logging
    global node_config
    global mqtt_client
    # Do some basic validation on the address
    if (address < 1 or address > 2047):
        logging.error ("MQTT-Client: Invalid DCC short event accessory address: "+ str(address))
    # Only publish the message if we have successfully configured the networking and are  
    # configured to publish DCC commands (otherwise we just drop out of the function)
    elif node_config["network_configured"] and node_config["publish_dcc_commands"]:
        if active:
            logging.debug ("MQTT-Client: Publishing DCC command ASON with DCC address: "+str(address)+" to broker")
        else:
            logging.debug ("MQTT-Client: Publishing DCC command ASOF with DCC address: "+str(address)+" to broker")
        # Encode the Message into JSON format
        message_payload = json.dumps([node_config["node_identifier"],address,active])
        # Publish to the appropriate topic: "dcc_accessory_short_event/<network-ID>/<node-ID>/<dcc-address>
        # We use a different topic for every dcc address so we can use "retained" messages to ensure when the
        # subscribing application starts up it will always receive the latest "state" of each dcc address
        message_topic = ( "dcc_accessory_short_event/"+node_config["network_identifier"]
                            +"/"+node_config["node_identifier"]+"/"+str(address) )
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Publishing JSON message to broker: "+message_payload)
        try:
            mqtt_client.publish(message_topic,message_payload,retain=True)
        except Exception:
            logging.error("MQTT-Client: Exception raised publishing message to broker: "+ message_payload)
    return()

#-----------------------------------------------------------------------------------------------
# Externally Called Function to Publish the state of a signal
#-----------------------------------------------------------------------------------------------

def publish_signal_state(sig_id:int):
    global logging
    global node_config
    global mqtt_client
    global tx_sig_states
    # Only publish the message if we have configured the MQTT network (successfully
    # established a connection to the broker) and set the signal to publish updates 
    if node_config["network_configured"] and sig_id in node_config["signals_to_publish_state_changes"]:
        
        # Create a new internal object to store the last transmitted sig stateif one doesn't exist
        if str(sig_id) not in tx_sig_states.keys():
            signal_object = create_remote_signal_object()
            tx_sig_states[str(sig_id)] = signal_object
            
        # Only transmit if the state has changed since the last time we sent something
        sig_state_to_publish =  convert_to_remote_signal_object(signals_common.signals[str(sig_id)])
        if sig_state_to_publish != tx_sig_states[str(sig_id)]:
            tx_sig_states[str(sig_id)] = sig_state_to_publish
             
            logging.debug ("MQTT-Client: Publishing state update for signal "+str(sig_id)+" to broker")
            # The "published" identifier of the signal is a string combining the node and signal IDs.
            sig_identifier = signals_common.remote_signal_identifier(sig_id,node_config["node_identifier"])
            # Encode the Message into JSON format (we send the "Value" of the enumeration signal_state type)
            message_payload = json.dumps( [ sig_identifier,
                        sig_state_to_publish["sigstate"].value, 
                        sig_state_to_publish["sigclear"], 
                        sig_state_to_publish["override"],
                        sig_state_to_publish["releaseonyel"],
                        sig_state_to_publish["releaseonred"] ] )
            # Publish to the appropriate topic: "signal_updated_event/<network-ID>/<sig_identifier>
            # where the <signal-identifier> is the unique combination of the Node-ID and Sig-ID
            # We use a different topic for every signal so we can use "retained" messages to ensure when the
            # subscribing application starts up it will always receive the latest "state" of each signal
            message_topic = "signal_updated_event/"+node_config["network_identifier"]+"/"+sig_identifier
            if node_config["enhanced_debugging"]:
                logging.debug("MQTT-Client: Publishing JSON message to broker: "+message_payload)
            try:
                mqtt_client.publish(message_topic,message_payload,retain=True)
            except Exception:
                logging.error("MQTT-Client: Exception raised publishing message to broker: "+ message_payload)
    return()

#-----------------------------------------------------------------------------------------------
# Externally Called Function to Publish the state of a signal
#-----------------------------------------------------------------------------------------------

def publish_signal_passed_event(sig_id:int):
    global logging
    global node_config
    global mqtt_client
    # Only publish the message if we have configured the MQTT network (successfully
    # established a connection to the broker) and set the signal to publish updates 
    if node_config["network_configured"] and sig_id in node_config["signals_to_publish_passed_events"]:
        logging.debug ("MQTT-Client: Publishing \'signal_passed\' event for signal "+str(sig_id)+" to broker")
        # The "published" identifier of the signal is a string combining the node and signal IDs.
        sig_identifier = signals_common.remote_signal_identifier(sig_id,node_config["node_identifier"])
        # Encode the Message into JSON format (we send the "Value" of the enumeration signal_state type)
        message_payload = json.dumps([sig_identifier])
        # Publish to the appropriate topic: "signal_updated_event/<network-ID>/<sig_identifier>
        # where the <signal-identifier> is the unique combination of the Node-ID and Sig-ID
        # As these are transitory events - we do not publish to the Broker as "retained messages"
        message_topic = "signal_passed_event/"+node_config["network_identifier"]+"/"+sig_identifier
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Publishing JSON message to broker: "+message_payload)
        try:
            mqtt_client.publish(message_topic,message_payload)
        except Exception:
            logging.error("MQTT-Client: Exception raised publishing message to broker: "+ message_payload)
    return()

##################################################################################################################