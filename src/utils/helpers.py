def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

def random_choice(choices):
    return random.choice(choices)

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def lerp(start, end, t):
    return start + (end - start) * t

def distance(point1, point2):
    return math.hypot(point1[0] - point2[0], point1[1] - point2[1])