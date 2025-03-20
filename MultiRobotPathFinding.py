#Roll No:22I-1134
#Name: Ahmad Aqeel
#Section: CS-G


import heapq
import re

class GridWorld:
    def __init__(self, grid, robots, dynamicAgents):
        self.grid = grid
        self.robots = robots
        self.dynamicAgents = dynamicAgents
        self.robotPaths = []

    def getAgentPosition(self, agent, t):
        path = agent['path']
        times = agent['times']
        if not path or not times:
            return None
        if t in times:
            return path[times.index(t)]
        t0 = times[0]
        tn = times[-1]
        if t < t0 or t < 0:
            return None
        cycleLength = 2 * (len(path) - 1)
        tPrime = t - tn
        if tPrime < 0:
            return None
        cycleStep = tPrime % cycleLength
        if cycleStep < len(path) - 1:
            index = cycleStep
        else:
            index = 2 * (len(path) - 1) - cycleStep
        if 0 <= index < len(path):
            return path[index]
        return None

    def getDynamicAgentPositions(self, t):
        positions = set()
        for agent in self.dynamicAgents:
            pos = self.getAgentPosition(agent, t)
            if pos:
                positions.add((pos[0], pos[1]))
        return positions

    def isValid(self, x, y, t, robotId):
        if x < 0 or y < 0 or x >= len(self.grid) or y >= len(self.grid[0]):
            return False
        if self.grid[x][y] == 'X':
            return False
        dynamicPos = self.getDynamicAgentPositions(t)
        if (x, y) in dynamicPos:
            return False
        for idx, robot in enumerate(self.robots):
            if idx == robotId:
                continue
            if idx >= len(self.robotPaths):
                continue
            path = self.robotPaths[idx]
            if t < len(path):
                otherPos = path[t]
            else:
                otherPos = robot['goal']
            if (x, y) == otherPos:
                return False
        return True

    def adjustStartPosition(self, start, robotId):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            newX = start[0] + dx
            newY = start[1] + dy
            if 0 <= newX < len(self.grid) and 0 <= newY < len(self.grid[0]):
                if self.grid[newX][newY] != 'X' and self.isValid(newX, newY, 0, robotId):
                    return (newX, newY)
        return None

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def planPaths(self):
        self.robotPaths = []
        for i in range(len(self.robots)):
            path, time = self.findPath(i)
            if path:
                self.robotPaths.append(path)
            else:
                self.robotPaths.append([])
        return self.robotPaths

    def findPath(self, robotId):
        start = self.robots[robotId]['start']
        goal = self.robots[robotId]['goal']

        if (start[0] < 0 or start[0] >= len(self.grid) or start[1] < 0 or start[1] >= len(self.grid[0]) or
            goal[0] < 0 or goal[0] >= len(self.grid) or goal[1] < 0 or goal[1] >= len(self.grid[0])):
            return None, None

        if self.grid[start[0]][start[1]] == 'X':
            adjustedStart = self.adjustStartPosition(start, robotId)
            if adjustedStart is None:
                return None, None
            self.robots[robotId]['start'] = adjustedStart
            start = adjustedStart

        if self.grid[goal[0]][goal[1]] == 'X':
            return None, None

        heap = []
        heapq.heappush(heap, (0 + self.heuristic(start, goal), 0, start[0], start[1], 0, []))
        visited = set()
        while heap:
            fVal, gVal, x, y, t, path = heapq.heappop(heap)
            if (x, y) == goal:
                fullPath = path + [(x, y)]
                return fullPath, gVal
            if (x, y, t) in visited:
                continue
            visited.add((x, y, t))
            if self.isValid(x, y, t + 1, robotId):
                newG = gVal + 1
                newF = newG + self.heuristic((x, y), goal)
                newPath = path + [(x, y)]
                heapq.heappush(heap, (newF, newG, x, y, t + 1, newPath))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                newX = x + dx
                newY = y + dy
                newT = t + 1
                if self.isValid(newX, newY, newT, robotId):
                    newG = gVal + 1
                    newF = newG + self.heuristic((newX, newY), goal)
                    newPath = path + [(x, y)]
                    heapq.heappush(heap, (newF, newG, newX, newY, newT, newPath))
        return None, None

def main():
    grid = []
    with open('D:/University Docs/Semester 6/AI/Data/data4.txt', 'r') as f:
        size = int(f.readline().strip())
        for _ in range(size):
            line = f.readline().strip('\n')
            row = []
            paddedLine = line.ljust(size)[:size]
            for c in paddedLine:
                row.append('X' if c == 'X' else '.')
            grid.append(row)
    
    robots = []
    with open('D:/University Docs/Semester 6/AI/Data/Robots4.txt', 'r') as f:
        for line in f:
            matches = re.findall(r'\((\d+),\s*(\d+)\)', line)
            if len(matches) == 2:
                start = (int(matches[0][0]), int(matches[0][1]))
                end = (int(matches[1][0]), int(matches[1][1]))
                robots.append({'start': start, 'goal': end})
    
    dynamicAgents = []
    with open('D:/University Docs/Semester 6/AI/Data/Agent4.txt', 'r') as f:
        for line in f:
            if not line.startswith('Agent'):
                continue
            agentPart, timesPart = line.split(' at times ')
            pathStr = agentPart.split('[', 1)[1].split(']', 1)[0]
            path = []
            tuples = pathStr.split('), (')
            for tup in tuples:
                tup = tup.strip('() ')
                if not tup:
                    continue
                x, y = map(int, tup.split(','))
                path.append((x, y))
            timesStr = timesPart.strip('[]\n')
            times = list(map(int, timesStr.split(', ')))
            combined = sorted(zip(times, path), key=lambda x: x[0])
            sortedTimes = [t for t, p in combined]
            sortedPath = [p for t, p in combined]
            dynamicAgents.append({'path': sortedPath, 'times': sortedTimes})
    
    world = GridWorld(grid, robots, dynamicAgents)
    paths = world.planPaths()
    
    for i, path in enumerate(paths):
        if path:
            print(f"Robot {i+1} Path: {path}")
            print(f"Total Time: {len(path)-1}")
        else:
            print(f"Robot {i+1} has no valid path.")

if __name__ == "__main__":
    main()