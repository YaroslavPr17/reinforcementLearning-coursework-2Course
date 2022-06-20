import aggdraw
from Environment.city import City
from Environment.objects.road import Road
from Environment.objects.intersection import Intersection
import tkinter as tk
from tkinter import Canvas
from PIL import ImageTk
from PIL import Image
from threading import Thread
from time import sleep
from Environment.model.state import State


class ThreadUpdater(Thread):
    def __init__(self, map):
        super().__init__()
        self.map = map

    def run(self) -> None:
        iF = MapVizualization.iFinish
        jF = MapVizualization.jFinish
        while self.map.running:
            if (iF != MapVizualization.iFinish or jF != MapVizualization.jFinish):
                iF = MapVizualization.iFinish
                jF = MapVizualization.jFinish
                self.map.drawContent()
            self.map.drawAgent()
            if MapVizualization.hasAgent and (isinstance(MapVizualization.city.city_model[MapVizualization.iAgent][MapVizualization.jAgent], Road)):
                MapVizualization.agentPosition = MapVizualization.agentPosition + 1
            sleep(MapVizualization.delay)


class MapVizualization(tk.Tk):
    running = True

    hasFinish = False
    iFinish = 0
    jFinish = 0

    hasAgent = False
    iAgent = 0
    jAgent = 0
    agentDirection = "Z"
    agentLaneNumber = 16
    agentPosition = 0

    x0 = 0
    y0 = 0

    xMouse = 0
    yMouse = 0

    scale = 1

    moveMode = False

    horizontalWindow = 2560 // 3 * 2
    verticalWindow = 1440 // 3 * 2

    def __init__(self, env: City, delay: float):
        print("DELAY", delay)

        super().__init__()

        self.title("env_visualization")

        self.canvas = Canvas(self, width=self.horizontalWindow, height=self.verticalWindow, bg="#247719")
        self.canvas.pack(expand=1, fill=tk.BOTH)

        MapVizualization.city = env
        self.drawAgentCount = 25
        MapVizualization.delay = delay / self.drawAgentCount

        self.setBlockSize()
        self.drawContent()
        self.drawAgent()

        self.canvas.bind('<MouseWheel>', self.canvas_mouseWheel_event)
        self.canvas.bind('<Motion>', self.canvas_motion_event)
        self.canvas.bind('<ButtonPress-1>', self.canvas_buttonPress_event)
        self.canvas.bind('<ButtonRelease-1>', self.canvas_buttonRelease_event)
        self.canvas.bind("<Configure>", self.canvas_resize_event)

        self.thread = ThreadUpdater(self)
        self.thread.start()

    def clear(self):
        print("del map")
        self.running = False
        self.thread.join()

    def setBlockSize(self):
        self.vertical = self.verticalWindow / MapVizualization.city.shape[0]
        self.horizontal = self.horizontalWindow / MapVizualization.city.shape[1]
        if self.vertical < self.horizontal:
            self.horizontal = self.vertical
        else:
            self.vertical = self.horizontal
        self.wp = self.vertical / 10

    def idxToX(self, idx):
        return idx * self.horizontal

    def idxToY(self, idx):
        return idx * self.vertical

    def drawContent(self):
        def drawRectangle(xLeft, yTop, xRight, yBottom, fillColor, lineColor):
            draw.rectangle((xLeft, yTop, xRight, yBottom), aggdraw.Pen(lineColor, 0.5), aggdraw.Brush(fillColor))

        def drawGrass(x0, y0, x1, y1, x2, y2, x3, y3):
            draw.polygon((x0, y0, x1, y1, x2, y2, x3, y3), aggdraw.Pen("#247719", 0.5), aggdraw.Brush("#247719"))

        def drawVerticalDashLine(x, yTop, yBottom):
            i = 0
            while True:
                y1 = yTop + i * self.wp * self.scale
                y2 = yTop + (i + 1) * self.wp * self.scale
                if y2 > yBottom:
                    break
                if i % 2 == 0:
                    draw.line((x, y1, x, y2), aggdraw.Pen("white", 1 * self.scale))
                i = i + 1

        def drawHorizontalDashLine(xLeft, xRight, y):
            i = 0
            while True:
                x1 = xLeft + i * self.wp * self.scale
                x2 = xLeft + (i + 1) * self.wp * self.scale
                if x2 > xRight:
                    break
                if i % 2 == 0:
                    draw.line((x1, y, x2, y), aggdraw.Pen("white", 1 * self.scale))
                i = i + 1

        def isRoad(i, j):
            return ((i > 0) and (i <= MapVizualization.city.shape[0]) and (j > 0) and (j <= MapVizualization.city.shape[1]) and (isinstance(MapVizualization.city.city_model[i][j], Road)))

        def getLeftCount(i, j):
            return [len(value) for key, value in MapVizualization.city.city_model[i][j].lanes.items()][1]

        def getRightCount(i, j):
            return [len(value) for key, value in MapVizualization.city.city_model[i][j].lanes.items()][0]

        def draw_destonation_point(x, y):
            # print(x, y)
            yTop = y - (4 * self.wp) * self.scale
            yBottom = y - (1 * self.wp) * self.scale
            xRight = x + (3 * self.wp) * self.scale
            yRight = y - (2.5 * self.wp) * self.scale
            points = [x, yBottom,
                      x, yTop,
                      xRight, yRight]

            draw.polygon((points), aggdraw.Pen("red", 0.5), aggdraw.Brush("red"))
            draw.line((x, y, x, yTop), aggdraw.Pen("black", 3 * self.scale))

        def drawGround(horizontalIdx, verticalIdx):
            xLeft = self.x0 + self.idxToX(horizontalIdx) * self.scale
            xRight = self.x0 + self.idxToX(horizontalIdx + 1) * self.scale
            yTop = self.y0 + self.idxToY(verticalIdx) * self.scale
            yBottom = self.y0 + self.idxToY(verticalIdx + 1) * self.scale

            drawRectangle(xLeft, yTop, xRight, yBottom, "#247719", "#247719")

        def drawIntersection(horizontalIdx, verticalIdx):
            xLeft = self.x0 + self.idxToX(horizontalIdx) * self.scale
            xRight = self.x0 + self.idxToX(horizontalIdx + 1) * self.scale
            yTop = self.y0 + self.idxToY(verticalIdx) * self.scale
            yBottom = self.y0 + self.idxToY(verticalIdx + 1) * self.scale

            drawRectangle(xLeft, yTop, xRight, yBottom, "gray", "gray")



            if MapVizualization.hasFinish and MapVizualization.iFinish == verticalIdx and MapVizualization.jFinish == horizontalIdx:
                xCenter = xLeft + (xRight - xLeft) // 2
                yCenter = yTop + (yBottom - yTop) // 2
                draw_destonation_point(xCenter, yCenter)

           
        def drawVerticalRoad(horizontalIdx, verticalIdx):
            xLeft = self.x0 + self.idxToX(horizontalIdx) * self.scale
            xRight = self.x0 + self.idxToX(horizontalIdx + 1) * self.scale
            yTop = self.y0 + self.idxToY(verticalIdx) * self.scale
            yBottom = self.y0 + self.idxToY(verticalIdx + 1) * self.scale

            drawRectangle(xLeft, yTop, xRight, yBottom, "gray", "gray")

            xCenter = xLeft + (xRight - xLeft) // 2

            # рисуем центральную линию: двойная сполшная и т.д.
            # if (self.wp * self.scale > 5):
            #     draw.line((xCenter - 1.3 * self.scale, yTop, xCenter - 1.3 * self.scale, yBottom), aggdraw.Pen("white", 1 * self.scale))
            #     draw.line((xCenter + 1.3 * self.scale, yTop, xCenter + 1.3 * self.scale, yBottom), aggdraw.Pen("white", 1 * self.scale))

            # количество полос сверху
            leftTopCount = getLeftCount(verticalIdx, horizontalIdx)
            rightTopCount = getRightCount(verticalIdx, horizontalIdx)
            leftBottomCount = getLeftCount(verticalIdx + 1, horizontalIdx) if isRoad(verticalIdx + 1,
                                                                                     horizontalIdx) else getLeftCount(
                verticalIdx, horizontalIdx)
            rightBottomCount = getRightCount(verticalIdx + 1, horizontalIdx) if isRoad(verticalIdx + 1,
                                                                                       horizontalIdx) else getRightCount(
                verticalIdx, horizontalIdx)

            # координаты для травы
            xLeftTopGrass = xLeft + self.wp * leftTopCount * self.scale
            xLeftBottomGrass = xLeft + self.wp * leftBottomCount * self.scale
            xRightTopGrass = xRight - self.wp * rightTopCount * self.scale
            xRightBottomGrass = xRight - self.wp * rightBottomCount * self.scale

            for i in range(1, 10):
                drawVerticalDashLine(xLeft + i * self.wp * self.scale, yTop, yBottom)

            drawGrass(xLeftTopGrass, yTop, xRightTopGrass, yTop, xRightBottomGrass, yBottom, xLeftBottomGrass, yBottom)
            draw.line((xLeftTopGrass, yTop, xLeftBottomGrass, yBottom), aggdraw.Pen("black", 1.5 * self.scale))
            draw.line((xRightTopGrass, yTop, xRightBottomGrass, yBottom), aggdraw.Pen("black", 1.5 * self.scale))

            if MapVizualization.hasFinish and MapVizualization.iFinish == verticalIdx and MapVizualization.jFinish == horizontalIdx:
                xCenter = xLeft + (xRight - xLeft) // 2
                yCenter = yTop + (yBottom - yTop) // 2
                draw_destonation_point(xCenter, yCenter)

        def drawHorizontalRoad(horizontalIdx, verticalIdx):
            xLeft = self.x0 + self.idxToX(horizontalIdx) * self.scale
            xRight = self.x0 + self.idxToX(horizontalIdx + 1) * self.scale
            yTop = self.y0 + self.idxToY(verticalIdx) * self.scale
            yBottom = self.y0 + self.idxToY(verticalIdx + 1) * self.scale

            drawRectangle(xLeft, yTop, xRight, yBottom, "gray", "gray")

            yCenter = yTop + (yBottom - yTop) // 2

            # рисуем центральную линию: двойная сполшная и т.д.
            # if (self.wp * self.scale > 5):
            #     draw.line((xLeft, yCenter - 1.3 * self.scale, xRight, yCenter - 1.3 * self.scale), aggdraw.Pen("white", 1 * self.scale))
            #     draw.line((xLeft, yCenter + 1.3 * self.scale, xRight, yCenter + 1.3 * self.scale), aggdraw.Pen("white", 1 * self.scale))

            # количество полос сверху
            leftTopCount = getRightCount(verticalIdx, horizontalIdx)
            leftBottomCount = getLeftCount(verticalIdx, horizontalIdx)

            rightTopCount = getRightCount(verticalIdx, horizontalIdx + 1) if isRoad(verticalIdx, horizontalIdx + 1) else getRightCount(verticalIdx, horizontalIdx)
            rightBottomCount = getLeftCount(verticalIdx, horizontalIdx + 1) if isRoad(verticalIdx, horizontalIdx + 1) else getLeftCount(verticalIdx, horizontalIdx)




            # координаты для травы
            yLeftTopGrass = yTop + self.wp * leftTopCount * self.scale
            yRightTopGrass = yTop + self.wp * rightTopCount * self.scale
            yLeftBottomGrass = yBottom - self.wp * leftBottomCount * self.scale
            yRightBottomGrass = yBottom - self.wp * rightBottomCount * self.scale

            for i in range(1, 10):
                drawHorizontalDashLine(xLeft, xRight, yTop + i * self.wp * self.scale)

            drawGrass(xLeft, yLeftTopGrass, xRight, yRightTopGrass, xRight, yRightBottomGrass, xLeft, yLeftBottomGrass)
            draw.line((xLeft, yLeftTopGrass, xRight, yRightTopGrass), aggdraw.Pen("black", 1.5 * self.scale))
            draw.line((xRight, yRightBottomGrass, xLeft, yLeftBottomGrass), aggdraw.Pen("black", 1.5 * self.scale))

            if MapVizualization.hasFinish and MapVizualization.iFinish == verticalIdx and MapVizualization.jFinish == horizontalIdx:
                xCenter = xLeft + (xRight - xLeft) // 2
                yCenter = yTop + (yBottom - yTop) // 2
                draw_destonation_point(xCenter, yCenter)

        image = Image.new("RGBA", (self.horizontalWindow, self.verticalWindow), (36, 119, 25, 1))
        draw = aggdraw.Draw(image)

        for i in range(MapVizualization.city.shape[0]):
            for j in range(MapVizualization.city.shape[1]):
                if (isinstance(MapVizualization.city.city_model[i][j], Road)):
                    if (MapVizualization.city.city_model[i][j].orientation == "v"):
                        drawVerticalRoad(j, i)
                    else:
                        drawHorizontalRoad(j, i)

                elif (isinstance(MapVizualization.city.city_model[i][j], Intersection)):
                    drawIntersection(j, i)
                else:
                    drawGround(j, i)

        draw.flush()
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image((0, 0), anchor='nw', image=self.tk_image)

    def drawAgent(self):

        def getCenter():
            xLeft = self.x0 + self.idxToX(MapVizualization.jAgent) * self.scale
            xRight = self.x0 + self.idxToX(MapVizualization.jAgent + 1) * self.scale
            yTop = self.y0 + self.idxToY(MapVizualization.iAgent) * self.scale
            yBottom = self.y0 + self.idxToY(MapVizualization.iAgent + 1) * self.scale

            xCenter = xLeft + (xRight - xLeft) // 2
            yCenter = yTop + (yBottom - yTop) // 2

            return xCenter, yCenter

        def getAgentCanvas(x, y):
            if MapVizualization.agentDirection == "N":
                xLeft = x + (self.horizontal * 0.5 - (self.agentLaneNumber + 1) * self.wp) * self.scale
                yTop = y - (self.vertical // self.drawAgentCount * MapVizualization.agentPosition + self.wp) * self.scale
                return xLeft, yTop, round(self.wp * self.scale), round(self.wp * 2 * self.scale)

            if MapVizualization.agentDirection == "S":
                xLeft = x - (self.horizontal * 0.5 - self.agentLaneNumber * self.wp) * self.scale
                yTop = y + (self.vertical // self.drawAgentCount * MapVizualization.agentPosition - self.wp) * self.scale
                return xLeft, yTop, round(self.wp * self.scale), round(self.wp * 2 * self.scale)

            if MapVizualization.agentDirection == "W":
                yTop = y - (self.vertical * 0.5 - self.agentLaneNumber * self.wp) * self.scale
                xLeft = x - (self.horizontal // self.drawAgentCount * MapVizualization.agentPosition + self.wp) * self.scale
                return xLeft, yTop, round(self.wp * 2 * self.scale), round(self.wp * self.scale)

            if MapVizualization.agentDirection == "E":
                yTop = y + (self.vertical * 0.5 - (self.agentLaneNumber + 1) * self.wp) * self.scale
                xLeft = x + (self.horizontal // self.drawAgentCount * MapVizualization.agentPosition - self.wp) * self.scale
                return xLeft, yTop, round(self.wp * 2 * self.scale), round(self.wp * self.scale)

        def draw_vehicle(width, height):
            if MapVizualization.agentDirection == "N":
                xMiddle = width / 2
                yMiddle = xMiddle

                points = [0, height,
                          0, yMiddle,
                          xMiddle, 0,
                          width, yMiddle,
                          width, height]
                drawAgent.polygon((points), aggdraw.Pen("black", 0.5), aggdraw.Brush("red"))

            if MapVizualization.agentDirection == "S":
                xMiddle = width / 2
                yMiddle = height - xMiddle

                points = [width, 0,
                          width, yMiddle,
                          xMiddle, height,
                          0, yMiddle,
                          0, 0]
                drawAgent.polygon((points), aggdraw.Pen("black", 0.5), aggdraw.Brush("red"))

            if MapVizualization.agentDirection == "W":
                yMiddle = height / 2
                xMiddle = yMiddle

                points = [width, height,
                          xMiddle, height,
                          0, yMiddle,
                          xMiddle, 0,
                          width, 0]
                drawAgent.polygon((points), aggdraw.Pen("black", 0.5), aggdraw.Brush("red"))

            if MapVizualization.agentDirection == "E":
                yMiddle = height / 2
                xMiddle = width - yMiddle

                points = [0, 0,
                          xMiddle, 0,
                          width, yMiddle,
                          xMiddle, height,
                          0, height]
                drawAgent.polygon((points), aggdraw.Pen("black", 0.5), aggdraw.Brush("red"))

        if MapVizualization.hasAgent:
            xCenter, yCenter = getCenter()
            xLeft, yTop, canvasWidth, canvasHeight = getAgentCanvas(xCenter, yCenter)

            imageAgent = Image.new("RGBA", (canvasWidth, canvasHeight), (0, 0, 0, 0))
            drawAgent = aggdraw.Draw(imageAgent)
            draw_vehicle(canvasWidth, canvasHeight)

            drawAgent.flush()
            self.tk_imageAgent = ImageTk.PhotoImage(imageAgent)
            self.canvas.create_image((xLeft, yTop), anchor='nw', image=self.tk_imageAgent)

    def updateContent(self, x, y):
        newX0 = self.x0 + x - self.xMouse
        if(newX0 > 0):
            newX0 = 0
        if(self.horizontalWindow * self.scale - abs(newX0) < self.horizontalWindow):
            newX0 = self.horizontalWindow - self.horizontalWindow * self.scale

        newY0 = self.y0 + y - self.yMouse
        if(newY0 > 0):
            newY0 = 0
        if(self.verticalWindow * self.scale - abs(newY0) < self.verticalWindow):
            newY0 = self.verticalWindow - self.verticalWindow * self.scale

        self.x0 = newX0
        self.y0 = newY0
        self.drawContent()
        self.drawAgent()

    def canvas_mouseWheel_event(self, event):
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            if self.scale > 1:
                self.scale -= 0.1
                self.drawContent()
                self.drawAgent()
        if event.num == 4 or event.delta == 120:
            self.scale += 0.1
            self.drawContent()
            self.drawAgent()

    def canvas_motion_event(self, event):
        if self.moveMode:
            self.updateContent(event.x, event.y)
        self.xMouse = event.x
        self.yMouse = event.y

    def canvas_buttonPress_event(self, event):
        self.something_clicked = 0  
        if self.scale > 1:
            self.moveMode = True
        self.xMouse = event.x
        self.yMouse = event.y

    def canvas_buttonRelease_event(self, event):
        self.something_clicked = 0
        self.moveMode = False
        self.updateContent(event.x, event.y)

    def canvas_resize_event(self, event):
        self.horizontalWindow, self.verticalWindow = event.width, event.height
        self.setBlockSize()
        self.drawContent()
        self.drawAgent()

    @staticmethod
    def callback_agent_draw(state: State):
        MapVizualization.iFinish = state.destination_coordinates.axis0
        MapVizualization.jFinish = state.destination_coordinates.axis1
        MapVizualization.hasFinish = True
        MapVizualization.iAgent = state.car_coordinates.axis0
        MapVizualization.jAgent = state.car_coordinates.axis1
        MapVizualization.agentDirection = state.current_direction
        MapVizualization.agentLaneNumber = state.current_lane
        MapVizualization.agentPosition = 0
        MapVizualization.hasAgent = True

