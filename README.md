# MidiToTabs

This repo can translate .mid files into guitar tabs.

How to use: \
-python3 MidiToTabs.py <.mid file>\
-python3 MidiToTabs.py <.mid file> <channel#> \
-python3 MidiToTabs.py <.mid file> <channel#> <tuning_offset> <capo_offset>

Default Values for run:
python3 MidiToTabs.py <.mid file> -1 0 0

<channel#> = -1 means choose to longest channel \
<tuning_offset> = 0 means regular tuning for low E string\
<capo_offset> = 0 means no capo
