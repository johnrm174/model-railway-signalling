# model-railway-signalling - Public API

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

The format of the DCC command feed 'Topic' is: 
<pre>
dcc_accessory_short_events/network_identifier/node_identifier-0/+
</pre>
* The network_identifier is the name you have given to your signalling network.
* The node_identifier will be the name you have given to the main Model Railway Signalling node.

As an example, for a signalling network name of "layout1" and the a node name (for the main Model Railway 
Signalling application) of "box1", the subscription would be:
<pre>
mqtt_client.subscribe("dcc_accessory_short_events/layout1/box1-0/+")
</pre>

## Decoding the DCC Command Feed in your application

Once subscribed, the paho MQTT client will make a callback for every message received (the following
example assumes we have registered this callback as our 'on_message' function).

To decode the DCC command you just need to unpack the json message (to convert this into a python dict in order
to access the individual elements). Note that your application should always handle the case of empty payloads 
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

The format of the GPIO Sensor Event 'Topic' is: 
<pre>
gpio_sensor_event/network_identifier/item_identifier 
</pre>
* The network_identifier is the name you have given to your signalling network.
* The item_identifier is the unique identifier for each 'GPIO sensor' you want to 'publish' in the format 'node_identifier-sensor_id'

As an example, for a signalling network name of "layout1" and a node name (for the node running 
your layout interfacing application) of "box2", trigger events for gpio sensor "3" would be
published to the following topic:
<pre>
"gpio_sensor_event/layout1/box2-3"
</pre>

To encode a GPIO sensor event you just need to include the item-identifier in a json message and
'publish' this to the MQTT broker on the appropriate topic. Note that as these messages relate to 
transitory events, they should be published to the broker as 'non-retained' messages.
<pre>
def publish_gpio_sensor_event(network_identifier:str, node_identifier:str, sensor_id:int):
    item_identifier = node_identifier+"-"+str(sensor_id)
    topic = "gpio_sensor_event/"+network_identifier+"/"+item_identifier
    payload = json.dumps( {"sourceidentifier": item_identifier } )
    mqtt_client.publish(topic, payload, retain=False, qos=1)
</pre>

Note that it will be the responsibility of your application to implement any 'debounce' or 'timeouts' that
may be required for whatever mechanisms you choose to use for train detection. Your application should
only ever publish a single GPIO sensor event to the main Model Railway Signalling application when triggered.