import math
import turtle as t

def turn(angle, state=None):
    if state is None:
        if angle > 0:
            t.left(angle)
        elif angle < 0:
            t.right(-angle)
    else:
        state["heading"] = (state["heading"] + angle) % 360

def forward(length, state=None, trace=None):
    if state is None:
        t.forward(length)
    else:
        rad = math.radians(state["heading"])
        newx = state["x"] + math.cos(rad) * length
        newy = state["y"] + math.sin(rad) * length
        if trace is not None:
            trace.append((newx, newy))
        state["x"], state["y"] = newx, newy

def koch_inward(length, depth, sign, state=None, trace=None):
    if depth == 0:
        forward(length, state, trace)
        return
    koch_inward(length / 3, depth - 1, sign, state, trace)
    turn(sign * 60, state)
    koch_inward(length / 3, depth - 1, sign, state, trace)
    turn(-sign * 120, state)
    koch_inward(length / 3, depth - 1, sign, state, trace)
    turn(sign * 60, state)
    koch_inward(length / 3, depth - 1, sign, state, trace)

def simulate_path(n_sides, side_len, depth):
    state = {"x": 0.0, "y": 0.0, "heading": 0.0}
    points = [(0.0, 0.0)]
    exterior_turn = 360.0 / n_sides
    sign = 1
    for _ in range(n_sides):
        koch_inward(side_len, depth, sign, state, points)
        turn(exterior_turn, state)
    return points

def draw_fractal_polygon(n_sides, side_len, depth):
    path = simulate_path(n_sides, side_len, depth)
    xs = [p[0] for p in path]
    ys = [p[1] for p in path]
    cx = (max(xs) + min(xs)) / 2
    cy = (max(ys) + min(ys)) / 2

    shifted = [(x - cx, y - cy) for (x, y) in path]

    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    pad = 50
    screen = t.Screen()
    screen.setup(width=int(w + pad), height=int(h + pad))
    screen.title("Perfectly Centered Fractal Polygon")

    t.penup()
    t.goto(shifted[0])
    t.pendown()
    for pt in shifted[1:]:
        t.goto(pt)

def main():
    try:
        n_sides = int(input("Enter the number of sides: ").strip())
        side_len = float(input("Enter the side length (pixels): ").strip())
        depth = int(input("Enter the recursion depth: ").strip())
        if n_sides < 3 or side_len <= 0 or depth < 0:
            raise ValueError
    except Exception:
        print("Please enter valid values: sides >= 3, side length > 0, depth >= 0.")
        return

    t.hideturtle()
    t.speed(0)
    t.tracer(False)

    draw_fractal_polygon(n_sides, side_len, depth)

    t.tracer(True)
    t.done()

if __name__ == "__main__":
    main()
