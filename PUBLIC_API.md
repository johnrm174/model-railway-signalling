# model-railway-signalling - Public API

NOTE THE CHANGE TO HOW GPIO SENSORS ARE HANDLED FROM RELEASE 5.1.0 ONWARDS (see below)

Although the application is primarily designed for use with the SPROG DCC Programmer Controller
(for control of the signals and points out on the layout) and the RPi GPIO interface (for detecting
train movements as signals are passed), the MQTT networking functions supported by the application
can also be exploited by those wishing to develop their own layout interface applications.

The public API comprises:

* Subscribing to the published DCC command feed from the Model Railway Signalling application.
* Publishing GPIO sensor triggered events to the Model Railway Signalling application.

To use this API you will need to:
* Stand up a MQTT message broker (or use a broker out on the internet).
* Connect the Model Railway Signalling Applcation to the MQTT Broker.
* Configure Model Railway Signalling to 'publish' the DCC command feed to your application.
* Configure Model Railway Signalling to 'subscribe' to any 'GPIO-Sensors' from your application.

The following example configurations use the Python PAHO MQTT client, but the configuration
for other Languages / MQTT Clients should be broadly similar - if in doubt read the docs!

## Subscribing to the DCC Command Feed in your application

The format of the DCC command feed subscription 'Topic' is: 
<pre>
dcc_accessory_short_events/network_identifier/node_identifier-0/+
</pre>
* The network_identifier is the name you have given to your signalling network.
* The node_identifier will be the name you have given to the main Model Railway Signalling node.

As an example, for a signalling network name of "layout1" and a node name (for the main Model Railway 
Signalling application) of "box1", the subscription would be:
<pre>
mqtt_client.subscribe("dcc_accessory_short_events/layout1/box1-0/+")
</pre>

## Decoding the DCC Command Feed in your application

Once subscribed, the paho MQTT client will make a callback for every message received (the following
example assumes we have registered this callback as our 'on_message' function).

To decode the DCC command you just need to convert the json message into a python dict to access the
individual message elements. Note that your application should always handle the case of empty payloads 
as the Model Railway Signalling application will publish 'Null' messages to this topic on shutdown.
<pre>
def on_message(mqtt_client, userdata, message):
    if message.topic.startswith("dcc_accessory_short_events") and message.payload:
        unpacked_json = json.loads(message.payload)
        source_node = unpacked_json["sourceidentifier"]   # String - e.g. "box1-0"
        dcc_address = unpacked_json["dccaddress"]         # Integer (between 1 and 2047)
        dcc_state = unpacked_json["dccstate"]             # boolean (True or False)
</pre>

## Publishing GPIO sensor events from your application

Each individual GPIO sensor should be published to its own 'Topic'. The format of a GPIO Sensor Event topic is: 
<pre>
gpio_sensor_event/network_identifier/item_identifier 
</pre>
* The network_identifier is the name you have given to your signalling network.
* The item_identifier is the unique identifier for each individual GPIO sensor in the format 'node_identifier-sensor_id'

As an example, for a signalling network name of "layout1" and a node name (for the node running 
your layout interfacing application) of "box2", GPIO sensor events for gpio sensor "3" would be
published to the following topic:
<pre>
"gpio_sensor_event/layout1/box2-3"
</pre>

NOTE THAT THE STATE OF THE GPIO SENSOR SHOULD NOW BE INCLUDED IN THE PAYLOAD FROM RELEASE 5.1.0 ONWARDS
IF YOU WANT TO USE 'TRACK CIRCUIT' TYPE TRAIN DETECTION FOR TRACK SECTIONS. YOU SHOULD THEREFORE UPDATE
YOUR APPLICATION TO PUBLISH BOTH TRIGGERED AND RELEASE EVENTS TO THE TOPIC.

To encode a GPIO sensor event you just need to include the item-identifier and the state of the GPIO sensor in
a json message and 'publish' this to the MQTT broker on the appropriate topic. Note that as the application can
now support 'track circuit' type train detection to drive track occupancy (as an option to using event-type
sensors to 'pass' trains from one Track Section to another) you should send both 'triggered' and 'released'
events as appropriate, and they should be published to the broker as 'retained' messages so the application
will always pick up the latest state (True for triggered, False for released):
<pre>
def publish_gpio_sensor_event(network_identifier:str, node_identifier:str, sensor_id:int, sensor_state:bool):
    item_identifier = node_identifier+"-"+str(sensor_id)
    topic = "gpio_sensor_event/"+network_identifier+"/"+item_identifier
    payload = json.dumps( {"sourceidentifier": item_identifier, "state": sensor_state} )
    mqtt_client.publish(topic, payload, retain=True, qos=1)
</pre>

Note that it will be the responsibility of your application to implement any 'debounce' or 'timeouts' that
may be required for whatever mechanisms you choose to use for train detection.
