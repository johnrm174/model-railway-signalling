# model-railway-signalling - Public API

Although the application is primarily designed for use with the SPROG DCC Programmer Controller
(for control of the signals and points out on the layout) and the RPi GPIO interface (for detecting
train movements as signals are passed), the MQTT networking functions supported by the application
can also be exploited by those wishing to develop their own layout interface applications.

The public API comprises:

* Subscribing to the published DCC command feed from the Model Railway Signalling application
* Publishing GPIO sensor triggered events to the Model Railway Signalling application

To use this API you will need to:
* Stand up a MQTT message broker (or use a broker out on the internet)
* Connect the Model Railway Signalling Applcation to the MQTT Broker
* Configure Model Railway Signalling to 'publish' the DCC command feed to your application
* Configure Model Railway Signalling to 'subscribe' to any 'GPIO-Sensors' from your application

The following example configuration uses the Python PAHO MQTT client, but the configuration
of other Languages / MQTT Clients should be broadly similar (read the docs!)

## Subscribing to the DCC Command Feed in your application

The Format of the DCC command feed Subscription Topic is: 
<pre>
dcc_accessory_short_events/network_identifier/node_identifier-0/+
</pre>
* The network_identifier is the name you have given to your signalling network.
* The node_identifier will be the name you have given to the main Model Railway Signalling node.

As an example, for a signalling network name of "layout1" and a node name of "box1", the subscription would be:
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
