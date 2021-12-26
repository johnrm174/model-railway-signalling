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
# signals based on the one ahead) and "signal passed" events (for updating track occupancy sections) 
# 
# To use these networking functions, you can either set up a local MQTT broker on one of the host computers
# on your local network or alternatively use an 'open source' broker out there on the internet - I've been
# using a test broker at "mqtt.eclipseprojects.io" (note this has no security or authentication).
# 
# If you do intend using an internet-based broker then it is important to configure it with an appropriate level
# of security. This package does support basic username/password authentication for connecting in to the broker
# but note that these are NOT ENCRYPTED when sending over the internet unless you are also using a SSL connection.
#
# configure_networking - Configures the local MQTT broker client and establishes a connection to the broker
#   Mandatory Parameters:
#       broker_host:str - The fully qualified name/IP address of the MQTT broker host
#       network_identifier:str - The name to use for the signalling network (can be any string)
#       node_identifier:str - The name to use for a particular node on the network (can be any string)
#   Optional Parameters:
#       broker_port:int - The network port for the broker host (default = 1883)
#       broker_username:str - the username to log into the MQTT Broker (default = None)
#       broker_password:str - the password to log into the MQTT Broker (default = None)
#       publish_dcc_commands:bool - True to publish all DCC commands to the Broker (default = False)
#       mqtt_enhanced_debugging:bool - True to enable additional debug logging (default = False)
#
# subscribe_to_dcc_command_feed - Subcribes to the feed of DCC commands from other nodes on the network.
#                         All received DCC commands are automatically forwarded to the local Pi-Sprog interface.
#   Mandatory Parameters:
#       *nodes:str - The name of the node(s) publishing the DCC command feed (multiple nodes can be specified)
#
# subscribe_to_section_updates - Subscribe to track section updates from another node on the network 
#   Mandatory Parameters:
#       node:str - The name of the node publishing the track section update feed(s)
#       sec_callback:name - Function to call when a section update is received from the remote node
#                    The callback function returns (item_identifier, section_callback_type.section_updated),
#                    where item_identifier is a string in the following format "<node>-<sec_id>"
#       *sec_ids:int - The section(s) to subscribe to (multiple Section_IDs can be specified)
#
# subscribe_to_signal_updates - Subscribe to signal updates from another node on the network 
#   Mandatory Parameters:
#       node:str - The name of the node publishing the signal state update feed(s)
#       sig_callback:name - Function to call when a signal update is received from the remote node
#                    The callback function returns (item_identifier, sig_callback_type.sig_updated),
#                    where item_identifier is a string in the following format "<node>-<sig_id>"
#       *sig_ids:int - The signal(s) to subscribe to (multiple Signal_IDs can be specified)
#
# subscribe_to_signal_passed_events  - Subscribe to a "signal passed" event feed for a specified node/signal 
#   Mandatory Parameters:
#       node:str - The name of the node publishing the signal passed event feed(s)
#       sig_callback:name - Function to call when a signal passed event is received from the remote node
#                    The callback function returns (item_identifier, sig_callback_type.sig_passed),
#                    where Item Identifier is a string in the following format "<node>-<sig_id>"
#       *sig_ids:int - The signal(s) to subscribe to (multiple Signal_IDs can be specified)
#
# set_sections_to_publish_state - Enable the publication of state updates for specified track sections.
#                All subsequent state changes will be automatically published to remote subscribers
#   Mandatory Parameters:
#       *sec_ids:int - The track section(s) to publish (multiple Signal_IDs can be specified)
#
# set_signals_to_publish_state - Enable the publication of state updates for specified signals.
#                All subsequent state changes will be automatically published to remote subscribers
#   Mandatory Parameters:
#       *sig_ids:int - The signal(s) to publish (multiple Signal_IDs can be specified)
#
# set_signals_to_publish_passed_events - Enable the publication of signal passed events for specified signals.
#                All subsequent events will be automatically published to remote subscribers
#   Mandatory Parameters:
#       *sig_ids:int - The signal(s) to publish (multiple Signal_IDs can be specified)
#
#-----------------------------------------------------------------------------------------------

import json
import logging
import time
import paho.mqtt.client
from . import pi_sprog_interface
from . import signals_common
from . import track_sections
from . import common

#-----------------------------------------------------------------------------------------------
# Define an empty dictionary for holding the basic configuration information we need to track
#-----------------------------------------------------------------------------------------------

node_config: dict = {}
node_config["network_identifier"] = None
node_config["node_identifier"] = None   
node_config["sections_to_publish_state_changes"] = []  
node_config["signals_to_publish_state_changes"] = []  
node_config["signals_to_publish_passed_events"] = []
node_config["list_of_published_dcc_addresses"] = []
node_config["subscribed_topics"] = []
node_config["enhanced_debugging"] = False
node_config["publish_dcc_commands"] = False
node_config["network_configured"] = False
node_config["connected_to_broker"] = False

# ---------------------------------------------------------------------------------------------
# Common Function to create a external item identifier from the Item_ID and the remote Node.
# This identifier can then be used as the "key" to look up the Item in the associated dictionary
# ---------------------------------------------------------------------------------------------

def create_remote_item_identifier(item_id:int,node:str = None):
    return (node+"-"+str(item_id))

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
    if rc==0:
        logging.info("MQTT-Client: Broker connection terminated")
    else:
        logging.warning("MQTT-Client: Unexpected disconnection from broker")
    node_config["connected_to_broker"] = False
    return()

#-----------------------------------------------------------------------------------------------
# Internal call-back to process broker connection and re-connection events
#-----------------------------------------------------------------------------------------------

def on_connect(mqtt_client, userdata, flags, rc):
    global logging
    global node_config
    if rc == 0:
        logging.info("MQTT-Client: Successfully connected to MQTT Broker")
        # As we set up our broker connection with 'cleansession=true' a disconnection will have removed
        # all client connection information from the broked (including knowledge of the topics we have
        # subscribed to - we therefore need to re-subscribe to all topics with this new connection
        # Note that this means we will immediately receive all retained messages for those topics
        if len(node_config["subscribed_topics"]) > 0:
            logging.debug("MQTT-Client: Re-subscribing to all MQTT broker topics")
            for topic in node_config["subscribed_topics"]:
                mqtt_client.subscribe(topic)
        # Pause just to ensure that MQTT is all fully up and running before we continue (and allow the client
        # to set up any subscriptions or publish any messages to the broker. We shouldn't need to do this but
        # I've experienced problems running on a Windows 10 platform if we don't include a short sleep
        time.sleep(0.1)
        node_config["connected_to_broker"] = True
    elif rc == 1: logging.error("MQTT-Client: Connection refused – incorrect protocol version")
    elif rc == 2: logging.error("MQTT-Client: Connection refused – invalid client identifier")
    elif rc == 3: logging.error("MQTT-Client: Connection refused – server unavailable")
    elif rc == 4: logging.error("MQTT-Client: Connection refused – bad username or password")
    elif rc == 5: logging.error("MQTT-Client: Connection refused – not authorised")
    return()

#-----------------------------------------------------------------------------------------------
# Internal Functions to decode the received json messages and update our internal data objects
# Note that these functions are executed in the main tkinter thread to make it all threadsafe
#-----------------------------------------------------------------------------------------------

def process_signal_updated_event(unpacked_json):
    global logging
    sig_identifier,signal_state = unpacked_json
    # Only process the updated event if the state has changed (just to make it all a bit more robust)
    # Note that we receive the "Value" of the enumeration signal_state type rather than the descriptor
    if signals_common.signals[sig_identifier]["sigstate"] != signals_common.signal_state_type(signal_state): 
        signals_common.signals[sig_identifier]["sigstate"] = signals_common.signal_state_type(signal_state)
        logging.info ("Signal "+str(sig_identifier)+": Received Remote Signal State Update *****************************")
        logging.info ("Signal "+sig_identifier+": Aspect has changed to : "+
                        str(signals_common.signals[sig_identifier]["sigstate"]).rpartition('.')[-1])
        signals_common.signals[sig_identifier]["extcallback"](sig_identifier,
                                signals_common.sig_callback_type.sig_updated)
    return()

def process_section_updated_event(unpacked_json):
    global logging
    section_identifier,section_state,section_label = unpacked_json
    # Only process the updated event if the state has changed (just to make it all a bit more robust)
    if (track_sections.sections[section_identifier]["occupied"] != section_state or
              track_sections.sections[section_identifier]["labeltext"] != section_label ): 
        track_sections.sections[section_identifier]["occupied"] = section_state
        track_sections.sections[section_identifier]["labeltext"] = section_label
        logging.info ("Section "+section_identifier+": Received Remote Section State Update ****************************")
        if section_state:
            logging.info ("Section "+str(section_identifier)+": Changed to OCCUPIED (Label \'"+section_label+"\')")
        else:
            logging.info ("Section "+str(section_identifier)+": Changed to CLEAR (Label \'"+section_label+"\')")
        track_sections.sections[section_identifier]["extcallback"](section_identifier,
                                  track_sections.section_callback_type.section_updated)
    return()

def process_signal_passed_event(unpacked_json):
    global logging
    sig_identifier, = unpacked_json
    logging.info("Signal "+sig_identifier+": Received Remote Signal Passed Event ******************************")
    signals_common.signals[sig_identifier]["extcallback"](sig_identifier,
                            signals_common.sig_callback_type.sig_passed)
    return()

#--------------------------------------------------------------------------------------------------------
# Internal function to handle messages received from the MQTT Broker - detecting the message type
# and then calling the appropriate functions to decode the message and update the local data objects
# Note that we pass processing of all message that will update our local data objects back into the
# main tkinter thread (as long as we know the main root window) to make everything threadsafe.
# If we don't, then as a fallback raise a callback in the current mqtt event thread.
#--------------------------------------------------------------------------------------------------------

def on_message(mqtt_client, obj, msg):
    global logging
    global node_config
    global received_dcc_commands
    try:
        # Unpack the json message so we can extract the contents (with exception handling)
        unpacked_json = json.loads(msg.payload)
    except Exception as exception:
        # Note - we will also get an exception when a remote node shuts down and publishes a 'None'
        # message to the topic (to purge the broker queues of retained messages) - expected behavior
        # So we only log the error message if the message payload is not empty (i.e. for other cases)
        if msg.payload: logging.error("MQTT-Client: Exception unpacking json - "+str(exception))
    else:
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Successfully parsed received message:"+str(unpacked_json))
        
        #--------------------------------------------------------------
        # dcc_accessory_short_event
        #--------------------------------------------------------------
        if msg.topic.startswith("dcc_accessory_short_event"):
            source_node,dcc_address,dcc_state = unpacked_json
            # We can't implement logic to process DCC commands only if "something has changed" in terms of the state of an address
            # as we may have Event Driven signals (e.g. TrainTech) which rely on sending different states to different addresses
            # to change the aspects (e.g. transition from CAUTION => PROCEED may be AddressX => TRUE and then PROCEED => CAUTION
            # may be AddressY => TRUE so toggling between them would not be detected as a "change".
            if dcc_state: 
                logging.debug ("MQTT-Client: Received ASON command from \'"+source_node+"\' for DCC address: "+str(dcc_address))
            else:
                logging.debug ("MQTT-Client: Received ASOF command from \'"+source_node+"\' for DCC address: "+str(dcc_address))
            # Forward the received DCC command on to the Pi-Sprog Interface (for transmission on the DCC Bus)
            # As the Pi-Sprog interface uses an event queue passing messages to a seperate thread then it is
            # already thread safe and we don't need to execute this function in the main tkinter thread
            pi_sprog_interface.send_accessory_short_event(dcc_address,dcc_state)

        #--------------------------------------------------------------
        # signal_updated_event
        #--------------------------------------------------------------
        elif msg.topic.startswith("signal_updated_event"):
            if common.root_window is not None:
                common.execute_function_in_tkinter_thread(lambda:process_signal_updated_event(unpacked_json))
            else:    
                process_signal_updated_event(unpacked_json)
                
        #--------------------------------------------------------------
        # section_updated_event
        #--------------------------------------------------------------
        elif msg.topic.startswith("section_updated_event"):
            if common.root_window is not None:
                common.execute_function_in_tkinter_thread(lambda:process_section_updated_event(unpacked_json))
            else:    
                process_section_updated_event(unpacked_json)

        #--------------------------------------------------------------
        # signal_passed_event
        #--------------------------------------------------------------
        elif msg.topic.startswith("signal_passed_event"):
            if common.root_window is not None:
                common.execute_function_in_tkinter_thread (lambda:process_signal_passed_event(unpacked_json))
            else:    
                process_signal_passed_event(unpacked_json)

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
                          publish_dcc_commands:bool = False,
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
        node_config["publish_dcc_commands"] = publish_dcc_commands
        # Wait for connection acknowledgement (from on-connect callback function)
        timeout_start = time.time()
        while time.time() < timeout_start + 5:
            if node_config["connected_to_broker"]:
                node_config["network_configured"] = True
                break
        if not node_config["connected_to_broker"]:
            logging.error("MQTT-Client: Timeout connecting to broker - No messages will be published/received")
    return()

#-----------------------------------------------------------------------------------------------
# Externally called function to perform a gracefull shutdown of the MQTT networking
# in terms of clearing out the publish topic queues (by sending null messages)
#-----------------------------------------------------------------------------------------------

def mqtt_shutdown():
    global logging
    global node_config
    global mqtt_client
    # Only shut down the mqtt networking if we configured it in the first place
    if node_config["network_configured"]:
        logging.info("MQTT-Client: Clearing message queues and shutting down")
        # Clean out the message queues on the broker by publishing null messages (empty strings)
        # to each of the topics that we have sent messages to during the lifetime of the session
        
        # Clear out the Signal Update event topics
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Cleaning up Signal Update message topics")
        for sig_id in node_config["signals_to_publish_state_changes"]:
            sig_identifier = create_remote_item_identifier(sig_id,node_config["node_identifier"])
            message_topic = "signal_updated_event/"+node_config["network_identifier"]+"/"+sig_identifier
            mqtt_client.publish(message_topic,payload=None,retain=True,qos=1)

        # Clear out the Section Update event topics
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Cleaning up Section Update message topics")
        for sec_id in node_config["sections_to_publish_state_changes"]:
            sec_identifier = create_remote_item_identifier(sec_id,node_config["node_identifier"])
            message_topic = "section_updated_event/"+node_config["network_identifier"]+"/"+sec_identifier
            mqtt_client.publish(message_topic,payload=None,retain=True,qos=1)

        # Clear out the DCC Address event topics
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Cleaning up DCC Address message topics")
        for dcc_address in node_config["list_of_published_dcc_addresses"]:
            message_topic = ( "dcc_accessory_short_event/"+node_config["network_identifier"]
                                +"/"+node_config["node_identifier"]+"/"+str(dcc_address) )
            mqtt_client.publish(message_topic,payload=None,retain=True,qos=1)
            
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
# Public API Function to "subscribe" to signal updates published by another "Node"
#-----------------------------------------------------------------------------------------------

def subscribe_to_signal_updates (node:str,sig_callback,*sig_ids:int):    
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot subscribe to signal updates")
    else:
        for sig_id in sig_ids:
            logging.info("MQTT-Client: Subscribing to signal "+str(sig_id)+" updates from \'"+node+"\'")
            # The Identifier for a remote signal is a string combining the the Node-ID and Sig-ID.
            sig_identifier = create_remote_item_identifier(sig_id,node)
            # Subscribe to the 'signal_updated_event' topic for the specified signal
            # Topic is in the following format: "signal_updated_event/<Network-ID>/<Sig-Identifier>"
            topic = "signal_updated_event/"+node_config["network_identifier"]+"/"+sig_identifier
            mqtt_client.subscribe(topic)
            # Add to the list of subscribed topics (so we can re-subscribe on reconnection)
            node_config["subscribed_topics"].append(topic)
            # "Create" a dummy signal object to hold the state of the signal.
            if not signals_common.sig_exists(sig_identifier):
                signals_common.signals[sig_identifier] = {}
                signals_common.signals[sig_identifier]["sigtype"] = signals_common.sig_type.remote_signal
                signals_common.signals[sig_identifier]["sigstate"] = signals_common.signal_state_type.DANGER
                signals_common.signals[sig_identifier]["extcallback"] = sig_callback
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to section updates published by another "Node"
#-----------------------------------------------------------------------------------------------

def subscribe_to_section_updates (node:str,sec_callback,*sec_ids:int):    
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot subscribe to section updates")
    else:
        for sec_id in sec_ids:
            logging.info("MQTT-Client: Subscribing to section "+str(sec_id)+" updates from \'"+node+"\'")
            # The Identifier for a remote Track Section is a string combining the the Node-ID and Section-ID
            sec_identifier = create_remote_item_identifier(sec_id,node)
            # Subscribe to the 'section_updated_event' topic for the specified track section
            # Topic is in the following format: "section_updated_event/<Network-ID>/<Sig-Identifier>"
            topic = "section_updated_event/"+node_config["network_identifier"]+"/"+sec_identifier
            mqtt_client.subscribe(topic)
            # Add to the list of subscribed topics (so we can re-subscribe on reconnection)
            node_config["subscribed_topics"].append(topic)
            # "Create" a dummy section object to hold the state of the section.
            if not track_sections.section_exists(sec_identifier):
                track_sections.sections[sec_identifier] = {}
                track_sections.sections[sec_identifier]["occupied"] = False
                track_sections.sections[sec_identifier]["labeltext"] = "OCCUPIED"
                track_sections.sections[sec_identifier]["extcallback"] = sec_callback
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to "subscribe" to signal passed events published by another "Node"
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
            # The Identifier for a remote signal is a string combining the the Node-ID and Sig-ID.
            sig_identifier = create_remote_item_identifier(sig_id,node)
            # Subscribe to the 'signal_passed_event' topic for the specified signal
            # Topic is in the following format: "signal_passed_event/<Network-ID>/<Sig-Identifier>"
            topic = "signal_passed_event/"+node_config["network_identifier"]+"/"+sig_identifier
            mqtt_client.subscribe(topic)
            # Add to the list of subscribed topics (so we can re-subscribe on reconnection)
            node_config["subscribed_topics"].append(topic)
            # "Create" a dummy signal object to hold the state of the signal.
            if not signals_common.sig_exists(sig_identifier):
                signals_common.signals[sig_identifier] = {}
                signals_common.signals[sig_identifier]["sigtype"] = signals_common.sig_type.remote_signal
                signals_common.signals[sig_identifier]["sigstate"] = signals_common.signal_state_type.DANGER
                signals_common.signals[sig_identifier]["extcallback"] = sig_callback
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to set all aspect changes to be "published" for a signal
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
# Public API Function to set all section changes (label or state) to be "published" for a section
#-----------------------------------------------------------------------------------------------

def set_sections_to_publish_state(*sec_ids:int):    
    global logging
    global node_config
    global mqtt_client
    if not node_config["network_configured"]:
        logging.error("MQTT-Client: Networking Disabled - Cannot configure sections to publish state changes")
    else:
        for sec_id in sec_ids:
            logging.info("MQTT-Client: Configuring section "+str(sec_id)+" to publish state changes")
            # Add the signal ID to the list of signals to publish
            if sec_id in node_config["sections_to_publish_state_changes"]:
                logging.warning("MQTT-Client: Section "+str(sec_id)+" already configured to publish state changes")
            else:
                node_config["sections_to_publish_state_changes"].append(sec_id)
    return()

#-----------------------------------------------------------------------------------------------
# Public API Function to set all "signal passed" events to be "published" for a signal
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
    # Only publish the state if the network is configured and we have been told to publish updates 
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
        # Maintain a list of all DCC addresses we have published. This is so we can purge the message
        # queues on the broker (each DCC address is mapped to a topic) during a graceful shutdown
        if address not in node_config["list_of_published_dcc_addresses"]:
            node_config["list_of_published_dcc_addresses"].append(address)
    return()

#-----------------------------------------------------------------------------------------------
# Externally Called Function to Publish the state (displayed aspect) of a signal
#-----------------------------------------------------------------------------------------------

def publish_signal_state(sig_id:int):
    global logging
    global node_config
    global mqtt_client
    # Only publish the state if the network is configured and the signal is set to publish updates 
    if node_config["network_configured"] and sig_id in node_config["signals_to_publish_state_changes"]:
        logging.info ("Signal "+str(sig_id)+": Publishing state to MQTT Broker")
        # The Identifier for a remote signal is a string combining the the Node-ID and Sig-ID.
        sig_identifier = create_remote_item_identifier(sig_id,node_config["node_identifier"])
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
# Externally Called Function to Publish the state (label and OCCUPIED/CLEAR) of a Track Section
#-----------------------------------------------------------------------------------------------

def publish_section_state(sec_id:int):
    global logging
    global node_config
    global mqtt_client
    # Only publish the state if the network is configured and the section is set to publish updates
    if node_config["network_configured"] and sec_id in node_config["sections_to_publish_state_changes"]:
        logging.info ("Section "+str(sec_id)+": Publishing state to MQTT Broker")
        # The Identifier for a remote section is a string combining the the Node-ID and Sec-ID.
        section_identifier = create_remote_item_identifier(sec_id,node_config["node_identifier"])
        # Encode the Message into JSON format
        message_payload = json.dumps( [ section_identifier,
                                        track_sections.sections[str(sec_id)]["occupied"],
                                        track_sections.sections[str(sec_id)]["labeltext"] ] ) 
        # Publish to the appropriate topic: "section_updated_event/<network-ID>/<section_identifier>"
        # We use a different topic for each section so we can use "retained" messages to ensure when the
        # subscribing application starts up it will always receive the latest "state" change
        message_topic = "section_updated_event/"+node_config["network_identifier"]+"/"+section_identifier
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
    # Only publish the state if the network is configured and the signal is set to publish updates 
    if node_config["network_configured"] and sig_id in node_config["signals_to_publish_passed_events"]:
        logging.info ("Signal "+str(sig_id)+": Publishing signal passed event to MQTT Broker")
        # The Identifier for a remote signal is a string combining the the Node-ID and Sig-ID.
        signal_identifier = create_remote_item_identifier(sig_id,node_config["node_identifier"])
        # Encode the Message into JSON format (we just send the compound signal identifier)
        message_payload = json.dumps([signal_identifier])
        # Publish to the appropriate topic: "signal_updated_event/<network-ID>/<sig_identifier>"
        # As these are transitory events - we do not publish to the Broker as "retained messages"
        message_topic = "signal_passed_event/"+node_config["network_identifier"]+"/"+signal_identifier
        if node_config["enhanced_debugging"]:
            logging.debug("MQTT-Client: Publishing JSON message to MQTT broker: "+message_payload)
        mqtt_client.publish(message_topic,message_payload,qos=1)
    return()

##################################################################################################################