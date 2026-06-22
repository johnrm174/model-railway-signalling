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
#   set_node_to_publish_dcc_locomotive_commands(publish:bool, destination_node) - set node to publish loco commands
#           If Publish=True then all DCC locomotive commands will then be published to the MQTT broker (not the local SPROG )
#           Similarly, requests for DC power on/off (from the throttles) will be sent to the MQTT Broker (not the local SPROG)
#           The destination node is required to subscribe to loco command acknowledgement messages and DCC power updates
#
#   subscribe_to_dcc_locomotive_command_feed(nodes) - subscribe to DCC locomotive commands from other nodes
#           All received DCC locomotive commands will then be automatically forwarded to the local SPROG interface.
#           The SPROG DCC Power state and all acknowledgement messages will be sent to the broker
#
#   subscribe_to_dcc_power_updates(callback) - subscribe to DCC power state
#   unsubscribe_from_dcc_power_updates(callback) - unsubscribe from DCC power state
#        Note that these functions will interact with either the local of remote SPROG interface
#        depending on whether the publish_dcc_locomotive_commands_to_mqtt_broker flag is set
#
#   request_track_power_on() - Request DCC Track Power On
#   request_track_power_off() - Request DCC Track Power Off
#
#   request_loco_session(dcc_address) - generates a loco session and returns session_id
#   release_loco_session(session_id) - releases the locomotive session
#   set_loco_speed_and_direction(session_id:int, speed:int, forward:bool)
#   send_emergency_stop(session_id) - Emergency Stops the loco
#   set_loco_function(session_id:int, function_id:int, state:bool)
#
# Internal API - classes and functions (used by the other library modules):
#
#   handle_mqtt_dcc_locomotive_control_response(message)
#   handle_mqtt_dcc_locomotive_control_request(message)
#----------------------------------------------------------------------------------------------------

import logging

from . import pi_sprog_interface
from . import mqtt_interface
from . import common

#----------------------------------------------------------------------------------------------------
# Global definitions
#----------------------------------------------------------------------------------------------------

# Define the Flag to control whether DCC Commands are published to the MQTT Broker
publish_dcc_locomotive_commands_to_mqtt_broker = False
# Define the flag to control whether we need to send a DCC power message on broker connect
notify_other_network_clients_of_dcc_power_updates = False
# Other global variables we need to track
session_acknowledgement_callbacks = {}
registered_dcc_power_state_callbacks = []
remote_dcc_power_is_on = None   # Unknown
local_dcc_power_is_on = None   # Unknown

#----------------------------------------------------------------------------------------------------
# API Functions to register/unregister for DCC power status updates. This will subscribe to either
# local SPROG power state updates or remote SPROG power state updates depending on whether this
# Node is configured to be a remote throttle (publish_dcc_locomotive_commands_to_mqtt_broker=True)
#----------------------------------------------------------------------------------------------------

def subscribe_to_dcc_power_updates(callback):
    global registered_dcc_power_state_callbacks
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
        # an immediate callback to let the client know the current power state.
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
# API Functions to request DCC power ON/OFF. These requests will be sent to either the local
# SPROG or the remote SPROG power sdepending on whether this Node is configured to be a remote
# throttle (publish_dcc_locomotive_commands_to_mqtt_broker=True) or a local throttle
#----------------------------------------------------------------------------------------------------

def request_track_power_on():
    # Send the command either to the local SPROG interface or the remote SPROG node. We will either
    # get a callback from the local SPROG or an acknowledgement message from the remote node
    if publish_dcc_locomotive_commands_to_mqtt_broker:
        mqtt_message = {"requestdccpower": True}
        mqtt_interface.send_mqtt_message("dcc_locomotive_control_commands", 0, data=mqtt_message, retain=True,
                log_message=f"Loco Control: Publishing loco control message to broker :{mqtt_message}")
    else:
        pi_sprog_interface.request_dcc_power_on()
    return()

def request_track_power_off():
    # Send the command either to the local SPROG interface or the remote SPROG node. We will either
    # get a callback from the local SPROG or an acknowledgement message from the remote node
    if publish_dcc_locomotive_commands_to_mqtt_broker:
        mqtt_message = {"requestdccpower": False}
        mqtt_interface.send_mqtt_message("dcc_locomotive_control_commands", 0, data=mqtt_message, retain=True,
                log_message=f"Loco Control: Publishing loco control message to broker :{mqtt_message}")
    else:
        pi_sprog_interface.request_dcc_power_off()
    return()

#------------------------------------------------------------------------------
# API function to request a loco session (returns session ID or 0 if unsuccessful)
#------------------------------------------------------------------------------

def request_loco_session(dcc_address:int, callback):
    global locomotive_sessions
    if not isinstance(dcc_address, int) or dcc_address < 1 or dcc_address > 10239:
        logging.error(f"Loco Control: request_loco_session - Invalid DCC Address {dcc_address} - must be an int (1-10239)")
    else:
        logging.debug(f"Loco Control: Requesting Loco Session for DCC address {dcc_address}")
        # Store the callback for session acknowledgement
        session_acknowledgement_callbacks[dcc_address] = callback
        # Send the command either to the local SPROG interface or the remote SPROG node. If sending
        # to the remote node, we wait for the callback - otherwise schedule the callback immediately
        # as the SPROG interface call waits for the response (with an appropriate timeout)
        if publish_dcc_locomotive_commands_to_mqtt_broker:
            # To Request a remote session we send the DCC Address with a Session ID of zero
            mqtt_message = {"dccaddress": dcc_address, "sessionid": 0}
            mqtt_interface.send_mqtt_message("dcc_locomotive_control_commands", 0, data=mqtt_message, retain=True,
                    log_message=f"Loco Control: Publishing loco control message to broker :{mqtt_message}")
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
        # Send the command either to the local SPROG interface or the remote SPROG node.
        if publish_dcc_locomotive_commands_to_mqtt_broker:
            # To Release a remote session we send the Session ID with DCC address of zero.
            # There is no callback here - it will either happen or it won't
            mqtt_message = {"dccaddress": 0, "sessionid": session_id}
            mqtt_interface.send_mqtt_message("dcc_locomotive_control_commands", 0, data=mqtt_message, retain=True,
                    log_message=f"Loco Control: Publishing loco control message to broker :{mqtt_message}")
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
        # Publish the Speed/Direction change message to either the local SPROG or the remote SPROG
        if publish_dcc_locomotive_commands_to_mqtt_broker:
            # Speed/Direction messages include the Session ID, Speed value and Direction Flag
            mqtt_message = {"sessionid": session_id, "speed": speed, "direction": forward}
            mqtt_interface.send_mqtt_message("dcc_locomotive_control_commands", 0, data=mqtt_message, retain=True,
                    log_message=f"Loco Control: Publishing loco control message to broker :{mqtt_message}")
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
        # Publish the Loco Function change message to either the local SPROG or the remote SPROG
        if publish_dcc_locomotive_commands_to_mqtt_broker:
            # Loco Function messages incluse the Session ID, Function ID and Function state Flag
            mqtt_message = {"sessionid": session_id, "functionid": function_id, "functionstate": state}
            mqtt_interface.send_mqtt_message("dcc_locomotive_control_commands", 0, data=mqtt_message, retain=True,
                    log_message=f"Loco Control: Publishing loco control message to broker :{mqtt_message}")
        else:
            pi_sprog_interface.set_loco_function(session_id, function_id, state)
    return()

#----------------------------------------------------------------------------------------------------
# Callback for handling DCC session responses received from the SPROG Node
# in response to a session request from a throttle running on this machine.
# We make the callback to update the client on the status of the session request
#----------------------------------------------------------------------------------------------------

def handle_mqtt_dcc_locomotive_control_response(message):
    global remote_dcc_power_is_on
    if "sourceidentifier" not in message.keys():
        logging.error (f"Loco Control: Unhandled MQTT Response Message - {message}")
    else:
        # All Messages include the following mandatory elements
        source_node = message["sourceidentifier"]
        # The following elements are optional - if not present then the values will be set to none
        dcc_address = message.get("dccaddress")
        session_id = message.get("sessionid")
        dcc_power_state = message.get("dccpowerstate")
        # Handle a DCC Power is ON or OFF message
        if dcc_power_state is not None:
            logging.debug(f"Loco Control: Received DCC Power State medssage from {source_node} "
                               +f" - DCC Power state: {dcc_power_state}")
            remote_dcc_power_is_on = dcc_power_state
            for power_status_changed_callback in registered_dcc_power_state_callbacks:
                power_status_changed_callback(dcc_power_state)
        # Handle a Loco Session acknowledgement message
        elif dcc_address is not None and session_id is not None and dcc_address in session_acknowledgement_callbacks.keys():
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

def handle_mqtt_dcc_locomotive_control_command(message):
    if "sourceidentifier" not in message.keys():
        logging.error ("Loco Control: Unhandled MQTT Control Message - "+str(message))
    else:
        # All Messages include the following mandatory elements
        source_node = message["sourceidentifier"]
        # The following elements are optional - if not present then the values will be set to none
        dcc_address = message.get("dccaddress")
        session_id = message.get("sessionid")
        loco_speed = message.get("speed")
        direction = message.get("direction")
        function_id = message.get("functionid")
        func_state = message.get("functionstate")
        request_dcc_power = message.get("requestdccpower")
        # Handle speed/direction commands from a remote throttle
        if session_id is not None and loco_speed is not None and direction is not None:
            logging.debug (f"Loco Control: Received message for Session {session_id} on {source_node}: speed={loco_speed}, forward={direction}")
            pi_sprog_interface.set_loco_speed_and_direction(session_id, loco_speed, direction)
        # Handle loco function commands from a remote throttle
        elif session_id is not None and function_id is not None and func_state is not None:
            logging.debug (f"Loco Control: Received message for Session {session_id} on {source_node}: function={function_id}, state={func_state}")
            pi_sprog_interface.set_loco_function(session_id, function_id, func_state)
        # Handle a DCC power On Request - No acknowledgement required (made via a seperate callback)
        elif request_dcc_power is not None and request_dcc_power:
            logging.debug (f"Loco Control: Received Request DCC Power ON message from {source_node}")
            pi_sprog_interface.request_dcc_power_on()
        # Handle a DCC power Off Request  - No acknowledgement required (made via a seperate callback)
        elif request_dcc_power is not None and not request_dcc_power:
            logging.debug (f"Loco Control: Received Request DCC Power OFF message from {source_node}")
            pi_sprog_interface.request_dcc_power_off()
        # Handle loco session request from a remote throttle
        elif dcc_address is not None and dcc_address > 0 and session_id is not None and session_id == 0:
            logging.debug (f"Loco Control: Received Session Request message for DCC Address {dcc_address} from {source_node}")
            loco_session = pi_sprog_interface.request_loco_session(dcc_address)
            # Acknowledge the session back to the client (session ID will be zero if unsuccessful)
            mqtt_interface.send_mqtt_message("dcc_locomotive_control_responses", 0, retain=True,
                        data={"dccaddress": dcc_address, "sessionid": loco_session},
                        log_message=f"Loco Control: Publishing acknowledgement message to broker - Session ID is {loco_session}")
        # Handle loco session release request from a remote node
        elif dcc_address is not None and dcc_address == 0 and session_id is not None and session_id > 0:
            logging.debug (f"Loco Control: Received Session Release message for Session {session_id} from {source_node}")
            pi_sprog_interface.release_loco_session(session_id)
    return()

#----------------------------------------------------------------------------------------------------
# API function to reset the published/subscribed DCC loco control feeds. This function is called by
# the editor on 'Apply' of the MQTT pub/sub configuration prior to applying the new configuration
# via the 'subscribe_to_dcc_command_feed' & 'set_node_to_publish_dcc_commands' functions.
#----------------------------------------------------------------------------------------------------

def reset_dcc_locomotive_mqtt_configuration():
    global publish_dcc_locomotive_commands_to_mqtt_broker
    global session_acknowledgement_callbacks
    logging.debug("Loco Control: Resetting MQTT publish and subscribe configuration")
    publish_dcc_locomotive_commands_to_mqtt_broker = False
    mqtt_interface.unsubscribe_from_message_type("dcc_locomotive_control_commands")
    mqtt_interface.unsubscribe_from_message_type("dcc_locomotive_control_responses")
    session_acknowledgement_callbacks.clear()
    return()

#----------------------------------------------------------------------------------------------------
# API Function to set this Signalling node to publish all DCC LOCOMOTIVE commands to remote MQTT
# nodes. This function is called by the editor on 'Apply' of the MQTT pub/sub configuration.
# Note that this node also needs to subscribe to the DCC power state of the remote node
# and all DCC loco control acknowledgement messages (e.g. request session)
#----------------------------------------------------------------------------------------------------

def set_node_to_publish_dcc_locomotive_commands(publish_dcc_commands:bool, destination_node:str):
    global publish_dcc_locomotive_commands_to_mqtt_broker
    publish_dcc_locomotive_commands_to_mqtt_broker = publish_dcc_commands
    if publish_dcc_locomotive_commands_to_mqtt_broker:
        logging.debug(f"Loco Control: Configuring Application to publish Loco Control Commands to Node {destination_node}")
        # If this node is publishing its DCC loco control command feed (to a remote SPROG node)
        # Then we need to know the current DCC power state (on or OFF) of the remote node.
        # We use a global subscription on the assumption there is only one SPROG node on
        # the network that is subscribing to dcc locomotive command feeds
        mqtt_interface.subscribe_to_mqtt_messages("dcc_locomotive_control_responses", destination_node, 0, handle_mqtt_dcc_locomotive_control_response)
    return()

#----------------------------------------------------------------------------------------------------
# API Function to "subscribe" to the published DCC loco command feed (from other MQTT nodes)
# This function is called by the editor on "Apply' of the MQTT pub/sub configuration.
# Note that we need to configure 'this' node to publish the local SPROG DCC power state
# back to the remote node(s) that are sending the DCC loco commands. This needs to be done
# immediately on broker connect and then every time the power state changes
#----------------------------------------------------------------------------------------------------

def send_local_dcc_power_state_on_broker_connect():
    if notify_other_network_clients_of_dcc_power_updates:
        local_dcc_power_state_updated(local_dcc_power_is_on)

def local_dcc_power_state_updated(power_state):
    global local_dcc_power_is_on
    local_dcc_power_is_on = power_state
    mqtt_interface.send_mqtt_message("dcc_locomotive_control_responses", 0, data={"dccpowerstate": power_state}, retain=True,
                log_message=f"Loco Control: Publishing DCC Power state response to broker: Power={power_state}")

def subscribe_to_dcc_locomotive_command_feed(*nodes:str):
    global notify_other_network_clients_of_dcc_power_updates
    for node in nodes:
        mqtt_interface.subscribe_to_mqtt_messages("dcc_locomotive_control_commands", node, 0, handle_mqtt_dcc_locomotive_control_command)
    # If this node is subscribing to one or more DCC loco control command feeds (from other nodes)
    # Then the other nodes need to know the current DCC power state (on or OFF). We therefore subscribe
    # to updates from the local SPROG interface with a callback to transmit updates via the network
    if len(nodes) > 0:
        notify_other_network_clients_of_dcc_power_updates = True
        pi_sprog_interface.subscribe_to_local_dcc_power_updates(local_dcc_power_state_updated)
    else:
        notify_other_network_clients_of_dcc_power_updates = False
        pi_sprog_interface.unsubscribe_from_local_dcc_power_updates(local_dcc_power_state_updated)
    return() 

#####################################################################################################
