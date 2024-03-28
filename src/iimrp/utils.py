"""Utilities for working with MRP recording files and dataframes.
"""

import os
import pickle
import pandas as pd
from datetime import datetime
from mido import MidiFile, MidiTrack, Message
from tqdm.auto import tqdm

dt = lambda: f"{datetime.now().strftime('%Y_%m_%d-%H%M%S')}"

def mrp_to_df(file: str):
    return pd.read_csv(file,
        names=('time', 'osc', 'types', 'v0', 'v1', 'v2'), 
        converters={'time':float, 'osc':str, 'types':str, 'v0':float, 'v1':float, 'v2':float},
        sep='\s+')

def df_to_mrp(df: pd.DataFrame, file: str):
    print(f"Writing to {file}")
    df['time'] = df['time'].round(5)
    rows_str = df.astype(str).agg(' '.join, axis=1)
    with open(file, 'w') as f:
        for row in rows_str:
            f.write(f"{row}\n")
    rows_list = rows_str.tolist()
    return rows_list

def gen_events_to_df(gen_events: dict, columns: list):
    note_on = lambda t, p, i: pd.Series([round(t,5), '/mrp/midi', 'iii', 159, p, 127], index=i)
    note_off = lambda t, p, i: pd.Series([round(t,5), '/mrp/midi', 'iii', 143, p, 0], index=i)
    quality = lambda t, n, p, q, v: pd.Series([round(t,5), f'/mrp/quality/{n}', 'iif', 15, p, round(v, 5)], index=q)
    rows = []
    for t, event in tqdm(gen_events.items(), total=len(gen_events)):
        if event['vel'] > 0:
            rows.append(note_on(t, event['pitch'], columns))
        else:
            rows.append(note_off(t, event['pitch'], columns))
    return pd.DataFrame(rows, columns=columns)

def gen_events_to_midi(events: dict, file: str):
    file = f'{file}_{dt()}.mid'
    print(f"Writing to {file}")
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    ticks_per_second = mid.ticks_per_beat / (500000 / 1000000)
    for k in tqdm(sorted(events)):
        event = events[k]
        delta_ticks = int(event['time'] * ticks_per_second)
        if event['vel'] < 0.5: track.append(Message(
                 'note_off', note=event['pitch'], velocity=100, time=delta_ticks))
        else: track.append(Message(
                 'note_on', note=event['pitch'], velocity=int(event['vel']+0.5), time=delta_ticks))
    mid.save(file)
    return mid

def gen_events_to_mrp(events: dict, dfcols: list, file: str, pkl: bool=False, midi: bool=False) -> tuple[pd.DataFrame, list]:
    """Convert a dictionary of generated events to a DataFrame and MRP file.

    Args:
        events (dict): Dictionary of generated events.
        dfcols (list): List of column names for the DataFrame.
        file (str): File name for the MRP file.
        pkl (bool, optional): Save the DataFrame to a pickle file. Defaults to False.
        midi (bool, optional): Save the events to a MIDI file. Defaults to False.

    Returns:
        tuple[pd.DataFrame, list]: DataFrame and list of rows for the MRP file.
    """
    file = f'{file}_{dt()}'
    df = gen_events_to_df(events, dfcols)
    rows = df_to_mrp(df, f"{file}.log")
    if pkl: save_pkl(df, f"{file}.pkl")
    if midi: gen_events_to_midi(events, file)
    return df, rows

def ext_files_in_dir(directory, ext=".txt"):
    files = os.listdir(directory)
    files = [f for f in files if f.endswith(ext)]
    return files

def save_pkl(data, file):
    with open(file, 'wb') as f:
        pickle.dump(data, f)

def load_pkl(file):
    with open(file, 'rb') as f:
        return pickle.load(f)
    
def concat_mrp_dfs(filepaths: list[str], save: bool=False, out_file: str=None) -> pd.DataFrame:
    dfs = []
    total_last_time = 0
    for i, file in enumerate(tqdm(filepaths, desc="Loading and adjusting MRP DFs")):
        print(f"Loading {file}")
        df = mrp_to_df(file)
        if i > 0:
            df['time'] += total_last_time
        total_last_time = df['time'].iloc[-1]
        dfs.append(df)
    print(f"Concatenating {len(dfs)} DataFrames")
    df = pd.concat(dfs, ignore_index=True)
    mins, secs = divmod(total_last_time, 60)
    duration = f"{int(mins)}m{int(secs)}s"
    print(f"Total duration: {duration}")
    if save:
        if not out_file:
            path = os.path.dirname(filepaths[0])
            out_file = f"{path}/concat_{duration}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        print(f"Saving to {out_file}")
        df_to_mrp(df, out_file)
    return df

def concat_dfs(dfs: list[pd.DataFrame], save: bool=False, out_file: str=None) -> pd.DataFrame:
    dfs = [df.copy() for df in dfs]
    total_last_time = 0
    for i, df in enumerate(tqdm(dfs, total=len(dfs), desc="Loading and adjusting MRP DFs")):
        if i > 0:
            df['time'] += total_last_time
        total_last_time = df['time'].iloc[-1]
        print(f"{i} total_last_time: {total_last_time}")
    print(f"Concatenating {len(dfs)} DataFrames")
    df = pd.concat(dfs, ignore_index=True)
    mins, secs = divmod(total_last_time, 60)
    # duration = f"{int(mins)}m{int(secs)}s"
    print(f"Total duration: {mins} {secs}")
    if save:
        if not out_file:
            out_file = f"concat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        print(f"Saving to {out_file}")
        df_to_mrp(df, out_file)
    return df

def reduce_gap(df, max_gap=20, min_gap=10):
    df = df.copy()
    df.reset_index(drop=True, inplace=True)
    g = max_gap
    for i in range(len(df) - 1):
        current_time = df.loc[i, 'time']
        next_time = df.loc[i + 1, 'time']
        if next_time - current_time > g:
            gap_size = next_time - current_time 
            df.loc[i + 1:, 'time'] -= gap_size - min_gap
    return df

