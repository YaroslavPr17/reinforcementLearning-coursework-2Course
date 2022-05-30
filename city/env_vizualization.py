from Environment.city import City
from Environment.objects.road import Road
from Environment.objects.intersection import Intersection
from tkinter import *

def main():
    #city = City(map_sample=0, layout_sample=0, narrowing_and_expansion=True)
    city = City(map_sample=1, layout_sample=0, narrowing_and_expansion=True)

    root = Tk()
    root.title("env_visualization")
    verticalWindow = 1440 // 3 * 2
    horizontalWindow = 2560 // 3 * 2
    c = Canvas(root, width=horizontalWindow, height=verticalWindow, bg='white')
    c.pack(pady=20)

    vertical = verticalWindow // city.shape[0]
    horizontal = horizontalWindow // city.shape[1]
    wp = vertical // 10 if vertical < horizontal else horizontal // 10

    def drawRectangle(xLeft, yTop, xRight, yBottom, fillColor, lineColor):
        c.create_rectangle(xLeft, yTop, xRight, yBottom, fill=fillColor, outline=lineColor)

    def drawGrass(x0, y0, x1, y1, x2, y2, x3, y3):
        c.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3,  fill="green")

    def idxToX(idx):
        return idx * horizontal

    def idxToY(idx):
        return idx * vertical

    def isRoad(i, j):
        return ((i > 0) and (i <= city.shape[0]) and (j > 0) and (j <= city.shape[1]) and (isinstance(city.city_model[i][j], Road)))

    def getLeftCount(i, j):
        return [len(value) for key, value in city.city_model[i][j].lanes.items()][1]

    def getRightCount(i, j):
        return [len(value) for key, value in city.city_model[i][j].lanes.items()][0]


    def drawGround(horizontalIdx, verticalIdx):
        xLeft = idxToX(horizontalIdx)
        xRight = idxToX(horizontalIdx + 1)
        yTop = idxToY(verticalIdx)
        yBottom = idxToY(verticalIdx + 1) #?

        drawRectangle(xLeft, yTop, xRight, yBottom, "green", "green")

    def drawIntersection(horizontalIdx, verticalIdx):
        xLeft = idxToX(horizontalIdx)
        xRight = idxToX(horizontalIdx + 1)
        yTop = idxToY(verticalIdx)
        yBottom = idxToY(verticalIdx + 1) #?

        drawRectangle(xLeft, yTop, xRight, yBottom, "green", "green")

        xCenter = xLeft + (xRight - xLeft) // 2
        yCenter = yTop + (yBottom - yTop) // 2

        xLeftTop = xCenter
        xRightTop = xCenter
        if (isRoad(verticalIdx - 1, horizontalIdx)):
            xLeftTop = xCenter - wp * getLeftCount(verticalIdx - 1, horizontalIdx)
            xRightTop = xCenter + wp * getRightCount(verticalIdx - 1, horizontalIdx)
        elif (isRoad(verticalIdx + 1, horizontalIdx)):
            xLeftTop = xCenter - wp * getLeftCount(verticalIdx + 1, horizontalIdx)
            xRightTop = xCenter + wp * getRightCount(verticalIdx + 1, horizontalIdx)

        xLeftBottom = xCenter
        xRightBottom = xCenter
        if (isRoad(verticalIdx + 1, horizontalIdx)):
            xLeftBottom = xCenter - wp * getLeftCount(verticalIdx + 1, horizontalIdx)
            xRightBottom = xCenter + wp * getRightCount(verticalIdx + 1, horizontalIdx)
        elif (isRoad(verticalIdx - 1, horizontalIdx)):
            xLeftBottom = xCenter - wp * getLeftCount(verticalIdx - 1, horizontalIdx)
            xRightBottom = xCenter + wp * getRightCount(verticalIdx - 1, horizontalIdx)

        yLeftTop = yCenter
        yLeftBottom = yCenter
        if (isRoad(verticalIdx, horizontalIdx - 1)):
            yLeftTop = yCenter - wp * getLeftCount(verticalIdx, horizontalIdx - 1)
            yLeftBottom = yCenter + wp * getRightCount(verticalIdx, horizontalIdx - 1)
        elif (isRoad(verticalIdx, horizontalIdx + 1)):
            yLeftTop = yCenter - wp * getLeftCount(verticalIdx, horizontalIdx + 1)
            yLeftBottom = yCenter + wp * getRightCount(verticalIdx, horizontalIdx + 1)

        yRightTop = yCenter
        yRightBottom = yCenter
        if (isRoad(verticalIdx, horizontalIdx + 1)):
            yRightTop = yCenter - wp * getLeftCount(verticalIdx, horizontalIdx + 1)
            yRightBottom = yCenter + wp * getRightCount(verticalIdx, horizontalIdx + 1)
        elif (isRoad(verticalIdx, horizontalIdx - 1)):
            yRightTop = yCenter - wp * getLeftCount(verticalIdx, horizontalIdx - 1)
            yRightBottom = yCenter + wp * getRightCount(verticalIdx, horizontalIdx - 1)

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

        c.create_polygon(points, fill="gray", outline="gray")

    def drawVerticalRoad(horizontalIdx, verticalIdx):
        xLeft = idxToX(horizontalIdx)
        xRight = idxToX(horizontalIdx + 1)
        yTop = idxToY(verticalIdx)
        yBottom = idxToY(verticalIdx + 1) #?

        drawRectangle(xLeft, yTop, xRight, yBottom, "gray", "gray")

        xCenter = xLeft + (xRight - xLeft) // 2

        # рисуем центральную линию: двойная сполшная и т.д.
        # пунктирная линия - параметр dash=(15, 15)
        if(wp > 5):
            c.create_line(xCenter - 3, yTop, xCenter - 3, yBottom, width=2, fill="white")
            c.create_line(xCenter + 3, yTop, xCenter + 3, yBottom, width=2, fill="white")

        # количество полос сверху
        leftTopCount = getLeftCount(verticalIdx, horizontalIdx)
        rightTopCount = getRightCount(verticalIdx, horizontalIdx)
        leftBottomCount = getLeftCount(verticalIdx + 1, horizontalIdx) if isRoad(verticalIdx + 1, horizontalIdx) else getLeftCount(verticalIdx, horizontalIdx)
        rightBottomCount = getRightCount(verticalIdx + 1, horizontalIdx) if isRoad(verticalIdx + 1, horizontalIdx) else getRightCount(verticalIdx, horizontalIdx)
        print(f"LeftTopCount = {leftTopCount}, rightTopCount = {rightTopCount}, leftBottomCount = {leftBottomCount}, rightBottomCount = {rightBottomCount}")

        # координаты для травы
        xLeftTopGrass = xCenter - wp * leftTopCount
        xLeftBottomGrass = xCenter - wp * leftBottomCount
        xRightTopGrass = xCenter + wp * rightTopCount
        xRightBottomGrass = xCenter + wp * rightBottomCount


        drawGrass(xLeft, yTop, xLeftTopGrass, yTop, xLeftBottomGrass, yBottom, xLeft, yBottom)
        drawGrass(xRight, yTop, xRightTopGrass, yTop, xRightBottomGrass, yBottom, xRight, yBottom)

    def drawHorizontalRoad(horizontalIdx, verticalIdx):
        xLeft = idxToX(horizontalIdx)
        xRight = idxToX(horizontalIdx + 1)
        yTop = idxToY(verticalIdx)
        yBottom = idxToY(verticalIdx + 1) #?

        drawRectangle(xLeft, yTop, xRight, yBottom, "gray", "gray")

        yCenter = yTop + (yBottom - yTop) // 2

        # рисуем центральную линию: двойная сполшная и т.д.
        #пунктирная линия - параметр dash=(15, 15)
        if(wp > 5):
            c.create_line(xLeft, yCenter - 3, xRight, yCenter - 3, width=2, fill="white")
            c.create_line(xLeft, yCenter + 3, xRight, yCenter + 3, width=2, fill="white")

        # количество полос сверху
        leftTopCount = getLeftCount(verticalIdx, horizontalIdx)
        leftBottomCount = getRightCount(verticalIdx, horizontalIdx)

        rightTopCount = getLeftCount(verticalIdx, horizontalIdx + 1) if isRoad(verticalIdx, horizontalIdx + 1) else getLeftCount(verticalIdx, horizontalIdx)
        rightBottomCount = getRightCount(verticalIdx, horizontalIdx + 1) if isRoad(verticalIdx, horizontalIdx + 1) else getRightCount(verticalIdx, horizontalIdx)
        print(f"LeftTopCount = {leftTopCount}, rightTopCount = {rightTopCount}, leftBottomCount = {leftBottomCount}, rightBottomCount = {rightBottomCount}")

        # координаты для травы
        yLeftTopGrass = yCenter - wp * leftTopCount
        yRightTopGrass = yCenter - wp * rightTopCount
        yLeftBottomGrass = yCenter + wp * leftBottomCount
        yRightBottomGrass = yCenter + wp * rightBottomCount


        drawGrass(xLeft, yLeftTopGrass, xLeft, yTop, xRight, yTop, xRight, yRightTopGrass)
        drawGrass(xLeft, yLeftBottomGrass, xLeft, yBottom, xRight, yBottom, xRight, yRightBottomGrass)



    for i in range(city.shape[0]):
        for j in range(city.shape[1]):
            print("Object ", i, j, "is a road", city.city_model[i][j], ": orientation is ", city.city_model[i][j].orientation, ", lanes dict: ", city.city_model[i][j].lanes, ", hard marking line type: ", city.city_model[i][j].hard_marking, ", soft marking line type: ", city.city_model[i][j].soft_marking, ".") if isinstance(city.city_model[i][j], Road) else print( "Object ", i, j, "is an intersection ", city.city_model[i][j], ": lanes count in directions: ", city.city_model[i][j].n_lanes) if isinstance(city.city_model[i][j], Intersection) else print( "Object ", i, j, " is a ground", city.city_model[i][j])
            if (isinstance(city.city_model[i][j], Road)):

                if (city.city_model[i][j].orientation == "v"):
                    drawVerticalRoad(j, i)
                else:
                    drawHorizontalRoad(j, i)

            elif (isinstance(city.city_model[i][j], Intersection)):
                drawIntersection(j, i)
            else:
                drawGround(j, i)

    root.mainloop()



#
if __name__ == "__main__":
    main()