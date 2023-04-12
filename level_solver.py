# thanks to https://youtu.be/ZuHW4fS60pc for the algorithm

def run(maze):
    finish_points = get_finish_points(maze)

    visited = []
    queue = []

    curent = None

    for row, content in enumerate(maze):
        if "r" in content:
            frontier = [[row, content.index("r")]]

    while curent not in finish_points:
        try:
            curent = frontier[0]
        except IndexError:
            return (0, [])  # succes

        if 0 in curent or 5 in curent:
            return (1, visited + [curent])  # fail

        temp = curent.copy()
        temp[0] -= 1
        try:
            if not (temp in visited or maze[temp[0]][temp[1]] == "w"):
                frontier.append(temp)
        except IndexError:
            pass

        temp = curent.copy()
        temp[0] += 1
        try:
            if not (temp in visited or maze[temp[0]][temp[1]] == "w"):
                frontier.append(temp)
        except IndexError:
            pass

        temp = curent.copy()
        temp[1] -= 1
        try:
            if not (temp in visited or maze[temp[0]][temp[1]] == "w"):
                frontier.append(temp)
        except IndexError:
            pass

        temp = curent.copy()
        temp[1] += 1
        try:
            if not (temp in visited or maze[temp[0]][temp[1]] == "w"):
                frontier.append(temp)
        except IndexError:
            pass

        visited.append(frontier[0])
        del frontier[0]


def get_finish_points(maze):
    res = []
    for index, arr in enumerate(maze):
        if index == 0 or index == len(maze) - 1:
            pass
        else:
            pass
    return res


if __name__ == "__main__":
    example = [['w', 'w', 'w', 'w', 'c', 'c'],
               ['c', 'w', 'r', 'c', 'w', 'c'],
               ['c', 'w', 'w', 'w', 'w', 'c'],
               ['w', 'w', 'w', 'c', 'w', 'c'],
               ['c', 'w', 'c', 'w', 'w', 'w'],
               ['c', 'c', 'c', 'w', 'w', 'c']]

    print(run(example))
