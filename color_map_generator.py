import webcolors


with open('testmaps/colors.txt', 'w') as f:
    f.write(
        '''# All CSS3 colors are available through the webcolors package.
# This is the entire palette expressed as a fly-in map.
# Also includes the special 'rainbow' color.

nb_drones: 1

start_hub: start 0 0 [color=black]
hub: path_a1 1 0
end_hub: goal 2 0 [color=black]

'''
    )
    for i, x in enumerate(webcolors.names() + ['rainbow']):
        f.write(f'hub: {x} {i // 14} {i % 14 + 1} [color={x}]\n')

    f.write(
        """
connection: start-path_a1
connection: path_a1-goal
"""
    )
