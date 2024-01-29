outlets = 2;

var valid_paths = [
	"/midi", // byte a, byte b, byte c // standard 3-byte MIDI messages e.g. 144 90 60
	"/pedal/damper", // int value || float value // change damper value
	"/pedal/sostenuto", // int value || float value // change sostenuto value
	"/ptrk/mute", // [array int notes]
	"/ptrk/pitch", // float freq, float amp
	"/quality/brightness", // int midiChannel, int midiNote, float brightness // brightness is an independent map to harmonic content, reduced to a linear scale
	"/quality/intensity", // int midiChannel, int midiNote, float intensity // intensity is a map to amplitude and harmonic content, relative to the current intensity
	"/quality/pitch", // int midiChannel, int midiNote, float pitch // Frequency base is relative to the fundamental frequency of the MIDI note
	"/quality/pitch/vibrato", // int midiChannel, int midiNote, float pitch // Frequency vibrato is a periodic modulation in frequency, zero-centered (+/-1 maps to range loaded from XML)
	"/quality/harmonic", //  int midiChannel, int midiNote, float harmonic // ?
	"/quality/harmonics/raw", // int midiChannel, int midiNote, [array of float harmonics] // ?
	"/ui/allnotesoff", // turn all current notes off
	"/ui/cal/save", // Marked as LEGACY
	"/ui/cal/load", // Marked as LEGACY
	"/ui/cal/phase", // float p
	"/ui/cal/volume", // float v
	"/ui/cal/currentnote", // int n // "Send a message announcing the current note, to update the UI"
	"/ui/gate", // Marked as LEGACY
	"/ui/harmonic", // Marked as LEGACY
	"/ui/patch/up", // increment current program
	"/ui/patch/down", // decrement current program
	"/ui/patch/set", //: int p // 0-N, set the current program to the given parameter
	"/ui/pianokey/calibrate/start",
	"/ui/pianokey/calibrate/finish",
	"/ui/pianokey/calibrate/abort",
	"/ui/pianokey/calibrate/idle", // (?)
	"/ui/pianokey/calibrate/disable", //: [array int keys] // 0-127, disable specified keys
	"/ui/pianokey/calibrate/save",// only saves to `mrp-pb-calibration.txt`
	"/ui/pianokey/calibrate/load", // only loads from `mrp-pb-calibration.txt`
	"/ui/pianokey/calibrate/clear",
	"/ui/status/keyboard", // get real-time calibration status (?)
	"/ui/tuning/global", // Marked as LEGACY
	"/ui/tuning/stretch", // Marked as LEGACY
	"/ui/volume", //:  float vol // 0-1, >0.5 ? 4^((vol-0.5)/0.5) : 10^((vol-0.5)/0.5)
	"/ui/volume/raw", //: float vol // 0-1, set volume directly
	];

function anything()
{
	var a = arrayfromargs(messagename, arguments);
	if (valid_paths.indexOf(a[0]) >= 0) {
		outlet(0, a);
	} else {
		outlet(1, "invalid path: " + a[0]);
	}
}