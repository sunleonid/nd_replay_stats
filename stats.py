import os, sys

###################
#
# Pass in a character name and dlc/pre-dlc, in any order.
#
# Example usages:
# python stats.py pre-dlc
# python stats.py coda
# python stats.py dlc nocturna
# python stats.py bolt amplified
# python stats.py classic dorian
# python stats.py monk pre-dlc
#
###################

# Path to the replays folder
REPLAY_PATH = 'C:/Program Files (x86)/Steam/steamapps/common/Crypt of the NecroDancer/replays'

# Characters in the order of their IDs
CHARS = ['cadence', 'melody', 'aria', 'dorian', 'eli', 'monk', 'dove', 'coda', 'bolt', 'bard', 'nocturna', 'diamond', 'mary', 'tempo']

# Whether or not to retrieve DLC stats. True by default
DLC = True

# Character name. Coda by default
CHAR = 'coda'

# Parse commandline args
for arg in sys.argv:
  arg = arg.lower()
  if arg in ['dlc', 'amplified']: DLC = True
  if arg in ['pre-dlc', 'classic']: DLC = False
  if arg in CHARS: CHAR = arg

# Store first floor replay data to remove duplicates
firstfloors = set()

# Number of floors per zone
floors = CHAR == 'dove' and 3 or 4

# Number of special floors (e.g. ND, Conductor)
specials = CHAR == 'cadence' and 2 or CHAR == 'nocturna' and 1 or 0

# Number of zones
zones = DLC and 5 or 4

# Name of zones
zonenames = list(range(1, zones + 1))
if CHAR == 'cadence': zonenames.append('N')
if CHAR == 'nocturna': zonenames.append('C')

# Death counts from 1-1 to 4-4/5-4 (or 4-6/5-5/5-6 for cadence/nocturna)
deaths = [0] * (floors * zones + specials)

for filename in os.listdir(REPLAY_PATH):
  namesplits = filename.split('_')
  version = int(namesplits[0])
  if DLC:
    isallzones = version > 75 and namesplits[9] == '-7'
  else:
    isallzones = version <= 75 and namesplits[9][0] == '6'

  if isallzones:
    file = open(REPLAY_PATH + '/' + filename, 'r')
    linesoffset = version > 84 and 6 or 9 # offset is different for full release DLC
    lines = file.read().split('\\n')[linesoffset:]
    file.close()

    if int(lines[6].split('|')[0]) == CHARS.index(CHAR) and int(lines[2]) == 1: # If solo mode with the chosen character
      firstfloor = lines[1] + lines[6] # Seed + Play data
      if firstfloor in firstfloors: continue # Filter out duplicate replays 
      firstfloors.add(firstfloor)

      if DLC:
        # I do not know whether it is possible to manually count number of songs played for DLC replays.
        numsongs = int(lines[0])

        # Skip obviously invalid numsongs, but this still does not filter out all bugged replays.
        if numsongs > len(deaths): continue
      else:
        # Manually count number of songs played. lines[0] isn't reliable due to the stacking replay bug
        seedindex = 1
        prevseed = int(lines[seedindex])
        numsongs = 1

        seedindex += 11
        while lines[seedindex]:
          seed = int(lines[seedindex])
          # Seed difference between floors:
          # 1 or 2 for regular floors
          # 16 or -8 for aria
          # seed is 0 for ND 1 second phase
          if seed - prevseed not in [1, 2, 16, -8, -prevseed]: break # Stacking replay bug
          prevseed = seed
          numsongs += 1
          seedindex += 11

      deaths[numsongs - 1] += 1

total = sum(deaths)

print('Stats for %s %s' % (DLC and 'Amplified' or 'Classic', CHAR.title()))
print('Total runs: %d' % total)
print('')

def percent(n, d):
  if d != 0:
    return '%.1f%%' % (100. * n / d)
  else:
    return 'N/A'

def printline(place, count, visits, prefix = ''):
  print(prefix + 'Deaths %s: %d\tVisited: %s\tSurvived: %s' % (place, count, percent(visits, total), percent(visits - count, visits)))

for i in range(len(deaths)):
  zone = zonenames[i // floors]
  floor = i % floors + 1
  asterisk = i == len(deaths) - 1 and '*' or ''
  printline('in %s-%d' % (zone, floor), deaths[i], sum(deaths[i:]), asterisk)

print('')

for i in range(zones):
  zone = i + 1
  offset = i * floors
  visits = sum(deaths[offset:])
  zonedeaths = sum(deaths[offset:][:floors])
  asterisk = zone * floors == len(deaths) and '*' or ''
  printline('in Zone %d' % zone, zonedeaths, visits, asterisk)

if CHAR == 'cadence':
  buttvisits = sum(deaths[-2:])
  buttsurvives = deaths[-1]
  printline('in ButtPuzzle', deaths[-2], sum(deaths[-2:]))
  printline('to NecroDancer', deaths[-1], deaths[-1], '*')

if CHAR == 'nocturna':
  printline('to Conductor', deaths[-1], deaths[-1], '*')

print('')
print('*Includes number of wins')