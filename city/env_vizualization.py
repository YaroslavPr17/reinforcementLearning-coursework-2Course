import aggdraw
from Environment.city import City
from Environment.objects.road import Road
from Environment.objects.intersection import Intersection
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
from PIL import Image, ImageColor
from PIL import ImageDraw

class MapVizualization(tk.Tk):
    x0 = 0
    y0 = 0

    xMouse = 0
    yMouse = 0

    scale = 1

    moveMode = False

    horizontalWindow = 2560 // 3 * 2
    verticalWindow = 1440 // 3 * 2

    vertical = verticalWindow // 15
    horizontal = horizontalWindow // 20

    def drawContent(self):
        def drawRectangle(xLeft, yTop, xRight, yBottom, fillColor, lineColor):
            draw.rectangle((xLeft, yTop, xRight, yBottom), aggdraw.Pen(fillColor, 0.5), aggdraw.Brush(fillColor)) #fill=fillColor, outline=lineColor)

        def drawGrass(x0, y0, x1, y1, x2, y2, x3, y3):
            draw.polygon((x0, y0, x1, y1, x2, y2, x3, y3), aggdraw.Pen("green", 0.5),aggdraw.Brush("green"))

        def idxToX(idx):
            return idx * self.horizontal

        def idxToY(idx):
            return idx * self.vertical

        def isRoad(i, j):
            return ((i > 0) and (i <= self.city.shape[0]) and (j > 0) and (j <= self.city.shape[1]) and (isinstance(self.city.city_model[i][j], Road)))

        def getLeftCount(i, j):
            return [len(value) for key, value in self.city.city_model[i][j].lanes.items()][1]

        def getRightCount(i, j):
            return [len(value) for key, value in self.city.city_model[i][j].lanes.items()][0]

        def drawGround(horizontalIdx, verticalIdx):
            xLeft = self.x0 + idxToX(horizontalIdx) * self.scale
            xRight = self.x0 + idxToX(horizontalIdx + 1) * self.scale
            yTop = self.y0 + idxToY(verticalIdx) * self.scale
            yBottom = self.y0 + idxToY(verticalIdx + 1) * self.scale

            drawRectangle(xLeft, yTop, xRight, yBottom, "green", "green")

        def drawIntersection(horizontalIdx, verticalIdx):
            xLeft = self.x0 + idxToX(horizontalIdx) * self.scale
            xRight = self.x0 + idxToX(horizontalIdx + 1) * self.scale
            yTop = self.y0 + idxToY(verticalIdx) * self.scale
            yBottom = self.y0 + idxToY(verticalIdx + 1) * self.scale

            drawRectangle(xLeft, yTop, xRight, yBottom, "green", "green")

            xCenter = xLeft + (xRight - xLeft) // 2
            yCenter = yTop + (yBottom - yTop) // 2

            xLeftTop = xCenter
            xRightTop = xCenter
            if (isRoad(verticalIdx - 1, horizontalIdx)):
                xLeftTop = xCenter - self.wp * getLeftCount(verticalIdx - 1, horizontalIdx) * self.scale
                xRightTop = xCenter + self.wp * getRightCount(verticalIdx - 1, horizontalIdx) * self.scale
            elif (isRoad(verticalIdx + 1, horizontalIdx)):
                xLeftTop = xCenter - self.wp * getLeftCount(verticalIdx + 1, horizontalIdx) * self.scale
                xRightTop = xCenter + self.wp * getRightCount(verticalIdx + 1, horizontalIdx) * self.scale

            xLeftBottom = xCenter
            xRightBottom = xCenter
            if (isRoad(verticalIdx + 1, horizontalIdx)):
                xLeftBottom = xCenter - self.wp * getLeftCount(verticalIdx + 1, horizontalIdx) * self.scale
                xRightBottom = xCenter + self.wp * getRightCount(verticalIdx + 1, horizontalIdx) * self.scale
            elif (isRoad(verticalIdx - 1, horizontalIdx)):
                xLeftBottom = xCenter - self.wp * getLeftCount(verticalIdx - 1, horizontalIdx) * self.scale
                xRightBottom = xCenter + self.wp * getRightCount(verticalIdx - 1, horizontalIdx) * self.scale

            yLeftTop = yCenter
            yLeftBottom = yCenter
            if (isRoad(verticalIdx, horizontalIdx - 1)):
                yLeftTop = yCenter - self.wp * getLeftCount(verticalIdx, horizontalIdx - 1) * self.scale
                yLeftBottom = yCenter + self.wp * getRightCount(verticalIdx, horizontalIdx - 1) * self.scale
            elif (isRoad(verticalIdx, horizontalIdx + 1)):
                yLeftTop = yCenter - self.wp * getLeftCount(verticalIdx, horizontalIdx + 1) * self.scale
                yLeftBottom = yCenter + self.wp * getRightCount(verticalIdx, horizontalIdx + 1) * self.scale

            yRightTop = yCenter
            yRightBottom = yCenter
            if (isRoad(verticalIdx, horizontalIdx + 1)):
                yRightTop = yCenter - self.wp * getLeftCount(verticalIdx, horizontalIdx + 1) * self.scale
                yRightBottom = yCenter + self.wp * getRightCount(verticalIdx, horizontalIdx + 1) * self.scale
            elif (isRoad(verticalIdx, horizontalIdx - 1)):
                yRightTop = yCenter - self.wp * getLeftCount(verticalIdx, horizontalIdx - 1) * self.scale
                yRightBottom = yCenter + self.wp * getRightCount(verticalIdx, horizontalIdx - 1) * self.scale

            if (not isRoad(verticalIdx - 1, horizontalIdx)):
                yTop = yRightTop

            if (not isRoad(verticalIdx + 1, horizontalIdx)):
                yBottom = yRightBottom

            if (not isRoad(verticalIdx, horizontalIdx - 1)):
                xLeft = xLeftBottom

            if (not isRoad(verticalIdx, horizontalIdx + 1)):
                xRight = xRightBottom

            points = [xLeft, yLeftTop,
                      xLeftTop, yLeftTop,
                      xLeftTop, yTop,
                      xRightTop, yTop,
                      xRightTop, yRightTop,
                      xRight, yRightTop,
                      xRight, yRightBottom,
                      xRightBottom, yRightBottom,
                      xRightBottom, yBottom,
                      xLeftBottom, yBottom,
                      xLeftBottom, yLeftBottom,
                      xLeft, yLeftBottom]

            draw.polygon((points), aggdraw.Pen("gray", 0.5),aggdraw.Brush("gray"))

        def drawVerticalRoad(horizontalIdx, verticalIdx):
            xLeft = self.x0 + idxToX(horizontalIdx) * self.scale
            xRight = self.x0 + idxToX(horizontalIdx + 1) * self.scale
            yTop = self.y0 + idxToY(verticalIdx) * self.scale
            yBottom = self.y0 + idxToY(verticalIdx + 1) * self.scale

            drawRectangle(xLeft, yTop, xRight, yBottom, "gray", "gray")

            xCenter = xLeft + (xRight - xLeft) // 2

            # рисуем центральную линию: двойная сполшная и т.д.
            # пунктирная линия - параметр dash=(15, 15)
            if (self.wp * self.scale > 5):
                draw.line((xCenter - 3, yTop, xCenter - 3, yBottom), aggdraw.Pen("white", 3))
                draw.line((xCenter + 3, yTop, xCenter + 3, yBottom), aggdraw.Pen("white", 3))

            # количество полос сверху
            leftTopCount = getLeftCount(verticalIdx, horizontalIdx)
            rightTopCount = getRightCount(verticalIdx, horizontalIdx)
            leftBottomCount = getLeftCount(verticalIdx + 1, horizontalIdx) if isRoad(verticalIdx + 1, horizontalIdx) else getLeftCount(verticalIdx, horizontalIdx)
            rightBottomCount = getRightCount(verticalIdx + 1, horizontalIdx) if isRoad(verticalIdx + 1, horizontalIdx) else getRightCount(verticalIdx, horizontalIdx)
            # print(f"LeftTopCount = {leftTopCount}, rightTopCount = {rightTopCount}, leftBottomCount = {leftBottomCount}, rightBottomCount = {rightBottomCount}")

            # координаты для травы
            xLeftTopGrass = xCenter - self.wp * leftTopCount * self.scale
            xLeftBottomGrass = xCenter - self.wp * leftBottomCount * self.scale
            xRightTopGrass = xCenter + self.wp * rightTopCount * self.scale
            xRightBottomGrass = xCenter + self.wp * rightBottomCount * self.scale

            drawGrass(xLeft, yTop, xLeftTopGrass, yTop, xLeftBottomGrass, yBottom, xLeft, yBottom)
            drawGrass(xRight, yTop, xRightTopGrass, yTop, xRightBottomGrass, yBottom, xRight, yBottom)

        def drawHorizontalRoad(horizontalIdx, verticalIdx):
            xLeft = self.x0 + idxToX(horizontalIdx) * self.scale
            xRight = self.x0 + idxToX(horizontalIdx + 1) * self.scale
            yTop = self.y0 + idxToY(verticalIdx) * self.scale
            yBottom = self.y0 + idxToY(verticalIdx + 1) * self.scale

            drawRectangle(xLeft, yTop, xRight, yBottom, "gray", "gray")

            yCenter = yTop + (yBottom - yTop) // 2

            # рисуем центральную линию: двойная сполшная и т.д.
            # пунктирная линия - параметр dash=(15, 15)
            if (self.wp * self.scale > 5):
                draw.line((xLeft, yCenter - 3, xRight, yCenter - 3), aggdraw.Pen("white", 3))
                draw.line((xLeft, yCenter + 3, xRight, yCenter + 3), aggdraw.Pen("white", 3))

            # количество полос сверху
            leftTopCount = getLeftCount(verticalIdx, horizontalIdx)
            leftBottomCount = getRightCount(verticalIdx, horizontalIdx)

            rightTopCount = getLeftCount(verticalIdx, horizontalIdx + 1) if isRoad(verticalIdx, horizontalIdx + 1) else getLeftCount(verticalIdx, horizontalIdx)
            rightBottomCount = getRightCount(verticalIdx, horizontalIdx + 1) if isRoad(verticalIdx, horizontalIdx + 1) else getRightCount(verticalIdx, horizontalIdx)
            # print(f"LeftTopCount = {leftTopCount}, rightTopCount = {rightTopCount}, leftBottomCount = {leftBottomCount}, rightBottomCount = {rightBottomCount}")

            # координаты для травы
            yLeftTopGrass = yCenter - self.wp * leftTopCount * self.scale
            yRightTopGrass = yCenter - self.wp * rightTopCount * self.scale
            yLeftBottomGrass = yCenter + self.wp * leftBottomCount * self.scale
            yRightBottomGrass = yCenter + self.wp * rightBottomCount * self.scale

            drawGrass(xLeft, yLeftTopGrass, xLeft, yTop, xRight, yTop, xRight, yRightTopGrass)
            drawGrass(xLeft, yLeftBottomGrass, xLeft, yBottom, xRight, yBottom, xRight, yRightBottomGrass)

        image = Image.new("RGBA", (self.horizontalWindow, self.verticalWindow), (255,255,255,255))
        draw = aggdraw.Draw(image)

        for i in range(self.city.shape[0]):
            for j in range(self.city.shape[1]):
                # print("Object ", i, j, "is a road", self.city.city_model[i][j], ": orientation is ", self.city.city_model[i][j].orientation, ", lanes dict: ", self.city.city_model[i][j].lanes,
                #       ", hard marking line type: ", self.city.city_model[i][j].hard_marking, ", soft marking line type: ",
                #       self.city.city_model[i][j].soft_marking, ".") if isinstance(self.city.city_model[i][j], Road) else print(
                #     "Object ", i, j, "is an intersection ", self.city.city_model[i][j], ": lanes count in directions: ",
                #     self.city.city_model[i][j].n_lanes) if isinstance(self.city.city_model[i][j], Intersection) else print(
                #     "Object ", i, j, " is a ground", self.city.city_model[i][j])
                if (isinstance(self.city.city_model[i][j], Road)):

                    if (self.city.city_model[i][j].orientation == "v"):
                        drawVerticalRoad(j, i)
                    else:
                        drawHorizontalRoad(j, i)

                elif (isinstance(self.city.city_model[i][j], Intersection)):
                    drawIntersection(j, i)
                else:
                    drawGround(j, i)

        draw.flush()
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image((0, 0), anchor='nw' ,image=self.tk_image)

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

    def __init__(self):
        super().__init__()

        self.title("env_visualization")

        self.canvas = Canvas(self, width=self.horizontalWindow, height=self.verticalWindow, bg="white")
        self.canvas.pack(expand=1,fill=tk.BOTH)

        self.city = City(map_sample=1, layout_sample=0, narrowing_and_expansion=True)
        #self.city = City(map_sample=2, layout_sample=0, narrowing_and_expansion=True)
        self.vertical = self.verticalWindow // self.city.shape[0]
        self.horizontal = self.horizontalWindow // self.city.shape[1]
        self.wp = self.vertical // 10 if self.vertical < self.horizontal else self.horizontal // 10

        self.drawContent()

        self.canvas.bind('<MouseWheel>', self.canvas_mouseWheel_event)
        self.canvas.bind('<Motion>', self.canvas_motion_event)
        self.canvas.bind('<ButtonPress-1>', self.canvas_buttonPress_event)
        self.canvas.bind('<ButtonRelease-1>', self.canvas_buttonRelease_event)


    def canvas_mouseWheel_event(self, event):
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            if self.scale > 1:
                self.scale -= 0.1
                self.drawContent()
        if event.num == 4 or event.delta == 120:
            self.scale += 0.1
            self.drawContent()
        print('Scale: ', self.scale)

    def canvas_motion_event(self, event):
        if self.moveMode:
            self.updateContent(event.x, event.y)
        self.xMouse = event.x
        self.yMouse = event.y
        # print('Motion: ', event.x, event.y)

    def canvas_buttonPress_event(self, event):
        self.something_clicked = 0
        if self.scale > 1:
            self.moveMode = True
        self.xMouse = event.x
        self.yMouse = event.y
        print('ButtonPress: ', event.x, event.y)

    def canvas_buttonRelease_event(self, event):
        self.something_clicked = 0
        self.moveMode = False
        self.updateContent(event.x, event.y)
        print('ButtonRelease: ', event.x, event.y)

if __name__ == "__main__":
    mapVizualization = MapVizualization()
    mapVizualization.mainloop()