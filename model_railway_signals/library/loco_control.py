#----------------------------------------------------------------------------------------------------
# This module contains the basic functions for DCC loco session management and control
# which can be either via the local SPROG interface or via a remote SPROG interface
# running on another signalling node (via MQTT Networking
#----------------------------------------------------------------------------------------------------
##
# External API - the classes and functions (used by the Schematic Editor):
#
#
# The following API functions are for configuring the pub/sub of DCC command feeds. The functions are called
# by the editor on 'Apply' of the MQTT settings. First, 'reset_loco_mqtt_configuration' is called to clear down
# the existing pub/sub configuration, followed by 'set_node_to_publish_dcc_commands' (either True or False)
# and 'subscribe_to_dcc_command_feed' for each REMOTE DCC Node (DCC Command feed subscribed).
#
#   reset_dcc_loco_mqtt_configuration() - Clears down the current DCC Command feed pub/sub configuration
#
#   set_node_to_publish_dcc_locomotive_commands(sprog_node) - set node to publish loco commands to the SPROG Node
#           All DCC locomotive commands will then be published to the MQTT broker for consumption by other nodes
#
#   subscribe_to_dcc_locomotive_command_feed(nodes) - subscribe to DCC locomotive commands from other nodes
#           All received DCC locomotive commands will then be automatically forwarded to the local SPROG interface.
#
#    subscribe_to_dcc_power_updates(callback) - subscribe to DCC power state
#    unsubscribe_from_dcc_power_updates(callback) - unsubscribe from DCC power state
#        Note that this will be either the local of remote SPROG interface depending
#        on whether the publish_dcc_locomotive_commands_to_mqtt_broker is set
#
#   request_loco_session(dcc_address) - generates a loco session and returns session_id
#   release_loco_session(session_id) - releases the locomotive session
#   set_loco_speed_and_direction(session_id:int, speed:int, forward:bool)
#   send_emergency_stop(session_id) - Emergency Stops the loco
#   set_loco_function(session_id:int, function_id:int, state:bool)

#
# Internal API - classes and functions (used by the other library modules):
#
#   handle_mqtt_dcc_power_event(message)
#   handle_mqtt_dcc_acknowledge_event(message)
#   handle_mqtt_dcc_locomotive_control_event(message)
#----------------------------------------------------------------------------------------------------

import logging

from . import pi_sprog_interface
from . import mqtt_interface
from . import common

#----------------------------------------------------------------------------------------------------
# Global definitions
#----------------------------------------------------------------------------------------------------

# Define the Flag to control whether DCC Commands are published to the MQTT Broker
publish_dcc_locomotive_commands_to_mqtt_broker:bool = False

# Other global variables we need to track
session_acknowledgement_callbacks = {}
registered_dcc_power_state_callbacks = []
remote_dcc_power_is_on = None   # Unknown

#----------------------------------------------------------------------------------------------------
# API Functions to register/unregister for DCC power status updates (local or remote)
#----------------------------------------------------------------------------------------------------

def subscribe_to_dcc_power_updates(callback):
    if publish_dcc_locomotive_commands_to_mqtt_broker:
        # Register the callback for DCC Power updates from the remote SPROG
        if callback not in registered_dcc_power_state_callbacks:
            registered_dcc_power_state_callbacks.append(callback)
        # If the remote node has already subscribed to the DCC loco feed from
        # other nodes then it will already have sent out a DCC power message
        # Similarly, if this node has been set to publish the loco feed then
        # we will already be subscribed to the DCC power feed from the remote
        # node and so the global remote_dcc_power_is_on will contain the state
        callback(remote_dcc_power_is_on)
    else:
        # Subscribe to updates from the local SPROG interface. this will trigger
        # an immediate callback to let the client know the current powerstate.
        pi_sprog_interface.subscribe_to_local_dcc_power_updates(callback)
    return()

def unsubscribe_from_dcc_power_updates(callback):
    # To be on the safe side, we unsubscribe from both local and remote SPROG DCC
    # power feeds (just in case the publish_dcc_locomotive_commands_to_mqtt_broker
    # Flag has been changed by a user configuration update)
    global registered_dcc_power_state_callbacks
    if callback in registered_dcc_power_state_callbacks:
        registered_dcc_power_state_callbacks.remove(callback)
    pi_sprog_interface.unsubscribe_from_local_dcc_power_updates(callback)
    return()

#----------------------------------------------------------------------------------------------------
# Callback for handling DCC power updates received from the remote SPROG node. This will apply to
# situations where we are a remote client of a SPROG Node somewhere out on the MQTT network.
# We need to know the power state of the SPROG node in order to update our Throttle UIs.
# A node subscribes to these updates when configured to subscribe to remote DCC loco feeds
# A node publishes the initial power state when configured to publish the loco feed
#----------------------------------------------------------------------------------------------------

def handle_mqtt_dcc_power_event(message):
    global remote_dcc_power_is_on
    if "sourceidentifier" not in message.keys() or "dccpower" not in message.keys():
        logging.error (f"Loco Control: Unhandled MQTT Message - {message}")
    else:
        # All Messages include the following mandatory elements
        source_node = message["sourceidentifier"]
        dcc_power = message["dccpower"]
        logging.debug(f"Loco Control: Received DCC Power message from {source_node}: power={dcc_power}")
        # Update the global remote power status
        remote_dcc_power_is_on = dcc_power
        # Make the callbacks to all registered clients
        for power_status_changed_callback in registered_dcc_power_state_callbacks:
            power_status_changed_callback(remote_dcc_power_is_on)
    return()

#----------------------------------------------------------------------------------------------------
# Callback for handling DCC session acknowledgements received from the SPROG Node
# in response to a session request from a throttle running on this machine.
# We make the callback to update the client on the status of the session request
#----------------------------------------------------------------------------------------------------

def handle_mqtt_dcc_acknowledge_event(message):
    message
    if "sourceidentifier" not in message.keys() or "dccaddress" not in message.keys() or "sessionid" not in message.keys():
        logging.error (f"Loco Control: Unhandled MQTT Message - {message}")
    else:
        # All Messages include the following mandatory elements
        source_node = message["sourceidentifier"]
        dcc_address = message["dccaddress"]
        session_id = message["sessionid"]
        if dcc_address in session_acknowledgement_callbacks.keys():
            logging.debug(f"Loco Control: Received session acknowledgement from {source_node}: "
                               +f"DCC Address {dcc_address}, Session ID is {session_id}")
            session_acknowledgement_callbacks[dcc_address] (dcc_address, session_id)
    return()

#----------------------------------------------------------------------------------------------------
# Callback for handling DCC locomotive commands received from a remote signalling node and sending
# them out to the Pi-SPROG to change the speed/direction/functions of the loco. This will apply to
# situations where we are the SPROG Node and there are remote throttle nodes on the MQTT network.
# A typical exchange would be as follows:
#   Client node - sends dcc_address with session_id=0 to request a loco session
#   This node - Responds with dcc_acknowledgement_event
#   Client Node - Sends speed/direction change messages as required
#   Client Node - Sends loco function change messages as required
#   Client Node - Sends session_id with dcc_address=0 to release the loco
# If this node terminates the session (i.e. DCC power has been turned off):
#   This node - Sends session_id with dcc_address=0 (to report the session terminated)
#----------------------------------------------------------------------------------------------------

def handle_mqtt_dcc_locomotive_control_event(message):
    if "sourceidentifier" not in message.keys() or "dccaddress" not in message.keys() or "sessionid" not in message.keys():
        logging.error ("Loco Control: Unhandled MQTT Message - "+str(message))
    else:
        # All Messages include the following mandatory elements
        source_node = message["sourceidentifier"]
        dcc_address = message["dccaddress"]
        session_id = message["sessionid"]
        # The following elements are optional - if not present then the values will be set to none
        speed = message.get("speed")
        direction = message.get("direction")
        func_id = message.get("functionid")
        func_state = message.get("functionstate")
        # Handle speed/direction commands from a remote throttle
        # Note that Direction of None is a valid "state" as far as the UI is concerned
        if speed is not None:
            logging.debug (f"Loco Control: Received message for Session {session_id} on {source_node}: speed={speed}, forward={direction}")
            pi_sprog_interface.set_loco_speed_and_direction(session_id, speed, direction)
        # Handle loco function commands from a remote throttle
        elif func_id is not None and func_state is not None:
            logging.debug (f"Loco Control: Received message for Session {session_id} on {source_node}: function={func_id}, state={func_state}")
            pi_sprog_interface.set_loco_function(session_id, func_id, func_state)
        # Handle loco session request from a remote throttle
        elif dcc_address > 0 and session_id == 0:
            logging.debug (f"Loco Control: Received Session Request message for DCC Address {dcc_address} from {source_node}")
            loco_session = pi_sprog_interface.request_loco_session(dcc_address)
            # Acknowledge the session back to the client (session ID will be zero if unsuccessful)
            mqtt_interface.send_mqtt_message("dcc_acknowledge_events", 0, retain=True,
                        data={"dccaddress": dcc_address, "sessionid": loco_session},
                        log_message="Loco Control: Publishing session acknowledgement message to broker")
        # Handle loco session release request from a remote node
        elif dcc_address == 0 and session_id > 0:
            logging.debug (f"Loco Control: Received Session Release message for Session {session_id} from {source_node}")
            pi_sprog_interface.release_loco_session(session_id)
    return()

#----------------------------------------------------------------------------------------------------
# Internal Function to send a Loco Control event to the SPROG Node. This will apply to situations
# where we are a remote client of a SPROG Node somewhere out there on the MQTT network.
# Mandatory Elements are "sourceidentifier", "dccaddress" and "sessionid"
# Optional elements are "speed", "direction", "functionid", "functionstate"
#----------------------------------------------------------------------------------------------------

def send_mqtt_dcc_locomotive_control_event(message:dict):
    if "dccaddress" not in message.keys() and "sessionid" not in message.keys():
        logging.error ("Loco Control: Invalid loco control Message - "+str(message))
    elif publish_dcc_locomotive_commands_to_mqtt_broker:
        mqtt_interface.send_mqtt_message("dcc_locomotive_control_events", 0, data=message, retain=True,
                log_message=f"Loco Control: Publishing loco control message to broker :{message}")
    return()

#----------------------------------------------------------------------------------------------------
# Internal Function to forward the current DCC power state to remote nodes. This will apply to
# situations where we are The SPROG Node and there are remote throttle nodes on the MQTT network.
# This function will be called by the SPROG interface (where we have registered a callback)
#----------------------------------------------------------------------------------------------------

def send_dcc_power_status_update_events(power_state):
    mqtt_interface.send_mqtt_message("dcc_power_events", 0, data={"dccpower": power_state}, retain=False, 
                    log_message=f"Loco Control: Publishing DCC Power message to broker: Power={power_state}")
    return()

#------------------------------------------------------------------------------
# API function to request a loco session (returns session ID or 0 if unsuccessful)
#------------------------------------------------------------------------------

def request_loco_session(dcc_address:int, callback):
    global locomotive_sessions
    def response_received(): return(locomotive_sessions[str(dcc_address)]["sessionid"] > 0)
    if not isinstance(dcc_address, int) or dcc_address < 1 or dcc_address > 10239:
        logging.error(f"Loco Control: request_loco_session - Invalid DCC Address {dcc_address} - must be an int (1-10239)")
    else:
        logging.debug(f"Loco Control: Requesting Loco Session for DCC address {dcc_address}")
        session_acknowledgement_callbacks[dcc_address] = callback
        # Send the command either to the local SPROG interface or the remote node. If sending to
        # the remote node, we wait for the callback - otherwise schedule the callback immediately.
        # To Request a session we send the DCC Address with a Session ID of zero
        if publish_dcc_locomotive_commands_to_mqtt_broker:
            mqtt_message = {"dccaddress": dcc_address, "sessionid": 0}
            send_mqtt_dcc_locomotive_control_event(mqtt_message)
        else:
            session_id = pi_sprog_interface.request_loco_session(dcc_address)
            common.root_window.after(0, lambda:callback(dcc_address, session_id))
    return()

#------------------------------------------------------------------------------
# API function to release a loco session (local or remote)
#------------------------------------------------------------------------------

def release_loco_session(session_id:int):
    global locomotive_sessions
    if not isinstance(session_id, int):
        logging.error(f"Loco Control: release_loco_session - Invalid Session ID {session_id} - must be an int")
    else:
        logging.debug(f"Loco Control: Releasing Loco Session {session_id}")
        # Send the command either to the local SPROG interface or the remote node.
        # To Release a session we send the Session ID with DCC address of zero
        if publish_dcc_locomotive_commands_to_mqtt_broker:
            mqtt_message = {"dccaddress": 0, "sessionid": session_id}
            send_mqtt_dcc_locomotive_control_event(mqtt_message)
        else:
            pi_sprog_interface.release_loco_session(session_id)
    return()

#------------------------------------------------------------------------------
# API function to set loco speed and direction (local or remote)
#------------------------------------------------------------------------------

def set_loco_speed_and_direction(session_id:int, speed:int, forward:bool, allow_emergency_stop:bool=False):
    if not isinstance(session_id, int):
        logging.error(f"Loco Control: set_loco_speed_and_direction - Invalid Session ID {session_id} - must be an int")
    elif not isinstance(speed, int) or speed < 0 or speed > 127:
        logging.error(f"Loco Control: set_loco_speed_and_direction - Invalid speed for session {session_id} - must be an int (0-127)")
    else:
        # Inhibit the Emergency Stop (unless overridden in the function call)
        if not allow_emergency_stop and speed == 1: speed = 0
        if publish_dcc_locomotive_commands_to_mqtt_broker:
            mqtt_message = {"dccaddress": 0, "sessionid": session_id, "speed": speed, "direction": forward}
            send_mqtt_dcc_locomotive_control_event(mqtt_message)
        else:
            pi_sprog_interface.set_loco_speed_and_direction(session_id, speed, forward)
    return()

def send_emergency_stop(session_id:int):
    set_loco_speed_and_direction(session_id, speed=1, forward=True, allow_emergency_stop=True)
    return()

#------------------------------------------------------------------------------
# API function to set a loco function (local or remote)
#------------------------------------------------------------------------------

def set_loco_function(session_id:int, function_id:int, state:bool):
    if not isinstance(session_id, int):
        logging.error(f"Pi-SPROG: set_loco_function - Invalid Session ID {session_id} - must be an int")
    elif not isinstance(function_id, int) or function_id < 0 or function_id > 28:
        logging.error(f"Pi-SPROG: set_loco_function - Invalid function ID {function_id} for session {session_id} - must be 0-28")
    else:
        if publish_dcc_locomotive_commands_to_mqtt_broker:
            mqtt_message = {"dccaddress": 0, "sessionid": session_id, "functionid": function_id, "functionstate": state}
            send_mqtt_dcc_locomotive_control_event(mqtt_message)
        else:
            pi_sprog_interface.set_loco_function(session_id, function_id, state)

#----------------------------------------------------------------------------------------------------
# API function to reset the published/subscribed DCC loco control feeds. This function is called by
# the editor on 'Apply' of the MQTT pub/sub configuration prior to applying the new configuration
# via the 'subscribe_to_dcc_command_feed' & 'set_node_to_publish_dcc_commands' functions.
#----------------------------------------------------------------------------------------------------

def reset_dcc_locomotive_mqtt_configuration():
    global publish_dcc_locomotive_commands_to_mqtt_broker
    logging.debug("Loco Control: Resetting MQTT publish and subscribe configuration")
    publish_dcc_locomotive_commands_to_mqtt_broker = False
    mqtt_interface.unsubscribe_from_message_type("dcc_power_events")
    mqtt_interface.unsubscribe_from_message_type("dcc_acknowledge_events")
    mqtt_interface.unsubscribe_from_message_type("dcc_locomotive_control_events")
    return()

#----------------------------------------------------------------------------------------------------
# API Function to set this Signalling node to publish all DCC LOCO commands to remote MQTT
# nodes. This function is called by the editor on 'Apply' of the MQTT pub/sub configuration.
#----------------------------------------------------------------------------------------------------

def set_node_to_publish_dcc_locomotive_commands(sprog_node:str):
    global publish_dcc_locomotive_commands_to_mqtt_broker
    if len(sprog_node) > 0:
        logging.debug(f"Loco Control: Configuring Application to publish Loco Control Commands to Node {sprog_node}")
        # If this node is publishing its DCC loco control command feed (to a remote SPROG node)
        # Then we need to know the current DCC power state (on or OFF) of the remote node.
        # We use a global subscription on the assumption there is only one SPROG node on
        # the network that is subscribing to dcc locomotive command feeds
        mqtt_interface.subscribe_to_mqtt_messages("dcc_power_events", sprog_node, 0, handle_mqtt_dcc_power_event)
        mqtt_interface.subscribe_to_mqtt_messages("dcc_acknowledge_events", sprog_node, 0, handle_mqtt_dcc_acknowledge_event)
    publish_dcc_locomotive_commands_to_mqtt_broker = len(sprog_node) > 0
    return()

#----------------------------------------------------------------------------------------------------
# API Function to "subscribe" to the published DCC command feed from other remote MQTT nodes
# This function is called by the editor on "Apply' of the MQTT pub/sub configuration.
#----------------------------------------------------------------------------------------------------

def subscribe_to_dcc_locomotive_command_feed(*nodes:str):
    for node in nodes:
        mqtt_interface.subscribe_to_mqtt_messages("dcc_locomotive_control_events", node, 0, handle_mqtt_dcc_locomotive_control_event)
    # If this node is subscribing to one or more DCC loco control command feeds (from other nodes)
    # Then the other nodes need to know the current DCC power state (on or OFF). We therefore subscribe
    # to updates from the local SPROG interface with a callback to transmit updates via the network
    if len(nodes) > 0: pi_sprog_interface.subscribe_to_local_dcc_power_updates(send_dcc_power_status_update_events)
    else: pi_sprog_interface.unsubscribe_from_local_dcc_power_updates(send_dcc_power_status_update_events)
    return() 


#####################################################################################################
