"""
Authors:
  Victor Shepardson
  Jack Armitage
  Intelligent Instruments Lab 2022
"""

"""
TODO:
- support relative updating of lists of qualities
- add qualities descriptions as comments/help
- qualities_update([note arr], qualities with arr)
- add more tests
- add timer to turn off notes after 90s
- custom max/min ranges for qualities
- harmonics_raw dict and functions
- add simulator via sc3 lib
- remove mido
- rename harmonic -> harmonic_sweep and add harmonic(note, partial, amplitude)
"""

import time
import math
import numpy as np
import copy
from datetime import datetime

from .thermal import *

NOTE_ON = True
NOTE_OFF = False

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

class MRP:
    def __init__(self, osc, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        self.default_settings = {
            'address': {
                'port': 7770,
                'ip': '127.0.0.1'
            },
            'voices': {
                'max': 16, # for 16 cables
                'rule': 'oldest' # oldest, lowest, highest, quietest...
            },
            'channel': 15, # real-time midi note ch (0-indexed)
            'range': { 'start': 21, 'end': 128 }, # MIDI for piano keys 0-88
            'qualities_max': 1.0,
            'qualities_min': 0.0,
            'heat_monitor': False
        }
        self.settings = kwargs.get('settings', self.default_settings)
        self.note_on_hex = 0x9F
        self.note_off_hex = 0x8F
        self.print('MRP starting with settings:', self.settings)

        # OSC reference and paths
        self.osc = osc
        if self.osc.get_client_by_name("mrp") is None:
            self.print(f"MRP OSC client not found, creating one at {self.settings['address']['ip']}:{self.settings['address']['port']}")
            self.osc.create_client("mrp", self.settings['address']['ip'], self.settings['address']['port'])
        self.osc_paths = {
            'midi': '/mrp/midi',
            'qualities': {
                'brightness':    '/mrp/quality/brightness',
                'intensity':     '/mrp/quality/intensity',
                'pitch':         '/mrp/quality/pitch',
                'pitch_vibrato': '/mrp/quality/pitch/vibrato',
                'harmonic':      '/mrp/quality/harmonic',
                'harmonics_raw': '/mrp/quality/harmonics/raw'
            },
            'pedal': {
                'damper':    '/mrp/pedal/damper',
                'sostenuto': '/mrp/pedal/sostenuto'
            },
            'misc': {
                'allnotesoff': '/mrp/allnotesoff'
            },
            'ui': {
                'volume':     '/ui/volume', # float vol // 0-1, >0.5 ? 4^((vol-0.5)/0.5) : 10^((vol-0.5)/0.5)
                'volume_raw': '/ui/volume/raw' # float vol // 0-1, set volume directly
            }
        }
        # internal state
        self.notes = [] # state of each real-time midi note
        self.note = { # template note
            'channel': self.settings['channel'],
            'status': NOTE_OFF,
            'midi': {
                'number': 0, # MIDI note number, not piano key number
                'velocity': 0, # not in use by MRP PLL synth
                'aftertouch_poly': 0, # not in use by MRP PLL synth
                'aftertouch_channel': 0, # not in use by MRP PLL synth
                'pitch_bend': 0 # not in use by MRP PLL synth
            },
            'qualities': {
                'brightness': 0,
                'intensity': 0,
                'pitch': 0,
                'pitch_vibrato': 0,
                'harmonic': 0,
                'harmonics_raw': []
            }
        }
        self.voices = [] # active notes indexed chronologically
        self.pedal = {
            'damper': 0,
            'sostenuto': 0
        }
        self.ui = {
            'volume': 0,
            'volume_raw': 0
        }
        self.program = 0 # current program (see MRP XML)
        # init sequence
        self.init_notes()
        if self.settings['heat_monitor'] is True:
            self.heat_monitor = MRPHeatMonitor(self)
        self.note_names = {
            "a0": 21, "as0": 22, "b0": 23,
            "c1": 24, "cs1": 25, "d1": 26, "ds1": 27, "e1": 28, "f1": 29, "fs1": 30, "g1": 31, "gs1": 32, "a1": 33, "as1": 34, "b1": 35,
            "c2": 36, "cs2": 37, "d2": 38, "ds2": 39, "e2": 40, "f2": 41, "fs2": 42, "g2": 43, "gs2": 44, "a2": 45, "as2": 46, "b2": 47,
            "c3": 48, "cs3": 49, "d3": 50, "ds3": 51, "e3": 52, "f3": 53, "fs3": 54, "g3": 55, "gs3": 56, "a3": 57, "as3": 58, "b3": 59,
            "c4": 60, "cs4": 61, "d4": 62, "ds4": 63, "e4": 64, "f4": 65, "fs4": 66, "g4": 67, "gs4": 68, "a4": 69, "as4": 70, "b4": 71,
            "c5": 72, "cs5": 73, "d5": 74, "ds5": 75, "e5": 76, "f5": 77, "fs5": 78, "g5": 79, "gs5": 80, "a5": 81, "as5": 82, "b5": 83,
            "c6": 84, "cs6": 85, "d6": 86, "ds6": 87, "e6": 88, "f6": 89, "fs6": 90, "g6": 91, "gs6": 92, "a6": 93, "as6": 94, "b6": 95,
            "c7": 96, "cs7": 97, "d7": 98, "ds7": 99, "e7": 100, "f7": 101, "fs7": 102, "g7": 103, "gs7": 104, "a7": 105, "as7": 106, "b7": 107,
            "c8": 108, "cs8": 109, "d8": 110, "ds8": 111, "e8": 112, "f8": 113, "fs8": 114, "g8": 115, "gs8": 116, "a8": 117, "as8": 118, "b8": 119,
            "c9": 120, "cs9": 121, "d9": 122, "e9": 123, "f9": 124, "fs9": 125, "g9": 126, "gs9": 127, "a9": 128
        }

        if kwargs.get('record', False):
            self.recording_filename = kwargs.get('file', None)
            self.record_start()

    def monitor(self):
        if self.settings['heat_monitor'] is True:
            self.heat_monitor()

    def init_notes(self):
        """
        initialise an array of notes in NOTE_OFF state,
        equal in length to the number of piano keys in use
        """
        self.notes = []
        piano_keys = self.settings['range']['end'] - \
                     self.settings['range']['start'] + 1 # inclusive
        for k in range(piano_keys):
            note = self.note_create(
                self.settings['range']['start'] + k, # MIDI note numbers
                0
            )
            self.notes.append(note)
        self.print(len(self.notes), 'notes created.')

    """
    /mrp/midi
    """
    def note_on(self, note, velocity=1, channel=None):
        """
        check if note on is valid
        add it as an active voice
        construct a Note On message & send over OSC
        """
        if self.note_on_is_valid(note) == True:
            self.voices_add(note)
            if channel is None:
                channel = self.settings['channel']
            tmp = self.notes[self.note_index(note)]
            tmp['status'] = NOTE_ON
            tmp['channel'] = channel
            tmp['midi']['velocity'] = velocity
            path = self.osc_paths['midi']
            self.print(path, 'Note On:', note, ', Velocity:', velocity)
            self.send(path, self.note_on_hex, note, velocity, client="mrp")
            return tmp
        else:
            self.print('note_on(): invalid Note On', note)
            return None

    def note_off(self, note, velocity=0, channel=None):
        """
        check if note off is valid
        remove it as an active voice
        construct a Note Off message & send over OSC
        """
        if self.note_off_is_valid(note) == True:
            if note in self.voices:
                self.voices_remove(note)
            if channel is None:
                channel = self.settings['channel']
            tmp = self.notes[self.note_index(note)]
            tmp['status'] = NOTE_OFF
            tmp['channel'] = channel
            tmp['midi']['velocity'] = velocity
            path = self.osc_paths['midi']
            self.print(path, 'Note Off:', note)
            self.send(path, self.note_off_hex, note, velocity, client="mrp")
            return tmp
        else:
            self.print('note_off(): invalid Note Off', note)
            return None

    def notes_on(self, notes, velocities=None):
        vmax = self.settings['voices']['max']
        if len(notes)+1 > vmax:
            if velocities == None:
                [self.note_on(n) for n in notes]
            else:
                [self.note_on(n, velocities[i]) for i,n in enumerate(notes)]
        else:
            print('notes_on(): too many notes', notes)

    def notes_off(self, notes, channel=None):
        [self.note_off(n) for n in notes]
    
    # def control_change(self, controller, value, channel=None):
    #     """
    #     construct MIDI CC message & send over OSC
    #     """
    #     if channel is None:
    #         channel = self.settings['channel']
    #     m = mido.Message(
    #         'control_change',
    #         channel=channel,
    #         controller=controller,
    #         value=value
    #     )
    #     path = self.osc_paths['midi']
    #     self.print(path, 'Control Change:', *m.bytes())
    #     self.send(path, *m.bytes(), client="mrp")

    # def program_change(self, program, channel=None):
    #     """
    #     update program state
    #     construct MIDI program change message 
    #     & send over OSC
    #     """
    #     if channel is None:
    #         channel = self.settings['channel']
    #     self.program = program
    #     m = mido.Message(
    #         'program_change',
    #         channel=channel,
    #         program=program
    #     )
    #     path = self.osc_paths['midi']
    #     self.print(path, 'Program Change:', *m.bytes())
    #     self.send(path, *m.bytes(), client="mrp")
    
    """
    /mrp/qualities
    """
    def set_note_quality(self, note: int, quality: str, value: float, relative=False, channel=None):
        """
        Set a note's quality to a new value.

        Example
            set_note_quality(48, 'brightness', 0.5)

        Args
            note (int): MIDI note number
            quality (string): name of quality to update, must be same as key in osc_paths
            value (float): value of quality
            relative (bool): replace the value or add it to the current value
            channel (int): which MIDI channel to send on
        """
        if isinstance(quality, str):
            if self.note_msg_is_valid(note) == True:
                if channel is None:
                    channel = self.settings['channel']
                tmp = self.notes[self.note_index(note)]
                if isinstance(value, list) or isinstance(value, np.ndarray): # e.g. /harmonics/raw
                    if relative is True:
                        self.print('set_note_quality(): relative updating of lists not supported')
                        # if (len(tmp['qualities'][quality]) > 0):
                        #     for i, q in enumerate(tmp['qualities'][quality]):
                        #         tmp['qualities'][quality][i] += self.quality_clamp(value[i])
                        #         value.pop(i)
                        #     for i, v in enumerate(value):
                        #         tmp['qualities'][quality].append(value[i])
                        # else:
                        #     tmp['qualities'][quality] = [self.quality_clamp(v) for v in value]
                    else:
                        tmp['qualities'][quality] = [self.quality_clamp(v) for v in value]
                    path = self.osc_paths['qualities'][quality]
                    self.print(path, channel, note, *tmp['qualities'][quality])
                    self.send(path, channel, note, *tmp['qualities'][quality], client="mrp")
                    return tmp
                else:
                    if relative is True:
                        tmp['qualities'][quality] = self.quality_clamp(value + tmp['qualities'][quality])
                    else:
                        tmp['qualities'][quality] = self.quality_clamp(value)
                    path = self.osc_paths['qualities'][quality]
                    self.print(path, channel, note, tmp['qualities'][quality])
                    self.send(path, channel, note, tmp['qualities'][quality], client="mrp")
                    return tmp
            else:
                self.print('set_note_quality(): invalid message:', quality, note, value)
                return None
        else:
            self.print('set_note_quality(): "quality" is not a string:', quality)
            return None

    def set_quality(self, quality, value, relative=False, channel=None):
        """
        Update quality of all active notes to a new value.

        Example
            set_quality('brightness', 0.5)
        
        Args
            quality (string): name of quality to update, must be same as key in osc_paths
            value (float): value of quality
            relative (bool): replace the value or add it to the current value
            channel (int): which MIDI channel to send on
        """
        if isinstance(quality, str):
            active_notes = self.note_on_numbers()
            changed_notes = []
            for note in active_notes:
                changed_note = self.set_note_quality(self, note, quality, value, relative, channel)
                changed_notes.append(changed_note)
            return changed_notes
        else:
            print('quality_update(): "quality" is not a string:', quality)
            return None

    def set_note_qualities(self, note, qualities, relative=False, channel=None):
        """
        Update a note's qualities to a new set of values.

        Example
            set_note_qualities(48, {
                'brightness': 0.5,
                'intensity': 0.6,
                'harmonics_raw': [0.2, 0.3, 0.4]
            })
        
        Args
            note (int): MIDI note number
            qualities (dict): dict of qualities in key (string):value (float) pairs to update, 
                              must be same as key in osc_paths
            relative (bool): replace the value or add it to the current value
            channel (int): which MIDI channel to send on
        """
        if isinstance(qualities, dict):
            if self.note_msg_is_valid(note) == True:
                if channel is None:
                    channel = self.settings['channel']
                tmp = self.notes[self.note_index(note)]
                for q, v in qualities.items():
                    if isinstance(v, list) or isinstance(v, np.ndarray): # e.g. /harmonics/raw
                        if relative is True:
                            self.print('quality_update(): relative updating of lists not supported')
                        else:
                            tmp['qualities'][q] = [self.quality_clamp(i) for i in v]
                        path = self.osc_paths['qualities'][q]
                        self.print(path, channel, note, *tmp['qualities'][q])
                        self.send(path, channel, note, *tmp['qualities'][q], client="mrp")
                    else:
                        if relative is True:
                            tmp['qualities'][q] = self.quality_clamp(v, tmp['qualities'][q])
                        else:
                            tmp['qualities'][q] = self.quality_clamp(v)
                        path = self.osc_paths['qualities'][q]
                        self.print(path, channel, note, tmp['qualities'][q])
                        self.send(path, channel, note, tmp['qualities'][q], client="mrp")
                return tmp
            else:
                self.print('quality_update(): invalid message:', note, qualities)
                return None
        else:
            self.print('quality_update(): "qualities" is not an object:', note, qualities)
            return None

    def set_qualities(self, qualities, relative=False, channel=None):
        """
        Update the qualities for all active notes to a new set of values.
        
        Example
            set_qualities({
                'brightness': 0.5,
                'intensity': 0.6,
                'harmonics_raw': [0.2, 0.3, 0.4]
            })
        
        Args
            qualities (dict): dict of qualities in key (string):value (float) pairs to update, 
                              must be same as key in osc_paths
            relative (bool): replace the value or add it to the current value
            channel (int): which MIDI channel to send on
        """
        if isinstance(qualities, dict):
            active_notes = self.note_on_numbers()
            changed_notes = []
            for note in active_notes:
                changed_note = self.qualities_update(self, qualities, relative, channel)
                changed_notes.append(changed_note)
            return changed_notes
        else:
            print('quality_update(): "qualities" is not an object:', note, qualities)
            return None

    def get_note_quality(self, note:int, quality:str) -> float:
        """
        Return the value of a note's quality.

        Example
            get_note_quality(48, 'brightness')
        
        Args
            note (int): MIDI note number
            quality (string): name of quality to get, must be same as key in osc_paths

        Returns
            float: value of quality
        """
        return self.notes[self.note_index(note)]['qualities'][quality]

    def get_note_qualities(self, note:int) -> dict:
        """
        Return the values of a note's qualities.

        Example
            get_note_qualities(48)
        
        Args
            note (int): MIDI note number

        Returns
            dict: dict of qualities in key (string):value (float) pairs
        """
        return self.notes[self.note_index(note)]['qualities']
    
    def get_quality(self, quality:str) -> dict:
        """
        Return values of a quality for all active notes.

        Example
            get_quality('brightness')
        
        Args
            quality (string): name of quality to get, must be same as key in osc_paths

        Returns
            dict: note:quality in key (int):value (float) pairs
        """
        active_notes = self.note_on_numbers()
        return {n:self.get_note_quality(n, quality) for n in active_notes}
    
    def get_qualities(self) -> dict:
        """
        Return values of all qualities for all active notes.

        Example
            get_qualities()
        
        Returns
            dict: note:qualities in key (int):value (dict) pairs
        """
        active_notes = self.note_on_numbers()
        return {n:self.get_note_qualities(n) for n in active_notes}

    """
    /mrp/pedal
    """
    def pedal_sostenuto(self, sostenuto):
        """
        set pedal sostenuto value
        """
        self.pedal.sostenuto = sostenuto
        path = self.osc_paths['pedal']['sostenuto']
        self.print(path, sostenuto)
        self.send(path, sostenuto, client="mrp")

    def pedal_damper(self, damper):
        """
        set pedal damper value
        """
        self.pedal.damper = damper
        path = self.osc_paths['pedal']['damper']
        self.print(path, damper)
        self.send(path, damper, client="mrp")

    """
    /mrp/* miscellaneous
    """
    def all_notes_off(self):
        """
        turn all notes off
        """
        path = self.osc_paths['misc']['allnotesoff']
        self.print(path)
        self.send(path, client="mrp")
        self.init_notes()
        self.voices_reset()

    """
    /mrp/ui
    """
    def ui_volume(self, value):
        """
        float vol // 0-1, >0.5 ? 4^((vol-0.5)/0.5) : 10^((vol-0.5)/0.5)
        """
        self.ui.volume = value
        path = self.osc_paths['ui']['volume']
        self.print(path, value)
        self.send(path, value, client="mrp")

    def ui_volume_raw(self, value):
        """
        float vol // 0-1, set volume directly
        """
        self.ui.volume_raw = value
        path = self.osc_paths['ui']['volume_raw']
        self.print(path, value)
        self.send(path, value, client="mrp")

    """
    note methods
    """
    def note_create(self, n, velocity, channel=None):
        """
        create and return a note object
        """
        if channel is None:
            channel = self.settings['channel']
        note = copy.deepcopy(self.note)
        note['midi']['number'] = n
        note['midi']['velocity'] = velocity
        return note

    def note_is_in_range(self, note):
        """
        check if a note is in valid range
        """
        start = self.settings['range']['start']
        end = self.settings['range']['end']
        if start > note or note > end:
            return False
        return True

    def note_is_off(self, note):
        """
        check if a note is off
        """
        index = note - self.settings['range']['start']
        if self.notes[index]['status'] == NOTE_ON:
            return False
        return True

    def note_index(self, note):
        return note - self.settings['range']['start']

    def note_on_numbers(self):
        """
        return numbers of notes that are on
        """
        return [
            note['midi']['number'] 
            for note in self.notes 
            if note['status']==NOTE_ON]

    def note_on_is_valid(self, note):
        """
        check if the note is on & in range
        """
        if self.note_is_in_range(note) == True:
            if self.note_is_off(note) == True:
                return True
            else:
                self.print('note_on_is_valid(): note', note, 'is already on')
                return False
        else:
            self.print('note_on_is_valid(): note', note, 'out of range')
            return False    

    def note_off_is_valid(self, note):
        """
        check if the note is off & in range
        """
        if self.note_is_off(note) == False:
            if self.note_is_in_range(note) == True:
                return True
            else:
                self.print('note_off_is_valid(): note', note, 'out of range')
                return False
        else:
            self.print('note_off_is_valid(): note', note, 'is already off')
            return False

    def note_msg_is_valid(self, note):
        return self.note_off_is_valid(note)

    """
    qualities methods
    """
    def quality_clamp(self, value):
        ### NOTE pitch, at least, can be negative or > 1
        return float(value)
        # return float(clamp(value, self.settings['qualities_min'], self.settings['qualities_max']))

    """
    voice methods
    """
    def voices_add(self, note):
        """
        add voices up to the maximum
        then replace voices based on the rule
        """
        if note in self.voices:
            self.print('voices_add(): note already active')
            return self.voices
        if self.voices_count() < self.settings['voices']['max']:
            self.voices.append(note)
        else:
            rule = self.settings['voices']['rule']
            match rule:
                case 'oldest':
                    oldest = self.voices[0]
                    self.print('voices_add(): removing oldest', oldest)
                    self.voices.pop(0)
                    self.voices.append(note)
                    self.note_off(oldest)
                    return self.voices
                case _: # lowest, highest, quietest, ...
                    return self.voices
        return self.voices

    def voices_remove(self, note):
        self.voices.remove(note)
        return self.voices

    def voices_update(self):
        """
        reconstruct active voices list based on self.notes
        """
        self.voices = self.note_on_numbers()
        return self.voices

    def voices_compare(self):
        """
        check if voices and notes match
        """
        note_on_numbers = self.note_on_numbers()
        return note_on_numbers == self.voices, {'notes': note_on_numbers}, {'voices': self.voices}

    def voices_reset(self):
        self.voices = []

    def voices_count(self):
        return len(self.voices)

    def voices_position(self, note):
        """
        return position of a note in voice queue
        """
        if note in self.voices:
            return self.voices.index(note)
        else:
            self.print('voices_note_age(): note', note, 'is off')
            return -1

    '''
    Getter utils
    '''
        
    def get_notes_on(self):
        return [n['midi']['number'] for n in self.notes if n['status']==NOTE_ON]
    
    def get_notes_status(self):
        # return a dict of midi_number:status for all notes:
        return {n['midi']['number']:n['status'] for n in self.notes}
    
    def get_notes_harmonics(self):
        return {n['midi']['number']:n['qualities']['harmonics_raw'] for n in self.notes}

    """
    logging
    """

    def send(self, *args, **kwargs):
        """
        wrapped osc.send to handle logging
        """
        self.osc.send(*args, **kwargs)
        if self.osc.log.recording:
            self.log(*args)

    def log(self, *args):
        """
        Examples:
            0.00336 /mrp/allnotesoff
            0.50414 /mrp/midi iii 159 48 1
            1.30600 /mrp/quality/harmonics/raw iifff 15 48 0.03 0.0 0.0
            2.81722 /mrp/quality/intensity iif 15 70 0 
            3.00336 /mrp/allnotesoff
        """
        tag = self.osc.log.type_tag(args[1:])
        args = [self.t(), args[0], tag] + list(args[1:])
        self.osc.log(self.osc_args_to_log_str(args))

    def osc_args_to_log_str(self, arr: list) -> str:
        return ' '.join([f'{x:.5f}' if isinstance(x, float) else str(x) for x in arr])

    def record_start(self):
        if self.recording_filename is None:
            self.recording_filename = f"iimrp-recording_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        self.start_time = time.time()
        self.t = lambda: time.time() - self.start_time
        self.osc.log.record_start(self.recording_filename)
        print(f"[iimrp] Recording started")

    """
    misc methods
    """
    def cleanup(self):
        print('MRP exiting...')
        self.all_notes_off()

    def print(self, *a, **kw):
        """verbose debug printing"""
        if self.verbose: print(*a, **kw)

    def midi_to_freq(self, midi_note):
        """
        Convert a MIDI note number to its frequency in Hertz.
        """
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

    def freq_to_midi(self, freq):
        """
        Convert a frequency in Hertz to the closest MIDI note number.
        """
        return 69 + 12 * math.log2(freq / 440.0)

    def note_name_to_midi(self, note_name):
        """
        Convert a musical note name (e.g., C4, A#3, etc.) to its MIDI note number.
        """
        return self.note_names[note_name]

    def midi_to_note_name(self, midi_note):
        """
        Convert a MIDI note number to its musical note name.
        """
        for note, value in self.note_names.items():
            if value == midi_note:
                return note

    def midi_notes_to_freqs(self, midi_notes):
        """
        Convert a list of MIDI note numbers to their frequencies in Hertz.
        """
        return [self.midi_to_freq(n) for n in midi_notes]
    
    def freqs_to_midi_notes(self, freqs):
        """
        Convert a list of frequencies in Hertz to the closest MIDI note numbers.
        """
        return [self.freq_to_midi(f) for f in freqs]
    
    def note_names_to_midi_notes(self, note_names):
        """
        Convert a list of musical note names to their MIDI note numbers.
        """
        return [self.note_name_to_midi(n) for n in note_names]
    
    def midi_notes_to_note_names(self, midi_notes):
        """
        Convert a list of MIDI note numbers to their musical note names.
        """
        return [self.midi_to_note_name(n) for n in midi_notes]
