class Point_Class():
    # store pertinent data of the point
    def __init__(self, index, x, y, z, red, green, blue, intensity):
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        self.xyz = [x, y, z]
        self.r = red
        self.g = green
        self.b = blue
        self.intensity = intensity