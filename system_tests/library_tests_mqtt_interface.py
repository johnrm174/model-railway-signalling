#-----------------------------------------------------------------------------------
# Library tests to check the basic function of all library object object functions
# Calls the library functions directly rather than using the sysytem_test_harness
#-----------------------------------------------------------------------------------

import time
import logging

import system_test_harness
from model_railway_signals.library import mqtt_interface

#---------------------------------------------------------------------------------------------------------
# Test MQTT interface
#---------------------------------------------------------------------------------------------------------

def shutdown_callback():
    print("Library Tests - MQTT shutdown callback received")

def message_callback(message):
    print("Library Tests - MQTT message received: "+str(message))

mqtt_connected = False

def mqtt_status_callback(connection_status:bool):
    global mqtt_connected
    mqtt_connected = connection_status
    print("Library Tests - MQTT connection_status is: " + str(connection_status))

def mqtt_configuration_tests():
    system_test_harness.reset_log_counters()
    # Test all functions - including negative tests for parameter validation
    print("Library Tests - split_remote_item_identifier - No errors or warnings")
    assert mqtt_interface.split_remote_item_identifier(123) is None
    assert mqtt_interface.split_remote_item_identifier("box111") is None
    assert mqtt_interface.split_remote_item_identifier("box1-abc") is None
    assert mqtt_interface.split_remote_item_identifier("box1-0") is None
    assert mqtt_interface.split_remote_item_identifier("box1-999") == ["box1", 999]
    assert mqtt_interface.split_remote_item_identifier("box1-99") == ["box1", 99]
    print("Library Tests - configure_mqtt_client - 5 Errors should be generated")
    mqtt_interface.configure_mqtt_client(100,"node1", False, False, False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1",100, False, False, False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", "False", False, False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", False, "False", False, shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", False, False, "False", shutdown_callback) # error
    mqtt_interface.configure_mqtt_client("network1","node1", True, True, True, shutdown_callback) # Success
    print("Library Tests - mqtt_broker_connect - 4 Errors should be generated")
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect(127,1883, mqtt_status_callback) # Fail
    time.sleep(0.2)
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect("127.0.0.1","1883", mqtt_status_callback) # Fail
    time.sleep(0.2)
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, 100, "password1") # Fail
    time.sleep(0.2)
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, "user1", 100) # Fail
    time.sleep(0.2)
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, "user1", "password1") # success
    time.sleep(2.0)
    assert mqtt_connected
    print("Library Tests - mqtt_broker_connect (to force a disconnect and then re-connect) - No errors or warnings")
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, "user1", "password1") # success
    time.sleep(4.0)
    assert mqtt_connected
    print("Library Tests - mqtt_broker_disconnect followed by mqtt_broker_connect - No errors or warnings")
    mqtt_interface.mqtt_broker_disconnect()
    time.sleep(1.0)
    assert not mqtt_connected
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, "user1", "password1") # success
    time.sleep(2.0)
    assert mqtt_connected
    print("Library Tests - get_mqtt_node_status (connected and disconnected)")
    connection_status1 = mqtt_interface.get_mqtt_node_status()
    print("Library Tests - get_mqtt_node_status - Reported status is: "+str(connection_status1))
    time.sleep(5.0)  # Heartbeat frequency is 5 seconds
    connection_status2 = mqtt_interface.get_mqtt_node_status()
    print("Library Tests - get_mqtt_node_status - Reported status is: "+str(connection_status2))
    assert connection_status1 != connection_status2
    mqtt_interface.mqtt_broker_disconnect()
    time.sleep(5.0)   # Heartbeat frequency is 5 seconds
    connection_status3 = mqtt_interface.get_mqtt_node_status()
    print("Library Tests - get_mqtt_node_status - Reported status is: "+str(connection_status3))
    assert connection_status2 == connection_status3
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(9)
    system_test_harness.assert_warning_logs_generated(0)    
    
def mqtt_messaging_tests():
    system_test_harness.reset_log_counters()
    mqtt_interface.configure_mqtt_client("network1","node1", True, True, True, shutdown_callback)
    print("Library Tests - subscribe_to_mqtt_messages whilst disconnected - No errors or warnings")
    assert not mqtt_connected
    assert len(mqtt_interface.node_config["list_of_subscribed_topics"]) == 0
    mqtt_interface.subscribe_to_mqtt_messages("test_messages_1", "node1", 1, message_callback)
    print("Library Tests - subscribe_to_mqtt_messages whilst connected - No errors or warnings")
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, "user1", "password1")
    time.sleep(2.0)
    assert mqtt_connected
    mqtt_interface.subscribe_to_mqtt_messages("test_messages_2", "node1", 1, message_callback, subtopics=True)
    assert len(mqtt_interface.node_config["list_of_subscribed_topics"]) == 2
    print("Library Tests - resubscribe on disconnect/reconnect - 1 Info and 7 Debug messages will be generated")
    mqtt_interface.mqtt_broker_disconnect()
    time.sleep(2.0)
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    mqtt_interface.mqtt_broker_connect("127.0.0.1",1883, mqtt_status_callback, "user1", "password1") # success
    time.sleep(2.0)
    assert mqtt_connected
    print("Library Tests - send_mqtt_message - Tests 1 - 12 Debug messages will be generated")
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":12, "data2":"abc"}, log_message="LOG MESSAGE 1")
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":34, "data2":"def"}, log_message="LOG MESSAGE 2")
    mqtt_interface.send_mqtt_message("test_messages_2", 1, {"data1":56, "data2":"ghi"}, log_message="LOG MESSAGE 3", subtopic="sub1")
    mqtt_interface.send_mqtt_message("test_messages_2", 1, {"data1":78, "data2":"jkl"}, log_message="LOG MESSAGE 4", subtopic="sub2")
    time.sleep(1.0)
    logging.getLogger().setLevel(logging.WARNING) #################################################################################
    print("Library Tests - unsubscribe_from_message_type")
    mqtt_interface.unsubscribe_from_message_type("test_messages_1")
    assert len(mqtt_interface.node_config["list_of_subscribed_topics"]) == 1
    print("Library Tests - send_mqtt_message - Tests 2 - 10 Debug messages will be generated")
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":12, "data2":"abc"}, log_message="LOG MESSAGE 1")
    mqtt_interface.send_mqtt_message("test_messages_1", 1, {"data1":34, "data2":"def"}, log_message="LOG MESSAGE 2")
    mqtt_interface.send_mqtt_message("test_messages_2", 1, {"data1":56, "data2":"ghi"}, log_message="LOG MESSAGE 3", subtopic="sub1")
    mqtt_interface.send_mqtt_message("test_messages_2", 1, {"data1":78, "data2":"jkl"}, log_message="LOG MESSAGE 4", subtopic="sub2")
    time.sleep(1.0)
    logging.getLogger().setLevel(logging.WARNING) #################################################################################
    print("Library Tests - mqtt_publish_shutdown_message - 3 Debug and 1 Info message will be generated")
    mqtt_interface.configure_mqtt_client("network1","node1", True, True, True, shutdown_callback) # Shutdown processed
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    mqtt_interface.mqtt_publish_shutdown_message()
    time.sleep(1.0)
    logging.getLogger().setLevel(logging.WARNING) #################################################################################
    mqtt_interface.configure_mqtt_client("network1","node1", True, True, True) # No shutdown message processed)
    logging.getLogger().setLevel(logging.DEBUG) #################################################################################
    mqtt_interface.mqtt_publish_shutdown_message()
    time.sleep(1.0)
    logging.getLogger().setLevel(logging.WARNING) #################################################################################
    # Clean up
    mqtt_interface.unsubscribe_from_message_type("test_messages_2")
    assert len(mqtt_interface.node_config["list_of_subscribed_topics"]) == 0
    mqtt_interface.mqtt_broker_disconnect() 
    time.sleep(1.0)
    # Check the total number of Log Messages Generated
    system_test_harness.assert_error_logs_generated(0)
    system_test_harness.assert_warning_logs_generated(0)
    system_test_harness.assert_debug_logs_generated(30)
    system_test_harness.assert_info_logs_generated(2)

#---------------------------------------------------------------------------------------------------------
# Run all library Tests
#---------------------------------------------------------------------------------------------------------

def run_all_tests():
    print("----------------------------------------------------------------------------------------")
    print("Library Tests - MQTT Interface Tests")
    print("----------------------------------------------------------------------------------------")
    # The only function calls that result in a Tkinter function call are 'mqtt_broker_connect'
    # and 'mqtt_broker_disconnect' (where it updates the MQTT Connection state indicator in the menubar)
    # We therefore 'take the risk' and run everything in the main Test Harness Thread
    mqtt_configuration_tests()
    mqtt_messaging_tests()
    system_test_harness.report_results()
    print("")
    
if __name__ == "__main__":
    system_test_harness.start_application(run_all_tests)

###############################################################################################################################
