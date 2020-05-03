from map import *
import HTML

HTMLFILE = 'HTML_map.html'
f = open(HTMLFILE, 'w')

test_map = Map()
test_map.set_map_size(8, 5)
test_map.generate_map()

t = HTML.table()

for i in range(test_map.size):
    for j in range(test_map.size):
        if test_map.tiles[i][j] is tile.GrassTile:
            colored_cell = HTML.TableCell(' ', bgcolor='olive')
            t.rows.append([test_map.tiles[i][j]])

htmlcode = str(t)
print(htmlcode)
f.write(htmlcode)
f.write('<p>')


