
# DEBUG
DEBUG = True

import re

# XML Reader
from xml.etree import ElementTree as ET

# Third Party
from svg.path import parse_path
from svg.path import Path

class TPSVGPathParser:

    """
        read SVG file
        get its canvas's size
        get its points at paths by iterating
    """

    PRECISION: float = 0.001

    # a list containing multiple tuples like 
    # # (classname, parsed path(svg.path.Path))
    _paths_list = list()

    # should call "get_points()" before getting this attr
    # it contains a list of paths which contains lists of points
    # it's a two-dimensional list
    _paths_points_list = list()

    # a dict like {"class": {"attrib":"value",},}
    _paths_style_dict = dict()

    def __init__(self, file_path: str) -> None:
        self.root = ET.parse(file_path).getroot()
        self.canvas = tuple(map(int, self.root.get("viewBox").split(" ")[2:4]))
        self.style_text = self.root.find("style").text

        for path in self.root.iter("path"):
            self._paths_list.append((path.get("class"), parse_path(path.get("d"))))

    def get_canvas(self) -> tuple:
        """
            @return(tuple) a tuple as (width, height) of the SVG viewBox
        """
        return self.canvas

    def get_points(self, precision: float=PRECISION) -> list:
        """
            get classnames and points from parsed paths
            @param precision(float=0.001): determine how to iterate path curves, should be less than 1
            @return(list): a two-dimensional list containing a list of paths which has a tuple
                containing the path's class and lists of points points are defined as (x, y)
        """
        precision = min(precision, self.PRECISION)
        calculating_times = int(1 / precision)

        for path in self._paths_list:

            #path is a tuple like (classname, parsed path)

            points_list = []

            # iterate path with precision
            for i in range(0, calculating_times + 1):
                point_in_complex = complex(path[1].point(float(i) * precision))
                points_list.append((point_in_complex.real, point_in_complex.imag))

            self._paths_points_list.append((path[0], points_list))

        return self._paths_points_list

    def get_style(self) -> dict:
        """
            this will parse style text written is CSS,
            WARNING: this function will ignore id !!!

            @return(list) a dict like {"class": {"attrib":"value",}}
        """

        CLASS_PATTERN = r"\.([a-zA-Z0-9]+)\{(.+)\}"
        CONTENT_PATTERN = r"([^:]+):([^;]+);"

        # got [("classname", "content"),]
        class_result = re.findall(CLASS_PATTERN, self.style_text)

        for c in class_result:
            class_name = c[0]

            # got [("attrib":"value"),]
            content_result = re.findall(CONTENT_PATTERN, c[1])
            content_dict = {content[0]:content[1] for content in content_result}

            self._paths_style_dict.update({class_name : content_dict})
        
        return self._paths_style_dict


import turtle

class TPTurtlePainter:

    def __init__(self, canvas: tuple, style: dict) -> None:
        """
            @param canvas(tuple): (width, height) of SVG viewBox
            @param style(dict): a dict like {"class": {"attrib":"value",}}
                SHOULD always get from TPSVGParser.get_style()
        """

        #configuring screen
        turtle.screensize(canvas[0], canvas[1])
        turtle.title("Tomortec")
        turtle.bgcolor("#315a78")

        self.turtle = turtle.Turtle()
        self.style  = style

        if DEBUG:
            #fastest
            self.turtle.speed("fastest")

    def paint_at(self, point: tuple):
        """
            @param point(tuple): (x, y)
        """
        self.turtle.goto(point)
        if not self.turtle.isdown():
            self.turtle.pendown()
        
    def paint_SVG(self, points: list):
        """
            @param points(list): a two-dimensional list containing a list of paths which has a tuple
                containing the path's class and lists of points points are defined as (x, y)

                SHOULD always get points with TPSVGPathParser.get_points()
        """
        self.turtle.penup() #should not draw right now
        for path in points:

            # path is a tuple like ("classname", parsed path)

            self.config_pen(self.style[path[0]])

            for point in path[1]:
                self.paint_at((point[0] - 512, -1*point[1] + 512))
            
            self.turtle.penup()

    def config_pen(self, config: dict):
        """
            @param config(dict): a dict like {"attrib": "value",}
                SHOULD always get config with TPSVGParser.get_style()
        """

        self.turtle.end_fill()

        if "fill" in config.keys():
            if config["fill"] != "none":

                self.turtle.pencolor(config["fill"])
                self.turtle.pensize(1)
                self.turtle.fillcolor(config["fill"])

                self.turtle.begin_fill()
        
        if "stroke" in config.keys():
            self.turtle.pencolor(config["stroke"])

            if "stroke-width" in config.keys():
                self.turtle.pensize(int(config["stroke-width"]))

if __name__=="__main__":

    svg_parser = TPSVGPathParser("TurtleSVGPainter/src/Icon-Tomortec.svg")
    svg_canvas = svg_parser.get_canvas()
    svg_points = svg_parser.get_points()
    svg_style  = svg_parser.get_style()

    TP = TPTurtlePainter(svg_canvas, svg_style)
    TP.paint_SVG(svg_points)