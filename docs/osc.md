# OSC

Important: all paths are prefixed with `/mrp`, everything else is ignored

## IP address and ports

- Default port: `7770`
- Default IP: `[localhost](http://localhost)` / `127.0.0.1`
- These can presumably be set using command line arguments to `./mrp`. Type `./mrp -h` or `./mrp --help` for a full list of options.

## Alphabetical paths index

```cpp
/midi: byte a, byte b, byte c // standard 3-byte MIDI messages e.g. 144 90 60
/pedal/damper: int value || float value // change damper value
/pedal/sostenuto: int value || float value // change sostenuto value
/ptrk/mute: [array int notes]
/ptrk/pitch: float freq, float amp
/quality/brightness: int midiChannel, int midiNote, float brightness // brightness is an independent map to harmonic content, reduced to a linear scale
/quality/intensity: int midiChannel, int midiNote, float intensity // intensity is a map to amplitude and harmonic content, relative to the current intensity
/quality/pitch: int midiChannel, int midiNote, float pitch // Frequency base is relative to the fundamental frequency of the MIDI note
/quality/pitch/vibrato: int midiChannel, int midiNote, float pitch // Frequency vibrato is a periodic modulation in frequency, zero-centered (+/-1 maps to range loaded from XML)
/quality/harmonic: int midiChannel, int midiNote, float harmonic // ?
/quality/harmonics/raw: int midiChannel, int midiNote, [array of float harmonics] // ?
/ui/allnotesoff // turn all current notes off
/ui/cal/save // Marked as LEGACY
/ui/cal/load // Marked as LEGACY
/ui/cal/phase: float p 
/ui/cal/volume: float v
/ui/cal/currentnote: int n // "Send a message announcing the current note, to update the UI"
/ui/gate // Marked as LEGACY
/ui/harmonic // Marked as LEGACY
/ui/patch/up // increment current program
/ui/patch/down // decrement current program
/ui/patch/set: int p // 0-N, set the current program to the given parameter
/ui/pianokey/calibrate/start
/ui/pianokey/calibrate/finish
/ui/pianokey/calibrate/abort
/ui/pianokey/calibrate/idle: // (?)
/ui/pianokey/calibrate/disable: [array int keys] // 0-127, disable specified keys
/ui/pianokey/calibrate/save: // only saves to `mrp-pb-calibration.txt`
/ui/pianokey/calibrate/load: // only loads from `mrp-pb-calibration.txt`
/ui/pianokey/calibrate/clear
/ui/status/keyboard: // get real-time calibration status (?)
/ui/tuning/global // Marked as LEGACY
/ui/tuning/stretch // Marked as LEGACY
/ui/volume: float vol // 0-1, >0.5 ? 4^((vol-0.5)/0.5) : 10^((vol-0.5)/0.5)
/ui/volume/raw: float vol // 0-1, set volume directly
```

## Paths by topic & source file, with notes

### `/midi`: MIDI notes

- `osccontroller.cpp` `OscController::handler`:

```cpp
/midi: byte a, byte b, byte c // standard 3-byte MIDI messages e.g. 144 90 60
```

### MIDI Over OSC Emulation

- `./mrp/source/main.cpp`
    - L493: `MidiController* mainMidiController = new MidiController(mainRender);`
    - L512: `useOscMidi = true` by default
    - L612: can also be turned off via CLI input while running
        
        ```cpp
        case 'z':
          useOsc = false;
        	useOscMidi = false;
        ```
        
    - L1091: OscController has a reference to the main MIDI controller and OscMIDI is on
        
        ```cpp
        oscController->setMidiController(mainMidiController); // Pass a reference to the MIDI controller
        oscController->setUseOscMidi(useOscMidi);
        ```
        
- OscController
    - `./mrp/source/osccontroller.h`
        - L62: `void setUseOscMidi(bool use) { useOscMidi_ = use; }`
        - L124: `bool useOscMidi_; // Whether we use OSC MIDI emulation`
    - `./mrp/source/osccontroller.cpp`
        - L72: `if (useOscMidi_) // OSC MIDI emulation` followed by a list of OSC paths:
            
            ```markdown
            /mrp/midi
            /mrp/quality/brightness
            /mrp/quality/intensity
            /mrp/quality/pitch
            /mrp/quality/pitch/vibrato
            /mrp/quality/harmonic
            /mrp/quality/harmonics/raw
            /mrp/volume
            /mrp/allnotesoff
            ```
            
        - L75: `/mrp/midi` sends off OSC message for parsing
            
            ```cpp
            if (!strcmp(path, "/mrp/midi") && argc >= 1) {
              if (types[0] == 'm')
                return handleMidi(argv[0]->m[1], argv[0]->m[2], argv[0]->m[3]);
            ```
            
        - L293: `OscController::handleMidi`
            
            ```cpp
            // Handle a MIDI message encapsulated by OSC.  This will be a standard 3-byte
            // message, and should be passed to the MIDI controller as if it originated from
            // a real MIDI device. Returns 0 on success (packet handled).
            
            int OscController::handleMidi(unsigned char byte1, unsigned char byte2, unsigned char byte3) {
                vector<unsigned char> midiMsg;
            
                if (midiController_ == NULL)
                    return 1;
            
                midiMsg.push_back(byte1);
                midiMsg.push_back(byte2);
                midiMsg.push_back(byte3);
            
                // FIXME: deltaTime
                midiController_->rtMidiCallback(0.0, &midiMsg, OSC_MIDI_CONTROLLER_NUM);
            
                return 0;
            }
            ```
            
- MidiController
    - `./mrp/source/midicontroller.cpp`
        - L964 `MidiController::rtMidiCallback`
            
            ```cpp
            // This gets called every time MIDI data becomes available on any input
            // controller.  deltaTime gives us the time since the last event on the same
            // controller, message holds a 3-byte MIDI message, and inputNumber tells us the
            // number of the device that triggered it (see main.cpp for how this number is
            // calculated).
            
            // For now, we don't store separate state for separate devices: we use standard
            // MIDI channels instead. channel 0 is the main (piano) keyboard, channel 1 the
            // first auxiliary keyboard, and so on.
            
            void MidiController::rtMidiCallback(double deltaTime, vector<unsigned char>* message, int inputNumber) {
            ...
            ```
            
    - `./mrp/source/midicontroller.h`
        - L74 various MIDI commands which match up with same in `./mrp/source/scanner_midi.h`
            
            ```cpp
            enum { // MIDI messages
                MESSAGE_NOTEOFF = 0x80,
                MESSAGE_NOTEON = 0x90,
                MESSAGE_AFTERTOUCH_POLY = 0xA0,
                MESSAGE_CONTROL_CHANGE = 0xB0,
                MESSAGE_PROGRAM_CHANGE = 0xC0,
                MESSAGE_AFTERTOUCH_CHANNEL = 0xD0,
                MESSAGE_PITCHWHEEL = 0xE0,
                MESSAGE_SYSEX = 0xF0,
                MESSAGE_SYSEX_END = 0xF7,
                MESSAGE_ACTIVE_SENSE = 0xFE,
                MESSAGE_RESET = 0xFF
            };
            
            enum { // Partial listing of MIDI controllers
                CONTROL_BANK_SELECT = 0,
                CONTROL_MODULATION_WHEEL = 1,
                CONTROL_VOLUME = 7,
                CONTROL_PATCH_CHANGER = 14, // Piano bar patch-changing interface (deprecate this?)
                CONTROL_AUX_PEDAL = 15, // Use this as an auxiliary pedal
                CONTROL_MRP_BASE = 16, // Base of a range of controllers used by MRP signal
                                       // routing hardware
                CONTROL_BANK_SELECT_LSB = 32,
                CONTROL_MODULATION_WHEEL_LSB = 33,
                CONTROL_VOLUME_LSB = 39,
                CONTROL_DAMPER_PEDAL = 64,
                CONTROL_SOSTENUTO_PEDAL = 66,
                CONTROL_SOFT_PEDAL = 67,
                CONTROL_ALL_SOUND_OFF = 120,
                CONTROL_ALL_CONTROLLERS_OFF = 121,
                CONTROL_LOCAL_KEYBOARD = 122,
                CONTROL_ALL_NOTES_OFF = 123,
                CONTROL_OMNI_OFF = 124,
                CONTROL_OMNI_ON = 125,
                CONTROL_MONO_OPERATION = 126,
                CONTROL_POLY_OPERATION = 127
            };
            
            enum { // Piano damper states (excluding effect of damper pedal)
                DAMPER_DOWN = 0, // Not lifted
                DAMPER_KEY = 1, // Lifted by key
                DAMPER_SOSTENUTO = 2 // Held by sostenuto pedal
                                     // Key and Sostenuto: 3
            };
            ```
            

### `/quality`: real-time note timbre parameters

- `osccontroller.cpp` `OscController::handler`:

```cpp
/quality/brightness: int midiChannel, int midiNote, float brightness // brightness is an independent map to harmonic content, reduced to a linear scale
/quality/intensity: int midiChannel, int midiNote, float intensity // intensity is a map to amplitude and harmonic content, relative to the current intensity
/quality/pitch: int midiChannel, int midiNote, float pitch // Frequency base is relative to the fundamental frequency of the MIDI note
/quality/pitch/vibrato: int midiChannel, int midiNote, float pitch // Frequency vibrato is a periodic modulation in frequency, zero-centered (+/-1 maps to range loaded from XML)
/quality/harmonic: int midiChannel, int midiNote, float harmonic // ?
/quality/harmonics/raw: int midiChannel, int midiNote, [array of float harmonics] // ?
```

### `/ui`: various interfaces

- Interfaces for KeyScanner calibration, patch navigation, tuning and volume settings, etc
- `pianobar.cpp` `ContinuousKeyController::setOscController`:
    
    ```cpp
    /ui/pianokey/calibrate/start
    /ui/pianokey/calibrate/finish
    /ui/pianokey/calibrate/abort
    /ui/pianokey/calibrate/idle: // (?)
    /ui/pianokey/calibrate/disable: [array int keys] // 0-127, disable specified keys
    /ui/pianokey/calibrate/save: // only saves to `mrp-pb-calibration.txt`
    /ui/pianokey/calibrate/load: // only loads from `mrp-pb-calibration.txt`
    /ui/pianokey/calibrate/clear
    /ui/status/keyboard: // get real-time calibration status (?)
    ```
    
- `midicontroller.cpp` `MidiController::setOscController`:
    
    ```cpp
    /ui/patch/up // increment current program
    /ui/patch/down // decrement current program
    /ui/patch/set: int p // 0-N, set the current program to the given parameter
    /ui/allnotesoff // turn all current notes off
    /ui/cal/save // Marked as LEGACY
    /ui/cal/load // Marked as LEGACY
    /ui/harmonic // Marked as LEGACY
    /ui/gate // Marked as LEGACY
    /ui/tuning/global // Marked as LEGACY
    /ui/tuning/stretch // Marked as LEGACY
    ```
    
- `audiorender.cpp` `AudioRender::setOscController`:
    
    ```cpp
    /ui/volume: float vol // 0-1, >0.5 ? 4^((vol-0.5)/0.5) : 10^((vol-0.5)/0.5)
    /ui/volume/raw: float vol // 0-1, set volume directly
    ```
    
- `note.cpp` `CalibratorNote::setOscController`:
    
    > This class implements a calibration note. The differences from MidiNote are:
    > 
    > 
    > (1) It is monophonic: a new note coming in of this type will stop the old
    > one
    > 
    > (2) It listens to a pair of MIDI controllers to change the phase offset
    > and amplitude of the current note 
    > 
    > (3) It can write these values to a special XML file that is loaded on startup 
    > 
    > (4) It does not need any Synth parameters; one internal synth is loaded automatically
    > 
    
    ```cpp
    /ui/cal/phase: float p 
    /ui/cal/volume: float v
    /ui/cal/currentnote: int n // "Send a message announcing the current note, to update the UI"
    ```
    

### `/pedal`: MIDI expression pedal

- `midicontroller.cpp` `MidiController::setOscController`:
    
    ```cpp
    /pedal/damper: int value || float value // change damper value
    /pedal/sostenuto: int value || float value // change sostenuto value
    ```
    

### `/ptrk`: pitch-tracking for PLL Synth

- `pitchtrack.cpp` `PitchTrackController::setOscController`
    
    > This class handles all the central dispatching related to tracking an incoming pitch.  Note that the actual tracking takes place externally, with the messages arriving via OSC.  The functions performed by this class include:
    > 
    > - Parsing pieces of the XML patch table related to pitch-tracking
    > - Allocating new notes and releasing old ones
    > - Routing incoming pitch and amplitude messages to the appropriate notes
    
    ```cpp
    /ptrk/pitch: float freq, float amp
    /ptrk/mute: [array int notes]
    ```
    

### misc

- `osccontroller.cpp` `OscController::handler`:
    
    ```cpp
    /volume: float volume // set global amplitude of audio engine
    /allnotesoff // turn off all notes
    ```