{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 8,
			"minor" : 6,
			"revision" : 0,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ 205.0, 304.0, 640.0, 480.0 ],
		"bglocked" : 0,
		"openinpresentation" : 0,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"statusbarvisible" : 2,
		"toolbarvisible" : 1,
		"lefttoolbarpinned" : 0,
		"toptoolbarpinned" : 0,
		"righttoolbarpinned" : 0,
		"bottomtoolbarpinned" : 0,
		"toolbars_unpinned_last_save" : 0,
		"tallnewobj" : 0,
		"boxanimatetime" : 200,
		"enablehscroll" : 1,
		"enablevscroll" : 1,
		"devicewidth" : 0.0,
		"description" : "",
		"digest" : "",
		"tags" : "",
		"style" : "",
		"subpatcher_template" : "",
		"assistshowspatchername" : 0,
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-19",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 48.0, 403.0, 115.0, 22.0 ],
					"text" : "print mrp @popup 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-6",
					"linecount" : 35,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 593.0, 8.0, 981.0, 476.0 ],
					"presentation_linecount" : 35,
					"text" : "/midi: byte a, byte b, byte c // standard 3-byte MIDI messages e.g. 144 90 60\n/pedal/damper: int value || float value // change damper value\n/pedal/sostenuto: int value || float value // change sostenuto value\n/ptrk/mute: [array int notes]\n/ptrk/pitch: float freq, float amp\n/quality/brightness: int midiChannel, int midiNote, float brightness // brightness is an independent map to harmonic content, reduced to a linear scale\n/quality/intensity: int midiChannel, int midiNote, float intensity // intensity is a map to amplitude and harmonic content, relative to the current intensity\n/quality/pitch: int midiChannel, int midiNote, float pitch // Frequency base is relative to the fundamental frequency of the MIDI note\n/quality/pitch/vibrato: int midiChannel, int midiNote, float pitch // Frequency vibrato is a periodic modulation in frequency, zero-centered (+/-1 maps to range loaded from XML)\n/quality/harmonic: int midiChannel, int midiNote, float harmonic // ?\n/quality/harmonics/raw: int midiChannel, int midiNote, [array of float harmonics] // ?\n/ui/allnotesoff // turn all current notes off\n/ui/cal/save // Marked as LEGACY\n/ui/cal/load // Marked as LEGACY\n/ui/cal/phase: float p \n/ui/cal/volume: float v\n/ui/cal/currentnote: int n // \"Send a message announcing the current note, to update the UI\"\n/ui/gate // Marked as LEGACY\n/ui/harmonic // Marked as LEGACY\n/ui/patch/up // increment current program\n/ui/patch/down // decrement current program\n/ui/patch/set: int p // 0-N, set the current program to the given parameter\n/ui/pianokey/calibrate/start\n/ui/pianokey/calibrate/finish\n/ui/pianokey/calibrate/abort\n/ui/pianokey/calibrate/idle: // (?)\n/ui/pianokey/calibrate/disable: [array int keys] // 0-127, disable specified keys\n/ui/pianokey/calibrate/save: // only saves to `mrp-pb-calibration.txt`\n/ui/pianokey/calibrate/load: // only loads from `mrp-pb-calibration.txt`\n/ui/pianokey/calibrate/clear\n/ui/status/keyboard: // get real-time calibration status (?)\n/ui/tuning/global // Marked as LEGACY\n/ui/tuning/stretch // Marked as LEGACY\n/ui/volume: float vol // 0-1, >0.5 ? 4^((vol-0.5)/0.5) : 10^((vol-0.5)/0.5)\n/ui/volume/raw: float vol // 0-1, set volume directly"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-16",
					"linecount" : 14,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 364.0, 8.0, 202.0, 194.0 ],
					"presentation_linecount" : 14,
					"text" : "prepend OSC messages with the correct path from the list on the right, /mrp gets added to the paths automatically\n\nif the path is invalid, an error message is sent to the outlet\n\nthe message arguments will not be validated before the message is sent, so please consult the documentation for the MRP and make sure you are using the correct message arguments"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-5",
					"linecount" : 5,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 180.0, 128.0, 150.0, 74.0 ],
					"text" : "sending osc is turned off by default (@active 0)\n\nuse a toggle or @active 1 to turn it on"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-9",
					"linecount" : 8,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 48.0, 88.0, 107.0, 114.0 ],
					"text" : "host and port can be set using messages or (optional) patcher arguments\n\nthe default adress  is 127.0.0.1:7770"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-3",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 364.0, 265.0, 87.0, 22.0 ],
					"text" : "/invalidPath 42"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-17",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 364.0, 239.0, 79.0, 22.0 ],
					"text" : "/ui/allnotesoff"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-15",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 48.0, 239.0, 59.0, 22.0 ],
					"text" : "port 7770"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-13",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 48.0, 212.0, 85.0, 22.0 ],
					"text" : "host 127.0.0.1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-11",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 364.0, 212.0, 91.0, 22.0 ],
					"text" : "/midi 144 90 60"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-4",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 243.0, 211.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-2",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 48.0, 364.0, 191.0, 22.0 ],
					"text" : "mrp.osc 127.0.0.1 7770 @active 1"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"midpoints" : [ 373.5, 298.5, 57.5, 298.5 ],
					"source" : [ "obj-11", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"midpoints" : [ 57.5, 298.5, 57.5, 298.5 ],
					"source" : [ "obj-13", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"midpoints" : [ 57.5, 299.0, 57.5, 299.0 ],
					"source" : [ "obj-15", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"midpoints" : [ 373.5, 298.0, 57.5, 298.0 ],
					"source" : [ "obj-17", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-19", 0 ],
					"source" : [ "obj-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"midpoints" : [ 373.5, 298.0, 57.5, 298.0 ],
					"source" : [ "obj-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"midpoints" : [ 252.5, 299.5, 57.5, 299.5 ],
					"source" : [ "obj-4", 0 ]
				}

			}
 ],
		"dependency_cache" : [ 			{
				"name" : "mrp.osc.maxpat",
				"bootpath" : "~/Documents/Max 8/Projects/mrp.osc/patchers",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
			}
, 			{
				"name" : "validate_path.js",
				"bootpath" : "~/Documents/Max 8/Projects/mrp.osc/code",
				"patcherrelativepath" : "../code",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
