import sys

for file in sys.argv[1:]:
    lines = iter(open(file).read().splitlines())
    for line in lines:
        if line.startswith('#define SD_MESSAGE') and '_STR ' not in line:
            if line.endswith('\\'):
                line = line[:-1] + next(lines)
            print(' '.join(line.split()))
