{
    "buttons": {},
    "information": "Model Railway Signalling Configuration File",
    "instruments": {},
    "levers": {},
    "objects": {
        "02febfbf-ee80-4c08-b52d-84b72fa9c23b": {
            "approachcontrol": [
                3,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                true,
                ""
            ],
            "bbox": 2107,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 2,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 0,
            "overrideahead": false,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [
                        [
                            3,
                            true
                        ],
                        [
                            5,
                            false
                        ]
                    ],
                    "4",
                    0
                ],
                [
                    [
                        [
                            3,
                            false
                        ]
                    ],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 1175.0,
            "posy": 150.0,
            "sigarms": [
                [
                    [
                        true,
                        20
                    ],
                    [
                        true,
                        22
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        true,
                        21
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [
                    [
                        13,
                        [
                            false,
                            false,
                            false,
                            false,
                            true,
                            false,
                            false
                        ]
                    ]
                ],
                [
                    [
                        7,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                true,
                true,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal2",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                12,
                [
                    [
                        4
                    ],
                    [
                        13
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "04c60499-4854-4474-9053-6ecdd98f13d7": {
            "background": "",
            "bbox": 2110,
            "borderwidth": 0,
            "hidden": false,
            "item": "textbox",
            "itemid": 3,
            "justification": 1,
            "posx": 528.0,
            "posy": 394.0,
            "tags": "textwidget3",
            "text": "Automation Example (in this case the automation is non-prototypical but\nprovides near-prototypical signal operation as you operate the trains)\n1) All signals overridden to DANGER if the Track Section ahead is OCCUPIED\n2) All home signals behind each 'section' signal configured for approach control\n   (this means that if the 'section' signal is at DANGER, all home signals behind\n   will be nominally overridden to DANGER and only 'released' when the train\n   approaches them - simulating the signaller pulling off the signals to allow\n   the train to proceed to the next home signal. Once the signal has been passed\n   then the signal will be returned to DANGER and the approach control reset)\n3) Signals 4 and 11 configured as timed signals for trains exiting the layout\n4) Some signals fully automated (no control buttons)",
            "textcolour": "Black",
            "textfonttuple": [
                "TkFixedFont",
                10,
                "bold "
            ]
        },
        "0664c58f-923d-4de0-b1fa-0ced0da953a5": {
            "approachcontrol": [
                3,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                true,
                ""
            ],
            "bbox": 2137,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": true,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 17,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 0,
            "overrideahead": false,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [],
                    "16",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 150.0,
            "posy": 200.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal17",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                10,
                [
                    [
                        5
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "146287d7-4772-46bc-8952-89c98ff36bb0": {
            "arrowends": 0,
            "arrowtype": [
                0,
                0,
                0
            ],
            "bbox": 2145,
            "colour": "black",
            "endx": 1275.0,
            "endy": 200.0,
            "item": "line",
            "itemid": 1,
            "linestyle": [],
            "linewidth": 3,
            "posx": 975.0,
            "posy": 200.0,
            "selection": "line1selected",
            "tags": "line1"
        },
        "16c59187-f382-4e52-9d40-41856f8c57e9": {
            "approachcontrol": [
                3,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                true,
                ""
            ],
            "bbox": 2172,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": true,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 19,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 180,
            "overrideahead": false,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [],
                    "11",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 425.0,
            "posy": 250.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal19",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                14,
                [
                    [
                        15
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "1b3f1dca-d687-4ec6-98e3-cc017d9f844a": {
            "bbox": 2176,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 11,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 750.0,
            "posy": 150.0,
            "tags": "section11",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "21668397-1f72-4283-ab64-b4b9f20013d9": {
            "background": "",
            "bbox": 2179,
            "borderwidth": 0,
            "hidden": false,
            "item": "textbox",
            "itemid": 5,
            "justification": 2,
            "posx": 48.0,
            "posy": 161.0,
            "tags": "textwidget5",
            "text": "Set\nNext\nTrain",
            "textcolour": "Black",
            "textfonttuple": [
                "TkFixedFont",
                9,
                ""
            ]
        },
        "23ef06a2-5597-4aba-920c-ca15828a7733": {
            "bbox": 2183,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 9,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 750.0,
            "posy": 250.0,
            "tags": "section9",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "2a02397d-f080-4a06-83f0-c8384cbf77d5": {
            "background": "",
            "bbox": 2186,
            "borderwidth": 0,
            "hidden": false,
            "item": "textbox",
            "itemid": 4,
            "justification": 2,
            "posx": 1050.0,
            "posy": 75.0,
            "tags": "textwidget4",
            "text": "Semaphore Automation Example",
            "textcolour": "Black",
            "textfonttuple": [
                "TkFixedFont",
                20,
                "bold "
            ]
        },
        "2af3fecc-b104-4832-bc02-aadedb0177e9": {
            "approachcontrol": [
                3,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                true,
                ""
            ],
            "bbox": 2213,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 12,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 180,
            "overrideahead": false,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [
                        [
                            5,
                            false
                        ]
                    ],
                    "10",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 1450.0,
            "posy": 250.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal12",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                7,
                [
                    [
                        8
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "2b5d8e22-47be-4105-b392-ab96eebc8b22": {
            "approachcontrol": [
                3,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                true,
                ""
            ],
            "bbox": 2240,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 8,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 0,
            "overrideahead": false,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [],
                    "1",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 625.0,
            "posy": 200.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [
                    [
                        6,
                        [
                            false,
                            true,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        15,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal8",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                1,
                [
                    [
                        2
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "2e5a7c4c-89ef-4aeb-8413-b75befa4db5c": {
            "background": "",
            "bbox": 2243,
            "borderwidth": 0,
            "hidden": false,
            "item": "textbox",
            "itemid": 6,
            "justification": 2,
            "posx": 1750.0,
            "posy": 286.0,
            "tags": "textwidget6",
            "text": "Set\nNext\nTrain",
            "textcolour": "Black",
            "textfonttuple": [
                "TkFixedFont",
                9,
                ""
            ]
        },
        "3ae53dd4-7b7e-4912-9dd8-f9cd9daf875b": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2269,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": true,
            "hidebuttons": false,
            "interlockahead": true,
            "item": "signal",
            "itemid": 9,
            "itemsubtype": 2,
            "itemtype": 3,
            "orientation": 180,
            "overrideahead": true,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [],
                    "12",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 1675.0,
            "posy": 250.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal9",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                6,
                [
                    [
                        7
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "3c5565ee-45f3-4298-a7da-5c1c52ebf2d2": {
            "bbox": 2273,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 13,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 1550.0,
            "posy": 150.0,
            "tags": "section13",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "3f11b41e-b356-402c-b59e-b314963b3723": {
            "arrowends": 0,
            "arrowtype": [
                0,
                0,
                0
            ],
            "bbox": 2281,
            "colour": "black",
            "endx": 1375.0,
            "endy": 200.0,
            "item": "line",
            "itemid": 2,
            "linestyle": [],
            "linewidth": 3,
            "posx": 1800.0,
            "posy": 200.0,
            "selection": "line2selected",
            "tags": "line2"
        },
        "40da50ad-40cf-4f2f-a86f-eef794d41ace": {
            "bbox": 2285,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 2,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 750.0,
            "posy": 200.0,
            "tags": "section2",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "48fb7f13-0c14-4920-b2d3-a1013c4b5a1f": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2293,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 6,
            "itemsubtype": 1,
            "itemtype": 4,
            "orientation": 180,
            "overrideahead": false,
            "overridesignal": false,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [
                        [
                            2,
                            false
                        ]
                    ],
                    "",
                    0
                ],
                [
                    [
                        [
                            2,
                            true
                        ]
                    ],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 1000.0,
            "posy": 150.0,
            "sigarms": [
                [
                    [
                        true,
                        60
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [
                    [
                        5,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [
                    [
                        1,
                        [
                            false,
                            true,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        8,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                true,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal6",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                12,
                [
                    [
                        11
                    ],
                    [
                        2
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "49436626-93f4-4b47-b9ae-5221c9d27577": {
            "bbox": 2297,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 7,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 1550.0,
            "posy": 250.0,
            "tags": "section7",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "547bd259-550f-4e84-b100-fb0dd86ba88d": {
            "approachcontrol": [
                3,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                true,
                ""
            ],
            "bbox": 2325,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 3,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 0,
            "overrideahead": false,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [
                        [
                            3,
                            false
                        ],
                        [
                            5,
                            false
                        ]
                    ],
                    "4",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 1175.0,
            "posy": 200.0,
            "sigarms": [
                [
                    [
                        true,
                        30
                    ],
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [
                    [
                        13,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal3",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                3,
                [
                    [
                        4
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "56b15939-53f4-4ba0-8e3f-7bbef0a19165": {
            "arrowends": 0,
            "arrowtype": [
                0,
                0,
                0
            ],
            "bbox": 2333,
            "colour": "black",
            "endx": 1375.0,
            "endy": 250.0,
            "item": "line",
            "itemid": 3,
            "linestyle": [],
            "linewidth": 3,
            "posx": 1800.0,
            "posy": 250.0,
            "selection": "line3selected",
            "tags": "line3"
        },
        "59c4ede5-e1ca-42cb-bcd9-fd630fb9c383": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2380,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": true,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": true,
            "hidebuttons": false,
            "interlockahead": true,
            "item": "signal",
            "itemid": 16,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 0,
            "overrideahead": true,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [],
                    "8",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 375.0,
            "posy": 200.0,
            "sigarms": [
                [
                    [
                        true,
                        80
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        true,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal16",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                5,
                [
                    [
                        1
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "654f5df2-b71f-427a-b79b-385df0044283": {
            "background": "#30d85e",
            "bbox": 2383,
            "borderwidth": 2,
            "hidden": false,
            "item": "textbox",
            "itemid": 1,
            "justification": 2,
            "posx": 1075.0,
            "posy": 275.0,
            "tags": "textwidget1",
            "text": " Platform 1 ",
            "textcolour": "Black",
            "textfonttuple": [
                "TkFixedFont",
                9,
                "bold "
            ]
        },
        "65b221aa-9d3c-4a9d-bbfe-1e61331d3811": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2391,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 15,
            "itemsubtype": 1,
            "itemtype": 4,
            "orientation": 180,
            "overrideahead": false,
            "overridesignal": false,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [
                        [
                            2,
                            false
                        ]
                    ],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 1000.0,
            "posy": 200.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [
                    [
                        1,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        8,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal15",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                3,
                [
                    [
                        2
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "6c28ce24-e08c-4845-8e06-b21f418911eb": {
            "alsoswitch": 4,
            "automatic": false,
            "bbox": 2400,
            "buttoncolour": "Grey85",
            "colour": "black",
            "dccaddress": 101,
            "dccreversed": false,
            "hasfpl": true,
            "hidebuttons": false,
            "item": "point",
            "itemid": 3,
            "itemsubtype": 1,
            "itemtype": 1,
            "linestyle": [],
            "linewidth": 3,
            "orientation": 0,
            "posx": 1300.0,
            "posy": 150.0,
            "reverse": false,
            "sectioninterlock": [],
            "siginterlock": [
                [
                    2,
                    [
                        true,
                        true,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ],
                [
                    3,
                    [
                        true,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ],
                [
                    7,
                    [
                        true,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ],
                [
                    13,
                    [
                        true,
                        false,
                        false,
                        false,
                        true,
                        false,
                        false
                    ]
                ]
            ],
            "tags": "point3",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "71e6fad1-a16e-4a4a-be41-a40a63a0f006": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2426,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 4,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 0,
            "overrideahead": false,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 1625.0,
            "posy": 200.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal4",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    true,
                    4,
                    0,
                    3
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                4,
                [
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "85d79875-69a8-4f48-b990-56add64e268d": {
            "bbox": 2430,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 1,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 525.0,
            "posy": 200.0,
            "tags": "section1",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "8efa0c5d-19c3-4826-a797-34453446bb67": {
            "arrowends": 0,
            "arrowtype": [
                0,
                0,
                0
            ],
            "bbox": 2438,
            "colour": "black",
            "endx": 1275.0,
            "endy": 150.0,
            "item": "line",
            "itemid": 4,
            "linestyle": [],
            "linewidth": 3,
            "posx": 975.0,
            "posy": 150.0,
            "selection": "line4selected",
            "tags": "line4"
        },
        "902284fd-0dc0-4ded-96b6-e94ba78a1cf4": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2446,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 14,
            "itemsubtype": 1,
            "itemtype": 4,
            "orientation": 0,
            "overrideahead": false,
            "overridesignal": false,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [
                        [
                            5,
                            true
                        ]
                    ],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 1300.0,
            "posy": 250.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [
                    [
                        13,
                        [
                            false,
                            true,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal14",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                8,
                [
                    [
                        4
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "94fd8cf6-a410-4f67-9da5-c985edcbf688": {
            "bbox": 2450,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 3,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 1075.0,
            "posy": 200.0,
            "tags": "section3",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "98387fe9-9a77-4b97-92e3-0df8c2a21c2f": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2476,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": true,
            "hidebuttons": false,
            "interlockahead": true,
            "item": "signal",
            "itemid": 18,
            "itemsubtype": 2,
            "itemtype": 3,
            "orientation": 180,
            "overrideahead": true,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [],
                    "19",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 675.0,
            "posy": 250.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal18",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                9,
                [
                    [
                        14
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "9c4be7ee-4780-4e8b-92a2-08e95a11d339": {
            "arrowends": 0,
            "arrowtype": [
                0,
                0,
                0
            ],
            "bbox": 2484,
            "colour": "black",
            "endx": 0.0,
            "endy": 250.0,
            "item": "line",
            "itemid": 5,
            "linestyle": [],
            "linewidth": 3,
            "posx": 1325.0,
            "posy": 250.0,
            "selection": "line5selected",
            "tags": "line5"
        },
        "a6e56e82-869d-4a63-b9fe-649476f59a62": {
            "bbox": 2488,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 12,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 1075.0,
            "posy": 150.0,
            "tags": "section12",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "a9fca83a-6c10-454f-a141-e4931d7c06d7": {
            "arrowends": 1,
            "arrowtype": [
                1,
                1,
                1
            ],
            "bbox": 2496,
            "colour": "black",
            "endx": 1325.0,
            "endy": 150.0,
            "item": "line",
            "itemid": 6,
            "linestyle": [],
            "linewidth": 3,
            "posx": 1600.0,
            "posy": 150.0,
            "selection": "line6selected",
            "tags": "line6"
        },
        "aa07d0f4-841d-40c9-87ef-cf9ec08a9239": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2522,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": true,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 11,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 180,
            "overrideahead": false,
            "overridesignal": false,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 200.0,
            "posy": 250.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal11",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    true,
                    11,
                    0,
                    3
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                15,
                [
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "af408a69-7a43-4f8e-9453-728ec2747514": {
            "bbox": 2526,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 6,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 1750.0,
            "posy": 250.0,
            "tags": "section6",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "b8c1ca15-569a-42d8-9692-c4634b06e70b": {
            "alsoswitch": 0,
            "automatic": true,
            "bbox": 2533,
            "buttoncolour": "Grey85",
            "colour": "black",
            "dccaddress": 0,
            "dccreversed": false,
            "hasfpl": false,
            "hidebuttons": false,
            "item": "point",
            "itemid": 4,
            "itemsubtype": 1,
            "itemtype": 1,
            "linestyle": [],
            "linewidth": 3,
            "orientation": 180,
            "posx": 1300.0,
            "posy": 200.0,
            "reverse": false,
            "sectioninterlock": [],
            "siginterlock": [],
            "tags": "point4",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "bd8c0b62-add0-4714-b49a-7bbae0da4124": {
            "bbox": 2537,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 8,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 1075.0,
            "posy": 250.0,
            "tags": "section8",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "bef3b222-f3c5-427d-b34c-cd5d283a00fa": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2563,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": true,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 10,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 180,
            "overrideahead": false,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [],
                    "18",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 900.0,
            "posy": 250.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal10",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                8,
                [
                    [
                        9
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "c157e7b9-9ea8-46a6-8b6f-99f2ac3b6626": {
            "arrowends": 0,
            "arrowtype": [
                0,
                0,
                0
            ],
            "bbox": 2571,
            "colour": "black",
            "endx": 0.0,
            "endy": 200.0,
            "item": "line",
            "itemid": 7,
            "linestyle": [],
            "linewidth": 3,
            "posx": 925.0,
            "posy": 200.0,
            "selection": "line7selected",
            "tags": "line7"
        },
        "c52e3e22-22c7-4623-bd67-8cacac93ba06": {
            "alsoswitch": 1,
            "automatic": false,
            "bbox": 2580,
            "buttoncolour": "Grey85",
            "colour": "black",
            "dccaddress": 100,
            "dccreversed": false,
            "hasfpl": true,
            "hidebuttons": false,
            "item": "point",
            "itemid": 2,
            "itemsubtype": 1,
            "itemtype": 2,
            "linestyle": [],
            "linewidth": 3,
            "orientation": 0,
            "posx": 950.0,
            "posy": 200.0,
            "reverse": false,
            "sectioninterlock": [],
            "siginterlock": [
                [
                    6,
                    [
                        true,
                        true,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ],
                [
                    15,
                    [
                        true,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ],
                [
                    5,
                    [
                        true,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ],
                [
                    1,
                    [
                        true,
                        true,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ]
            ],
            "tags": "point2",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "c8564be9-6891-48f3-999a-53472f24c85f": {
            "arrowends": 2,
            "arrowtype": [
                1,
                1,
                1
            ],
            "bbox": 2588,
            "colour": "black",
            "endx": 675.0,
            "endy": 150.0,
            "item": "line",
            "itemid": 8,
            "linestyle": [],
            "linewidth": 3,
            "posx": 925.0,
            "posy": 150.0,
            "selection": "line8selected",
            "tags": "line8"
        },
        "c88a11f5-d1b0-4a02-869e-f53d2c930635": {
            "bbox": 2592,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 5,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 275.0,
            "posy": 200.0,
            "tags": "section5",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "ce134677-c6b8-43f6-8d96-4da4fc745df1": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2600,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 5,
            "itemsubtype": 1,
            "itemtype": 4,
            "orientation": 0,
            "overrideahead": false,
            "overridesignal": false,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [
                        [
                            2,
                            false
                        ]
                    ],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 925.0,
            "posy": 150.0,
            "sigarms": [
                [
                    [
                        true,
                        50
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [
                    [
                        6,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        13,
                        [
                            false,
                            false,
                            false,
                            false,
                            true,
                            false,
                            false
                        ]
                    ],
                    [
                        7,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal5",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                11,
                [
                    [
                        12
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "d5bac97c-de07-407d-966d-83ea0ae26a83": {
            "bbox": 2604,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 10,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 50.0,
            "posy": 200.0,
            "tags": "section10",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "d9840a46-28fd-40dd-a059-df46b9a762e2": {
            "alsoswitch": 6,
            "automatic": false,
            "bbox": 2612,
            "buttoncolour": "Grey85",
            "colour": "black",
            "dccaddress": 0,
            "dccreversed": false,
            "hasfpl": false,
            "hidebuttons": false,
            "item": "point",
            "itemid": 5,
            "itemsubtype": 1,
            "itemtype": 2,
            "linestyle": [],
            "linewidth": 3,
            "orientation": 0,
            "posx": 1350.0,
            "posy": 250.0,
            "reverse": false,
            "sectioninterlock": [],
            "siginterlock": [
                [
                    2,
                    [
                        true,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ],
                [
                    12,
                    [
                        true,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ],
                [
                    3,
                    [
                        true,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ],
                [
                    14,
                    [
                        true,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false
                    ]
                ],
                [
                    13,
                    [
                        true,
                        true,
                        false,
                        false,
                        true,
                        false,
                        false
                    ]
                ]
            ],
            "tags": "point5",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "dbb2c8c7-46aa-44aa-a3bf-694a4b37aa1f": {
            "background": "#30d85e",
            "bbox": 2615,
            "borderwidth": 2,
            "hidden": false,
            "item": "textbox",
            "itemid": 2,
            "justification": 2,
            "posx": 1075.0,
            "posy": 175.0,
            "tags": "textwidget2",
            "text": "Platform 2/3",
            "textcolour": "Black",
            "textfonttuple": [
                "TkFixedFont",
                9,
                "bold "
            ]
        },
        "dcf7ea0d-cd58-45bf-842e-d4e6e87c9a2a": {
            "bbox": 2619,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 15,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 275.0,
            "posy": 250.0,
            "tags": "section15",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "df337c59-d6c8-420a-9165-628b58e8be08": {
            "alsoswitch": 0,
            "automatic": true,
            "bbox": 2626,
            "buttoncolour": "Grey85",
            "colour": "black",
            "dccaddress": 0,
            "dccreversed": false,
            "hasfpl": false,
            "hidebuttons": false,
            "item": "point",
            "itemid": 1,
            "itemsubtype": 1,
            "itemtype": 2,
            "linestyle": [],
            "linewidth": 3,
            "orientation": 180,
            "posx": 950.0,
            "posy": 150.0,
            "reverse": false,
            "sectioninterlock": [],
            "siginterlock": [],
            "tags": "point1",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "e0705584-fbf0-47f0-a695-810489e4d5d4": {
            "bbox": 2630,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 4,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 1550.0,
            "posy": 200.0,
            "tags": "section4",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        },
        "ed8d646c-60cc-4a5a-b8f0-cbd337263db8": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2638,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 7,
            "itemsubtype": 1,
            "itemtype": 4,
            "orientation": 180,
            "overrideahead": false,
            "overridesignal": false,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [
                        [
                            3,
                            false
                        ]
                    ],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 1350.0,
            "posy": 150.0,
            "sigarms": [
                [
                    [
                        true,
                        70
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [
                    [
                        2,
                        [
                            false,
                            true,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        1,
                        [
                            false,
                            true,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        5,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal7",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                13,
                [
                    [
                        12
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "f14ef6e8-7b7b-4568-b0e6-c105889caf10": {
            "alsoswitch": 0,
            "automatic": true,
            "bbox": 2645,
            "buttoncolour": "Grey85",
            "colour": "black",
            "dccaddress": 0,
            "dccreversed": false,
            "hasfpl": false,
            "hidebuttons": false,
            "item": "point",
            "itemid": 6,
            "itemsubtype": 1,
            "itemtype": 2,
            "linestyle": [],
            "linewidth": 3,
            "orientation": 180,
            "posx": 1350.0,
            "posy": 200.0,
            "reverse": false,
            "sectioninterlock": [],
            "siginterlock": [],
            "tags": "point6",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "f455f78a-6e63-453c-b335-28b389182cbb": {
            "approachcontrol": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                false,
                ""
            ],
            "bbox": 2653,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 13,
            "itemsubtype": 1,
            "itemtype": 4,
            "orientation": 180,
            "overrideahead": false,
            "overridesignal": false,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [
                        [
                            5,
                            false
                        ],
                        [
                            3,
                            false
                        ]
                    ],
                    "",
                    0
                ],
                [
                    [
                        [
                            5,
                            true
                        ]
                    ],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [
                        [
                            5,
                            false
                        ],
                        [
                            3,
                            true
                        ]
                    ],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 1400.0,
            "posy": 200.0,
            "sigarms": [
                [
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [
                    [
                        3,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        1,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [
                    [
                        14,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                [],
                [
                    [
                        2,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        1,
                        [
                            false,
                            true,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        5,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                []
            ],
            "sigroutes": [
                true,
                true,
                false,
                false,
                true,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal13",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                4,
                [
                    [
                        3
                    ],
                    [
                        8
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        12
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "f7e885c9-faa7-4ee6-87df-9c035c5dadeb": {
            "approachcontrol": [
                3,
                1,
                0,
                0,
                0,
                0,
                0
            ],
            "approachsensor": [
                true,
                ""
            ],
            "bbox": 2683,
            "buttoncolour": "Grey85",
            "clearancedelay": 0,
            "dccaspects": [
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dccautoinhibit": false,
            "dccfeathers": [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "dcctheatre": [
                [
                    "#",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ],
                [
                    "",
                    []
                ]
            ],
            "distautomatic": false,
            "feathers": [
                false,
                false,
                false,
                false,
                false,
                false,
                false
            ],
            "flipped": false,
            "fullyautomatic": false,
            "hidebuttons": false,
            "interlockahead": false,
            "item": "signal",
            "itemid": 1,
            "itemsubtype": 1,
            "itemtype": 3,
            "orientation": 0,
            "overrideahead": false,
            "overridesignal": true,
            "passedsensor": [
                true,
                ""
            ],
            "pointinterlock": [
                [
                    [
                        [
                            2,
                            false
                        ]
                    ],
                    "3",
                    0
                ],
                [
                    [
                        [
                            2,
                            true
                        ]
                    ],
                    "2",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ],
                [
                    [],
                    "",
                    0
                ]
            ],
            "postcolour": "White",
            "posx": 850.0,
            "posy": 200.0,
            "sigarms": [
                [
                    [
                        true,
                        10
                    ],
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        true,
                        11
                    ],
                    [
                        true,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ],
                [
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ],
                    [
                        false,
                        0
                    ]
                ]
            ],
            "siginterlock": [
                [
                    [
                        15,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        13,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [
                    [
                        6,
                        [
                            false,
                            true,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ],
                    [
                        13,
                        [
                            false,
                            false,
                            false,
                            false,
                            true,
                            false,
                            false
                        ]
                    ],
                    [
                        7,
                        [
                            true,
                            false,
                            false,
                            false,
                            false,
                            false,
                            false
                        ]
                    ]
                ],
                [],
                [],
                [],
                [],
                []
            ],
            "sigroutes": [
                true,
                true,
                false,
                false,
                false,
                false,
                false
            ],
            "slotwith": 0,
            "subroutes": [
                true,
                true,
                false,
                false,
                false,
                false,
                false
            ],
            "subsidary": [
                false,
                0,
                false
            ],
            "tags": "signal1",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                8,
                ""
            ],
            "theatreroute": false,
            "theatresubsidary": false,
            "timedsequences": [
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ],
                [
                    false,
                    0,
                    0,
                    0
                ]
            ],
            "trackinterlock": [
                [],
                [],
                [],
                [],
                [],
                [],
                []
            ],
            "tracksections": [
                2,
                [
                    [
                        3
                    ],
                    [
                        12
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ],
                    [
                        0
                    ]
                ]
            ],
            "xbuttonoffset": 0,
            "ybuttonoffset": 0
        },
        "fc4b8a11-3862-417f-ba09-493456b59064": {
            "bbox": 2687,
            "buttoncolour": "Black",
            "buttonwidth": 5,
            "defaultlabel": "XXXXX",
            "editable": true,
            "gpiosensor": "",
            "hidden": false,
            "highlightcolour": "Red",
            "item": "section",
            "itemid": 14,
            "linestohighlight": [],
            "mirror": "",
            "pointstohighlight": [],
            "posx": 525.0,
            "posy": 250.0,
            "tags": "section14",
            "textcolourtype": 1,
            "textfonttuple": [
                "Courier",
                9,
                "bold"
            ]
        }
    },
    "points": {
        "1": {
            "fpllock": false,
            "locked": false,
            "switched": true
        },
        "2": {
            "fpllock": true,
            "locked": false,
            "switched": true
        },
        "3": {
            "fpllock": true,
            "locked": false,
            "switched": false
        },
        "4": {
            "fpllock": false,
            "locked": false,
            "switched": false
        },
        "5": {
            "fpllock": false,
            "locked": false,
            "switched": false
        },
        "6": {
            "fpllock": false,
            "locked": false,
            "switched": false
        }
    },
    "sections": {
        "1": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "10": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "11": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "12": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "13": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "14": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "15": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "2": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "3": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "4": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "5": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "6": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "7": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "8": {
            "labeltext": "XXXXX",
            "occupied": false
        },
        "9": {
            "labeltext": "XXXXX",
            "occupied": false
        }
    },
    "settings": {
        "canvas": {
            "canvascolour": "grey85",
            "displaygrid": true,
            "grid": 25,
            "gridcolour": "#999",
            "height": 500,
            "scrollbuttons": [],
            "snaptogrid": true,
            "width": 1800
        },
        "control": {
            "dccsoundmappings": []
        },
        "general": {
            "automation": true,
            "baseitemid": 1,
            "editmode": false,
            "filename": "/home/john/model-railway-signalling/model_railway_signals/examples/automation_semaphore_example.sig",
            "info": "This layout is a development of the basic interlocking example to demonstrate signalling automation\n(note that the application needs to be in 'run' mode for all automation features to function).\n\nTrack sensors (such as those from TrainTech, Heathcote Electronics, DCC Concepts etc) can be located \nwith each signal and connected in to the R-Pi's GPIO ports (via appropriate opto-isolator circuits).\nEach GPIO port can then be mapped to a signal to generate 'signal passed' events - In 'edit' mode,\nclick on a signal and select the 'automation' tab to view the configuration (note that external\nGPIO sensors haven't been configured for this particular example layout). 'Signal passed' events\ncan also be triggered by clicking on the small button at the base of each signal (as an aid to \ndevelopment and testing of signalling schemes before going 'live' with the R-Pi).\n\nTrack sections can be added to the schematic to provide a mimic display of track occupancy (when a\ntrain passes a signal (signal must be 'off') it gets passed from the section behind to the section ahead.\nThe required behavior is configured via the 'automation' tab of each signal. For example, signal 1\ncontrols two 'routes' so when passed, section 2 will be cleared and either section 12 or 3 will be set \nto occupied, depending on which route the signal is cleared for.\n\nAll main signals are configured to be 'overridden' if the track section ahead is occupied. This means\nthat each signal will automatically change to 'on' when passed (section ahead is occupied) and then\nrevert to 'off' as soon as the section ahead is cleared. Note that some of the signals in this example \nhave been configured as 'fully automatic' (without a control button). This means that they will be 'off'\nby default and controlled entirely by whether the track section ahead is occupied or not.\n\nTo simulate prototypical aspect changes for trains going off scene, the 'exit' signals (signals 4 and\n11 in this example) can be configured as 'timed signals'. Once passed (when 'off') they are overriden \nto 'on' (as per the other signals on the layout) but then revert to 'off' after the specified delay.\n\nTrack sensors can also be positioned slightly before the signal and mapped to generate 'signal \napproached' events to simulate 'approach control'. In this example, all non-fully-automatic home signals \nare configured for 'release on red based on the signals ahead'. This means that if any home signals ahead\nare showing danger then the home signal will also be overridden to 'on' by default.As the train approaches\nthe signal (at a slow speed as the signal is against it) then the signal will be released to 'off' to\nallow the train to pass and then revert back to the overidden 'on' state when the signal is passed.\nSignal 1 is also configured for 'release on red' for the diverging (low-speed) route. In this case it\nwill be overridden to 'on' even if all home signals ahead are 'off', only released as the train approaches.\n\nTo demonstrate all the above in action, set 'run' mode and reset the layout to set all signals, points\nand track sections back to their default states. Right click the far left track section and enter a train\ndesignation code of your choice (this sets the section to 'occupied'). Set signals 8, 1 and 3 to 'off' (note\nthat they will remail overridden to 'on' as home signal ahead 4 is still showing 'on'. Now, move the train\nthrough the schematic, clicking the 'signal passed' button at the base of each signal along the route\nin turn (don't forget to click the 'signal approached' button ahead of each signal if you want to see\napproach control working). When the train reaches signal 4, set the signal to 'off' and trigger the signal\npassed event. The track section before the signal will be cleared and the signal overridden to 'on' as part\nof the timed sequence. After a short delay it will revert to 'off' and when it does, all home signals behind\nwill also revert to 'off' (as they will no longer be overridden on a home signal ahead).\n\nThe layout is fully configured to support all possible train movements (including shunting movements)\nso have a play - but note that signals can only be 'passed' when 'off' for the track occupancy\nchanges to work correctly (the application currently doesn't support any form of SPAD functionality)\n\n",
            "leverinterlocking": false,
            "leverpopupwarnings": false,
            "menubarfontsize": 10,
            "resetdelay": 0,
            "spadpopups": false,
            "version": "Version 6.0.0"
        },
        "gpio": {
            "maxevents": 100,
            "portmappings": [],
            "timeoutperiod": 1.0,
            "triggerdelay": 0.001
        },
        "logging": {
            "level": 2
        },
        "mqtt": {
            "debug": false,
            "network": "",
            "node": "",
            "password": "",
            "port": 1883,
            "pubdcc": false,
            "pubinstruments": [],
            "pubsections": [],
            "pubsensors": [],
            "pubshutdown": false,
            "pubsignals": [],
            "startup": false,
            "subdccnodes": [],
            "subinstruments": [],
            "subsections": [],
            "subsensors": [],
            "subshutdown": false,
            "subsignals": [],
            "url": "",
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
    "signals": {
        "1": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 2,
            "sigclear": false,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "10": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": true,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "1016": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": true,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "11": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": true,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "12": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": false,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "13": {
            "override": false,
            "releaseonred": null,
            "releaseonyel": null,
            "routeset": 1,
            "sigclear": false,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": null
        },
        "14": {
            "override": false,
            "releaseonred": null,
            "releaseonyel": null,
            "routeset": 1,
            "sigclear": false,
            "siglocked": true,
            "subclear": false,
            "sublocked": false,
            "theatretext": null
        },
        "15": {
            "override": false,
            "releaseonred": null,
            "releaseonyel": null,
            "routeset": 1,
            "sigclear": false,
            "siglocked": true,
            "subclear": false,
            "sublocked": false,
            "theatretext": null
        },
        "16": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": true,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "17": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": true,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "18": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": true,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "19": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": true,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "2": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 2,
            "sigclear": false,
            "siglocked": true,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "3": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": false,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "4": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": true,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "5": {
            "override": false,
            "releaseonred": null,
            "releaseonyel": null,
            "routeset": 1,
            "sigclear": false,
            "siglocked": true,
            "subclear": false,
            "sublocked": false,
            "theatretext": null
        },
        "6": {
            "override": false,
            "releaseonred": null,
            "releaseonyel": null,
            "routeset": 2,
            "sigclear": false,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": null
        },
        "7": {
            "override": false,
            "releaseonred": null,
            "releaseonyel": null,
            "routeset": 1,
            "sigclear": false,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": null
        },
        "8": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": false,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        },
        "9": {
            "override": false,
            "releaseonred": false,
            "releaseonyel": false,
            "routeset": 1,
            "sigclear": true,
            "siglocked": false,
            "subclear": false,
            "sublocked": false,
            "theatretext": ""
        }
    }
}