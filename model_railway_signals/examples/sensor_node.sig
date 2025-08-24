{
    "buttons": {},
    "information": "Model Railway Signalling Configuration File",
    "instruments": {},
    "levers": {},
    "objects": {
        "11572d7d-c95f-47e0-a3fa-400d86e6f3f0": {
            "background": "grey85",
            "bbox": 24179,
            "borderwidth": 2,
            "hidden": false,
            "item": "textbox",
            "itemid": 1,
            "justification": 1,
            "posx": 500.0,
            "posy": 250.0,
            "tags": "textwidget1",
            "text": "This is the default layout file loaded on start-up and is configured\nto publish all GPIO sensor inputs via the MQTT network. \n\nTo complete the configuration:\n- Select Settings => MQTT\n  - Under Broker Configuration:\n    - Specify the IP address of your main signalling node\n  - Under Network Configuration:\n    - Specify the name you have assigned to your signalling network\n    - Specify a unique name (on the network) for this signallling node. \n\nIf you want to run this node 'headless' (without a monitor, keyboard or \nmouse connected), then you will also need to:\n  - On this node - under Network Configuration:\n    - Select 'Connect to broker on layout load'\n    - Select 'Quit application on reciept of shutdown'\n  - On your main signalling node - under Network Configuration:\n    - Select 'Publish shutdown on application exit'\n\nThis will cause this signalling node to initiate a shutdown when the\napplication instance running on your main signalling node is closed.\nThe Raspberry Pi will perform an orderly shutdown 10 seconds after \nthe application exits.\n\nIf required, you can also run a full layout file on this node\n(simulating another signal box on the layout for example) but\nnote that the Raspberry Pi-zero is not as powerful as the Pi-4B\nand so this will really only be suitable for simple layouts.",
            "textcolour": "#0000ff",
            "textfonttuple": [
                "Courier",
                10,
                "bold "
            ]
        }
    },
    "points": {},
    "sections": {},
    "settings": {
        "canvas": {
            "canvascolour": "grey85",
            "displaygrid": true,
            "grid": 25,
            "gridcolour": "#999",
            "height": 500,
            "scrollbuttons": [],
            "snaptogrid": true,
            "width": 1000
        },
        "general": {
            "automation": true,
            "editmode": true,
            "filename": "/home/john/model-railway-signalling/model_railway_signals/examples/sensor_node.sig",
            "info": "Document your layout here",
            "leverinterlocking": false,
            "leverpopupwarnings": false,
            "menubarfontsize": 10,
            "resetdelay": 0,
            "spadpopups": false,
            "version": "Version 5.4.0"
        },
        "gpio": {
            "maxevents": 100,
            "portmappings": [
                [
                    4,
                    4
                ],
                [
                    5,
                    5
                ],
                [
                    6,
                    6
                ],
                [
                    7,
                    7
                ],
                [
                    8,
                    8
                ],
                [
                    9,
                    9
                ],
                [
                    10,
                    10
                ],
                [
                    11,
                    11
                ],
                [
                    12,
                    12
                ],
                [
                    13,
                    13
                ],
                [
                    18,
                    18
                ],
                [
                    19,
                    19
                ],
                [
                    20,
                    20
                ],
                [
                    21,
                    21
                ],
                [
                    22,
                    22
                ],
                [
                    23,
                    23
                ],
                [
                    24,
                    24
                ],
                [
                    25,
                    25
                ],
                [
                    26,
                    26
                ],
                [
                    27,
                    27
                ]
            ],
            "timeoutperiod": 1.0,
            "triggerdelay": 0.02
        },
        "logging": {
            "level": 2
        },
        "mqtt": {
            "debug": false,
            "network": "network",
            "node": "node",
            "password": "",
            "port": 1883,
            "pubdcc": false,
            "pubinstruments": [],
            "pubsections": [],
            "pubsensors": [
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27
            ],
            "pubshutdown": false,
            "pubsignals": [],
            "startup": false,
            "subdccnodes": [],
            "subinstruments": [],
            "subsections": [],
            "subsensors": [],
            "subshutdown": false,
            "subsignals": [],
            "url": "127.0.0.1",
            "username": ""
        },
        "sprog": {
            "addressmode": 1,
            "baud": 460800,
            "debug": false,
            "port": "/dev/serial0",
            "power": false,
            "startup": false
        },
        "styles": {
            "dccswitches": {
                "buttoncolour": "SkyBlue2",
                "buttonwidth": 12,
                "textcolourtype": 1,
                "textfonttuple": [
                    "Courier",
                    9,
                    ""
                ]
            },
            "levers": {
                "buttoncolour": "Grey85",
                "framecolour": "Grey40",
                "lockcolourtype": 1,
                "textcolourtype": 1,
                "textfonttuple": [
                    "TkFixedFont",
                    8,
                    "bold"
                ]
            },
            "points": {
                "buttoncolour": "Grey85",
                "textcolourtype": 1,
                "textfonttuple": [
                    "Courier",
                    8,
                    ""
                ]
            },
            "routebuttons": {
                "buttoncolour": "SeaGreen3",
                "buttonwidth": 15,
                "textcolourtype": 1,
                "textfonttuple": [
                    "Courier",
                    9,
                    ""
                ]
            },
            "routelines": {
                "colour": "Black",
                "linestyle": [],
                "linewidth": 3
            },
            "signals": {
                "buttoncolour": "Grey85",
                "postcolour": "White",
                "textcolourtype": 1,
                "textfonttuple": [
                    "Courier",
                    8,
                    ""
                ]
            },
            "textboxes": {
                "background": "",
                "borderwidth": 0,
                "justification": 2,
                "textcolour": "Black",
                "textfonttuple": [
                    "Courier",
                    10,
                    ""
                ]
            },
            "tracksections": {
                "buttoncolour": "Black",
                "buttonwidth": 5,
                "defaultlabel": "XXXXX",
                "textcolourtype": 1,
                "textfonttuple": [
                    "Courier",
                    9,
                    "bold"
                ]
            }
        }
    },
    "signals": {}
}