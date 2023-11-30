'''
Functions for calculating harmonics and harmonic series suitable for interfacing with the MRP.

TODO: Calculate f0 pitch-bend to go from harmonic to frequency (review MRP API)
TODO: nearest harmonics: for a given frequency and a set of notes, find nearest multiples of f0
'''

import numpy as np
np.set_printoptions(suppress=True)

def create_harmonics(H:int, N:int=88, A0_freq:float=27.5) -> np.array:
    """Create a 2D array of harmonics for a piano with N keys.

    Args:
        H (int): Number of harmonics to create.
        N (int): Number of piano notes (default=88).
        A0_freq (float): Frequency of note A0 (default=27.5).

    Returns:
        np.array: 2D array of harmonics.
    """
    # The ratio between the frequencies of two adjacent notes in a chromatic scale
    chromatic_ratio = 2 ** (1 / 12)
    note_indices = np.arange(N) # Create an array of note indices
    note_frequencies = A0_freq * (chromatic_ratio ** note_indices) # Calculate the frequencies of the notes
    harmonic_indices = np.arange(1, H + 1) # Create an array of harmonic indices
    harmonics = note_frequencies[:, np.newaxis] * harmonic_indices # Calculate the frequencies of the harmonics
    return harmonics

MAX_HARMONICS = 8
piano_harmonics = create_harmonics(MAX_HARMONICS)

def find_harmonic(frequency:float, A0_note:int=21) -> np.array:
    """Find the nearest harmonic for a given frequency.

    Args:
        frequency (float): Frequency to find the nearest harmonic for.
        A0_note (int, optional): MIDI note number for A0. Defaults to 21.

    Returns:
        np.array: Array containing the MIDI note number, harmonic index, and frequency of the nearest harmonic.
    """
    harmonics = piano_harmonics # Get the global 2D array of harmonics
    # Calculate the absolute differences between the harmonics and the input frequency
    differences = np.abs(harmonics - frequency)
    # Find the index of the minimum difference
    note_index, harmonic_index = np.unravel_index(np.argmin(differences), differences.shape)
    # Convert the note index to a MIDI note number and the harmonic index to a 1-based index
    midi_note_number = note_index + A0_note # MIDI note number for A0 is 21
    nearest_harmonic = harmonics[note_index, harmonic_index] # Get the nearest harmonic
    return np.array([midi_note_number, harmonic_index + 1, nearest_harmonic])

def find_nearest_harmonics(frequency:float, H:int, sort:str="frequency") -> np.array:
    """Find the H nearest harmonics for a given frequency.

    Args:
        frequency (float): Frequency to find the nearest harmonics for.
        H (int): Number of harmonics to find.
        sort (str, optional): Sort the results by "note", "harmonic", or "frequency". Defaults to "frequency".

    Returns:
        np.array: Array containing the MIDI note number, harmonic index, and frequency of the nearest harmonics.
    """
    harmonics = piano_harmonics # Get the global 2D array of harmonics
    # Calculate the absolute differences between the harmonics and the input frequency
    differences = np.abs(harmonics - frequency)
    # Get the indices of the H smallest differences
    indices = np.argpartition(differences, H, axis=None)[:H]
    # Convert the indices to 2D indices
    note_indices, harmonic_indices = np.unravel_index(indices, differences.shape)
    # Convert the note indices to MIDI note numbers
    midi_note_numbers = note_indices + 21  # MIDI note number for A0 is 21
    # Create a 2D array of the results
    results = np.column_stack((midi_note_numbers, harmonic_indices + 1, harmonics[note_indices, harmonic_indices]))
    # Sort the results
    sort_index = {"note": 0, "harmonic": 1, "frequency": 2}.get(sort, 2)
    results = results[results[:, sort_index].argsort()]
    return results

def create_single_harmonic_gain_array(index:int, gain:float=1.0, N:int=MAX_HARMONICS) -> np.array:
    """Create an array of harmonic gains with a single non-zero value.

    Args:
        index (int): Index of the harmonic to set.
        gain (float, optional): Gain of the harmonic. Defaults to 1.0.
        N (int, optional): Length of the array. Defaults to MAX_HARMONICS.

    Returns:
        np.array: Array of harmonic gains.
    """
    harmonics = np.zeros(N) # Create an array of zeros with length N
    # Set the value at the harmonic index to the gain
    harmonics[index - 1] = gain  # Subtract 1 because numpy arrays are 0-indexed
    return harmonics

def get_harmonic_gain_arrays(nearest_harmonics:np.ndarray, gain:float=1.0, N:int=MAX_HARMONICS) -> np.array:
    """Get an array of harmonic gain arrays for a given array of nearest harmonics.

    Args:
        nearest_harmonics (np.ndarray): Array of nearest harmonics.
        gain (float, optional): Gain of the harmonics. Defaults to 1.0.
        N (int, optional): Length of the harmonic gain arrays. Defaults to MAX_HARMONICS.

    Returns:
        np.array: Array of harmonic gain arrays.
    """
    harmonic_gain_arrays = [] # Initialize an empty list to store the arrays
    # For each row in the nearest harmonics array
    for row in nearest_harmonics:
        harmonic_index = int(row[1]) # Get the harmonic index
        # Create the harmonic gain array
        harmonic_gain_array = create_single_harmonic_gain_array(harmonic_index, gain, N)
        # Add the array to the list
        harmonic_gain_arrays.append(harmonic_gain_array)
    return np.array(harmonic_gain_arrays)

def freq_to_harmonics_and_gains(frequency:float, H:int, N:int=MAX_HARMONICS, gain:float=1.0, sort:str="frequency") -> tuple[np.ndarray, np.ndarray]:
    """Convert a frequency to an array of nearest harmonics and an array of harmonic gain arrays.

    Args:
        frequency (float): Frequency to convert.
        H (int): Number of harmonics to find.
        N (int, optional): Length of the harmonic gain arrays. Defaults to MAX_HARMONICS.
        gain (float, optional): Gain of the harmonics. Defaults to 1.0.
        sort (str, optional): Sort the results by "note", "harmonic", or "frequency". Defaults to "frequency".

    Returns:
        tuple[np.ndarray, np.ndarray]: Array of nearest harmonics and array of harmonic gain arrays.
    """
    # Find the nearest harmonics
    nearest_harmonics = find_nearest_harmonics(frequency, H, sort)
    # Get the harmonic gain arrays
    harmonic_gain_arrays = get_harmonic_gain_arrays(nearest_harmonics, gain, N)
    return (nearest_harmonics, harmonic_gain_arrays)

# Harmonic series for various instruments (untested)
instrument_harmonics = {
    'violin':[1, 0.8, 0.6, 0.5, 0.4, 0.35, 0.3, 0.25, 0.2, 0.18, 0.16, 0.14, 0.12, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
    'flute': [1, 0.1, 0.05, 0.025, 0.0125, 0.00625, 0.003125, 0.0015625, 0.00078125, 0.000390625, 0.0001953125, 0.00009765625, 0.000048828125, 0.0000244140625, 0.00001220703125, 0.000006103515625, 0.0000030517578125, 0.00000152587890625, 0.000000762939453125, 0.0000003814697265625, 0.00000019073486328125, 0.000000095367431640625, 0.0000000476837158203125, 0.00000002384185791015625, 0.000000011920928955078125, 0.0000000059604644775390625, 0.00000000298023223876953125, 0.000000001490116119384765625, 0.0000000007450580596923828125, 0.00000000037252902984619140625, 0.000000000186264514923095703125, 0.0000000000931322574615478515625],
    'trumpet': [1, 0.75, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1, 0.08, 0.06, 0.05, 0.04, 0.03, 0.025, 0.02, 0.015, 0.01, 0.008, 0.006, 0.005, 0.004, 0.003, 0.0025, 0.002, 0.0015, 0.001, 0.0008, 0.0006, 0.0005, 0.0004, 0.0003],
    'piano': [1, 0.7, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1, 0.07, 0.05, 0.035, 0.025, 0.02, 0.015, 0.01, 0.007, 0.005, 0.0035, 0.0025, 0.002, 0.0015, 0.001, 0.0007, 0.0005, 0.00035, 0.00025, 0.0002, 0.00015, 0.0001, 0.00007, 0.00005, 0.000035],
    'oboe': [1, 0.6, 0.36, 0.22, 0.13, 0.08, 0.05, 0.03, 0.02, 0.01, 0.006, 0.0036, 0.0022, 0.0013, 0.0008, 0.0005, 0.0003, 0.0002, 0.0001, 0.00006, 0.000036, 0.000022, 0.000013, 0.000008, 0.000005, 0.000003, 0.000002, 0.000001, 0.0000006, 0.00000036, 0.00000022, 0.00000013],
    'female': [1, 0.8, 0.64, 0.51, 0.41, 0.33, 0.26, 0.21, 0.17, 0.13, 0.1, 0.08, 0.06, 0.05, 0.04, 0.03, 0.02, 0.016, 0.013, 0.01, 0.008, 0.0064, 0.0051, 0.0041, 0.0033, 0.0026, 0.0021, 0.0017, 0.0013, 0.001, 0.0008, 0.00064],
    'male': [1, 0.75, 0.56, 0.42, 0.32, 0.24, 0.18, 0.14, 0.1, 0.075, 0.056, 0.042, 0.032, 0.024, 0.018, 0.014, 0.01, 0.0075, 0.0056, 0.0042, 0.0032, 0.0024, 0.0018, 0.0014, 0.001, 0.00075, 0.00056, 0.00042, 0.00032, 0.00024, 0.00018, 0.00014],
    'nightingale': [1, 0.5, 0.25, 0.13, 0.06, 0.03, 0.015, 0.0075, 0.00375, 0.001875, 0.0009375, 0.00046875, 0.000234375, 0.0001171875, 0.00005859375, 0.000029296875, 0.0000146484375, 0.00000732421875, 0.000003662109375, 0.0000018310546875, 0.00000091552734375, 0.000000457763671875, 0.0000002288818359375, 0.00000011444091796875, 0.000000057220458984375, 0.0000000286102294921875, 0.00000001430511474609375, 0.000000007152557373046875, 0.0000000035762786865234375, 0.00000000178813934326171875, 0.000000000894069671630859375, 0.0000000004470348358154296875]
}

def harmonic_frequencies(base_frequency, n):
    """
    Given a base frequency and a number of harmonics, returns the frequencies of the harmonics.

    Arguments:
    base_frequency -- the base frequency from which to calculate harmonics
    n -- the number of harmonics to calculate
    """
    # Calculate the frequencies by multiplying the base frequency by each integer up to n
    frequencies = [base_frequency * i for i in range(1, n+1)]
    
    return frequencies

def create_frequency_map(base_frequency, harmonic_generator, n, **kwargs):
    """
    Given a base frequency, a harmonic series generator function, and a number of harmonics,
    returns a map of frequencies to amplitudes.

    Arguments:
    base_frequency -- the base frequency from which to calculate harmonics
    harmonic_generator -- function that generates the amplitudes of a harmonic series
    n -- the number of harmonics to calculate
    kwargs -- additional keyword arguments to pass to the harmonic_generator function
    """
    # Calculate the frequencies using the harmonic_frequencies function
    frequencies = harmonic_frequencies(base_frequency, n)

    # Generate the amplitudes using the harmonic generator function
    amplitudes = harmonic_generator(n, **kwargs)

    # Create a map of frequencies to amplitudes
    frequency_map = dict(zip(frequencies, amplitudes))

    return frequency_map

def midi_to_freq(midi_number):
    """
    Converts a MIDI note number into a frequency in Hz.
    
    Arguments: 
    midi_number -- MIDI note number
    """
    return 440.0 * 2.0**((midi_number - 69) / 12.0)

def freq_to_midi(frequency):
    """
    Converts a frequency in Hz to a MIDI note number.
    
    Arguments: 
    frequency -- frequency in Hz
    """
    return int(round(69 + 12 * np.log2(frequency / 440.0)))

def harmonic_map_for_frequencies(freq_list):
    """
    Computes a harmonic map for a list of base frequencies.

    Arguments:
    freq_list -- List of frequencies to calculate the harmonics for.
    """
    
    freq_harmonic_map = {}

    for base_freq in freq_list:
        freq_harmonic_map[base_freq] = harmonic_frequencies(base_freq, 32)
    
    return freq_harmonic_map

def harmonic_map_for_midi_notes(midi_list):
    """
    Computes a harmonic map for a list of MIDI notes.

    Arguments:
    midi_list -- List of MIDI notes to calculate the harmonics for.
    """
    
    freq_harmonic_map = {}

    for midi_num in midi_list:
        base_freq = midi_to_freq(midi_num)
        freq_harmonic_map[midi_num] = harmonic_frequencies(base_freq, 32)
    
    return freq_harmonic_map

def basic_harmonic_series(n):
    """
    Generate the simple harmonic series.
  
    Arguments:
    n -- length of the harmonic series
    """  
    return np.array([1 / (i + 1) for i in range(n)])

def alternating_sign_harmonic_series(n):
    """
    Generate the alternating sign harmonic series.

    Arguments:
    n -- length of the harmonic series
    """  
    return np.array([((-1)**i) / (i + 1) for i in range(n)])

def odd_harmonic_series(n):
    """
    Generate the harmonic series that only includes odd denominators.

    Arguments:
    n -- length of the harmonic series
    """  
    return np.array([1 / (2*i + 1) for i in range(n)])

def even_harmonic_series(n):
    """
    Generate the harmonic series that only includes even denominators.

    Arguments:
    n -- length of the harmonic series
    """  
    return np.array([1 / (2*(i + 1)) for i in range(n)])

def shifted_harmonic_series(n, shift=2):
    """
    Generate the shifted harmonic series where each successive term is divided by i plus a shift.

    Arguments:
    n -- length of the harmonic series
    shift -- the value to shift the denominators by (default 2)
    """  
    return np.array([1 / (i + shift) for i in range(n)])

def reverse_basic_harmonic_series(n):
    """
    Generate the harmonic series where denominators are descended from n to 1.
  
    Arguments:
    n -- limiting value for the denominators and length of the harmonic series
    """  
    return np.array([1 / (n - i) for i in range(n)])

def reverse_odd_harmonic_series(n):
    """
    Generate the harmonic series where odd denominators are descended from 2n-1 to 1.
  
    Arguments:
    n -- half limit for the denominators and length of the harmonic series
    """  
    return np.array([1 / (2 * (n - i) + 1) for i in range(n)]) 

def prime_harmonic_series(n, primes=np.array([2, 3, 5, 7, 11, 13])):
    """
    Generate the harmonic series where denominators are prime numbers repeated to achieve length n.
  
    Arguments:
    n -- length of the harmonic series
    primes -- array of prime numbers (default [2, 3, 5, 7, 11, 13])  
    """  
    return np.array([1 / i for i in primes for _ in range(int(n/len(primes)))])

def squared_harmonic_series(n):
    """
    Generate the harmonic series where denominators are squares of integers from 0 to n-1.

    Arguments:
    n -- limiting value for the series
    """  
    return np.array([1 / (i**2 + 1) for i in range(n)])

def cubic_harmonic_series(n):
    """
    Generate the harmonic series where denominators are cubes of integers from 0 to n-1.

    Arguments:
    n -- limiting value for the series
    """  
    return np.array([1 / (i**3 + 1) for i in range(n)])

def const_base_harmonic_series(n, base=5):
    """
    Generate the harmonic series with a constant base, where each denominator is base*i + 1.

    Arguments:
    n -- length of the harmonic series
    base -- base for the harmonic series (default 5)
    """  
    return np.array([1 / (base*i + 1) for i in range(n)])

def fibonacci_harmonic_series(n):
    """
    Generate the harmonic series where denominators are fibonacci numbers.

    Arguments:
    n -- limiting term for the fibonacci series and length of the harmonic series 
    """  
    fibonacci_numbers = np.array([0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987][:n])
    return 1 / fibonacci_numbers[2:]

def triangular_number_harmonic_series(n):
    """
    Generate the harmonic series where each denominator is a triangular number.

    Arguments:
    n -- limiting value for the triangular number sequence and length of the harmonic series
    """  
    return np.array([1 / ((i * (i + 1)) / 2) for i in range(1, n+1)])

def factorial_harmonic_series(n):
    """
    Generate the harmonic series where each denominator is factorial of index.

    Arguments:
    n -- limiting value for factorial calculation and length of the series
    """  
    return np.array([1 / np.math.factorial(i) for i in range(n)])

def geometric_progression_harmonic_series(n, base=2):
    """
    Generate the harmonic series where each denominator is geometric progression.

    Arguments:
    n -- limiting value for geometric progression and length of the series
    base -- base of the geometric progression (default 2)
    """
    return np.array([1 / (base ** i) for i in range(n)])

def power_series(n, power=3):
    """
    Generate the power series where each denominator is raised to a given power.
  
    Arguments:
    n -- length of the series
    power -- power to which each denominator is raised (default 3)
    """  
    return np.array([1 / (i**power + 1) for i in range(n)])

def logarithmic_harmonic_series(n, base=2):
    """
    Generate the harmonic series where each denominator is a logarithm of index.

    Arguments:
    n -- length of the series
    base -- base of the logarithm (default 2)
    """  
    return np.array([1 / np.log(i + base) for i in range(n)])

def double_harmonic_series(n):
    """
    Generate the double harmonic series which includes fractional terms for both i and i+1 index.

    Arguments:
    n -- length of the harmonic series
    """
    return np.array([1/(2*i+1) + 1/(2*(i+1)) for i in range(n)])

def harmonic_series_with_sin(n):
    """
    Generate the harmonic series where each denominator is the sine of index.

    Arguments:
    n -- length of the harmonic series
    """
    return np.array([1 / np.sin(i + np.pi/2 + 1e-6) for i in range(n)])

def harmonic_series_with_cos(n):
    """
    Generate the harmonic series where each denominator is the cosine of index.

    Arguments:
    n -- length of the harmonic series
    """
    return np.array([1 / np.cos(i + np.pi/2 + 1e-6) for i in range(n)])

def harmonic_series_with_tan(n):
    """
    Generate the harmonic series where each denominator is the tangent of index.

    Arguments:
    n -- length of the harmonic series
    """
    return np.array([1 / np.tan(i + np.pi/4 + 1e-6) for i in range(n)])

def exponent_harmonic_series(n, base=0.5):
    """
    Generate the harmonic series where each denominator is raised to an exponential function of index.

    Arguments:
    n -- length of the harmonic series
    base -- base of the exponent (default 0.5)
    """
    return np.array([1 / np.power(base, i) for i in range(n)])

def prime_power_series(n, primes=np.array([2, 3, 5, 7, 11, 13])):
    """
    Generate the harmonic series where denominators are prime numbers raised to the power their index.
  
    Arguments:
    n -- length of the harmonic series
    primes -- array of prime numbers (default [2, 3, 5, 7, 11, 13])  
    """  
    return np.array([1 / np.power(primes[i%len(primes)], i+1) for i in range(n)]) 

def fibonacci_square_series(n):
    """
    Generate the harmonic series where denominators are squares of fibonacci numbers.

    Arguments:
    n -- limiting term for the fibonacci series and length of the harmonic series 
    """  
    fibonacci_numbers = np.array([0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987][:n])
    return 1 / np.power(fibonacci_numbers[2:], 2)

def reciprocals_of_triangular_numbers(n):
    """
    Generate the harmonic series where each denominator is a reciprocal of triangular number.

    Arguments:
    n -- limiting value for the triangular number sequence and length of the harmonic series
    """  
    return np.array([1 / ((i * (i + 1)) / (2*n)) for i in range(1, n+1)])

def create_subplot(func, n):
    """
    Given a harmonic generating function and length, returns a subplot titled by function name.

    Arguments:
    func -- function that generates a harmonic series
    n -- length of the harmonic series
    """
    # Generate harmonic series
    harmonic_series = func(n)
    
    # Arrange function name into title
    title = ' '.join(func.__name__.split('_')).title() + ' (' + str(n) + ')'

    # Create a new plot with a axis labels and no grid/axis
    p = figure(width=300, height=300, title=title, x_axis_label='Harmonics', y_axis_label='Value', toolbar_location=None)
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    
    # Add a bar renderer
    p.vbar(x=list(range(n)), top=harmonic_series, width=0.5)

    return p

def plot_grid(functions, n):
    """
    Given a list of harmonic series functions, plot them in a grid layout

    Arguments: 
    functions -- list of functions that generate harmonic series
    n -- length of each harmonic series
    """
    # Generate a list of subplots
    plots = [create_subplot(func, n) for func in functions]

    # Arrange the subplots in a grid layout of appropriate shape
    grid = gridplot(plots, ncols=3)

    # Output to notebook
    output_notebook()

    # Show the results
    show(grid)


