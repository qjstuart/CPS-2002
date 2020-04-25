from openeye import oedepict

width, height = 100, 100
image = oedepict.OEImage(width, height)

# @ <SNIPPET-CREATE-GROUP>
svg_group_circ = image.NewSVGGroup("circle")

image.PushGroup(svg_group_circ)
image.DrawCircle(oedepict.OEGetCenter(image), 30, oedepict.OERedBoxPen)
image.PopGroup(svg_group_circ)

oedepict.OEWriteImage("CreateSVGGroup.svg", image)
# @ </SNIPPET-CREATE-GROUP>

# @ <SNIPPET-GETSVGGROUPS>
for g in image.GetSVGGroups():
    print(g.GetId())


# @ </SNIPPET-GETSVGGROUPS>


class Map:
    size = 0

    # def __init__(self, size):`
    #     self.size = size

    def set_map_size(self, x, n):
        if x > 50 or n < 2 or n > 8:
            return False

        if n >= 4 and x < 5:
            return False

        if n >= 5 and x < 8:
            return False

        self.size = x
        print("Size: ", self.size)

    # def generate():


test_map = Map()
test_map.set_map_size(5, 3)
