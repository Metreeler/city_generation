import numpy as np
import cv2 as cv
import time
import random
import string



def random_number(seed, x, y, z=None):
    if z is None:
        z = x + y + x * y
    a = x * np.cos(x) + y * np.sin(x) + 1 / (1 + np.exp(np.cos(x + y)))
    b = x * np.cos(y) + y * np.sin(y) + 1 / (1 + np.exp(np.sin(x + y)))
    c = x * np.cos(z) + y * np.sin(z) + 1 / (1 + np.exp(np.cos(z)))
    seed_value = int(seed[:min(5, len(seed))], 36)
    d = seed_value * (a + b + c)
    return (((a * b * c * d) % 10477) / 10477)


# def normalize_vector(v):
#     norm = np.linalg.norm(v)
#     if norm == 0: 
#        return v
#     return v / norm


def normalize_array(arr, low, high):
    if np.max(arr) > np.min(arr):
        return (high - low) * (arr - np.min(arr)) / (np.max(arr) - np.min(arr)) + low
    return arr


def interpolate(a0, a1, w, interpolate_function="linear"):
    if interpolate_function == "smoothstep":
        return (a1 - a0) * ((w * (w * 6.0 - 15.0) + 10.0) * w * w * w) + a0
    elif interpolate_function == "cubic":
        return (a1 - a0) * (3.0 - w * 2.0) * w * w + a0
    return (a1 - a0) * w + a0


def noise(v00x, v10x, v01x, v11x, v00y, v10y, v01y, v11y, co_x, co_y):
    
    n0 = v00x * co_x + v00y * co_y
    n1 = v10x * (co_x - 1) + v10y * co_y
    n2 = v01x * co_x + v01y * (co_y - 1)
    n3 = v11x * (co_x - 1) + v11y * (co_y - 1)

    ix0 = interpolate(n0, n1, co_x, "smoothstep")
    ix1 = interpolate(n2, n3, co_x, "smoothstep")

    return interpolate(ix0, ix1, co_y, "smoothstep")


def get_bounding_values(vectors, x , y):
    out = np.zeros((4, 2))
    out[0] = vectors[x, y]
    out[1] = vectors[x + 1, y]
    out[2] = vectors[x, y + 1]
    out[3] = vectors[x + 1, y + 1]
    return out


def noise_layer(seed: string, 
                row: int, 
                col: int, 
                first_layer_division: int = 0,
                octave: int | None = None, 
                min_cell_size: int = 3, 
                degeneration_rate: float = 0.5,
                gradient_use: bool = True):
    """
    Generate 2D Perlin Noise
    
    Args:
        seed (string): The seed determining the randomness of the noise created.
        row (int): Number of rows.
        col (int): Number of columns.
        first_layer_division (int): Number of division of the first perlin layer, default value = 0.
        octave (int | None): Number of perlin layers, default value = None.
        min_cell_size (int): Minimum size of the last layer division, default value = 2.
        degeneration_rate (float): Degenration rate, default value = 0.5.
    Returns:
        np.array: A 2D numpy array with perlin noise values between 0 and 1
    """
    gt0 = time.time()

    min_dim = min(row, col)
    start_dimensions = []

    for s in [row, col]:
        if s / min_dim > int(s / min_dim):
            start_dimensions.append(int(s / min_dim) + 1)
        else:
            start_dimensions.append(int(s / min_dim))
    
    out = np.zeros((row, col))

    gt1 = time.time()

    oc = first_layer_division

    if min_dim / (2 ** oc) > int(min_dim / (2 ** oc)):
        steps = int(min_dim / (2 ** oc)) + 1
    else:
        steps = int(min_dim / (2 ** oc))
    
    if octave is None:
        octave = 0
        while min_dim / (2 ** (octave)) > min_cell_size - 1:
            octave += 1
    else:
        octave += oc

    gt2 = time.time()

    gradient_x, gradient_y = np.zeros((row, col)), np.zeros((row, col))

    gt3 = time.time()

    while oc < octave:
        
        print("Layer :", oc, "cell_size :", steps)

        ############################

        vec_dim = np.zeros((3))
        vec_dim[0:2] = np.array(start_dimensions) * (2 ** oc) + 1
        vec_dim[2] = 2
        vec_dim = vec_dim.astype(int)

        vectors = np.zeros(vec_dim)

        positions_i = np.arange(0.0, vec_dim[0])
        positions_i = np.repeat(positions_i, vec_dim[1])
        positions_i = np.repeat(positions_i, vec_dim[2])
        positions_i = np.reshape(positions_i, vec_dim)

        positions_j = np.arange(0.0, vec_dim[1])
        positions_j = np.repeat(positions_j, vec_dim[2])
        positions_j = np.tile(positions_j, vec_dim[0])
        positions_j = np.reshape(positions_j, vec_dim)

        positions_k = np.arange(0.0, vec_dim[2])
        positions_k = np.tile(positions_k, vec_dim[0])
        positions_k = np.tile(positions_k, vec_dim[1])
        positions_k = np.reshape(positions_k, vec_dim)

        layer_seed = seed[(oc % len(seed)):] + seed[:(oc % len(seed))]

        vectors = random_number(layer_seed, positions_i, positions_j, positions_k) * 2 - 1

        ############################

        dimensions = np.array(start_dimensions) * (2 ** oc)
        
        layer = np.zeros(dimensions * steps)

        t0 = time.time()

        s = 1 / steps
        positions_n = np.arange(0.0, 1.0, s)
        positions_n = np.tile(positions_n, (steps, 1))
        positions_m = positions_n.T

        positions_m = np.tile(positions_m, (dimensions[0], dimensions[1]))
        positions_n = np.tile(positions_n, (dimensions[0], dimensions[1]))

        pos_j = np.arange(dimensions[1])
        pos_j = np.tile(pos_j, (dimensions[0], 1))
        pos_i = np.arange(dimensions[0])
        pos_i = np.tile(pos_i, (dimensions[1], 1))
        pos_i = pos_i.T

        t1 = time.time()

        vec_bound_00_x = vectors[pos_i, pos_j, 0]
        vec_bound_10_x = vectors[pos_i + 1, pos_j, 0]
        vec_bound_01_x = vectors[pos_i, pos_j + 1, 0]
        vec_bound_11_x = vectors[pos_i + 1, pos_j + 1, 0]
        vec_bound_00_y = vectors[pos_i, pos_j, 1]
        vec_bound_10_y = vectors[pos_i + 1, pos_j, 1]
        vec_bound_01_y = vectors[pos_i, pos_j + 1, 1]
        vec_bound_11_y = vectors[pos_i + 1, pos_j + 1, 1]

        t2 = time.time()
        
        vec_bound_00_x = np.repeat(vec_bound_00_x, steps, axis=0)
        vec_bound_00_x = np.repeat(vec_bound_00_x, steps, axis=1)
        vec_bound_10_x = np.repeat(vec_bound_10_x, steps, axis=0)
        vec_bound_10_x = np.repeat(vec_bound_10_x, steps, axis=1)
        vec_bound_01_x = np.repeat(vec_bound_01_x, steps, axis=0)
        vec_bound_01_x = np.repeat(vec_bound_01_x, steps, axis=1)
        vec_bound_11_x = np.repeat(vec_bound_11_x, steps, axis=0)
        vec_bound_11_x = np.repeat(vec_bound_11_x, steps, axis=1)
        vec_bound_00_y = np.repeat(vec_bound_00_y, steps, axis=0)
        vec_bound_00_y = np.repeat(vec_bound_00_y, steps, axis=1)
        vec_bound_10_y = np.repeat(vec_bound_10_y, steps, axis=0)
        vec_bound_10_y = np.repeat(vec_bound_10_y, steps, axis=1)
        vec_bound_01_y = np.repeat(vec_bound_01_y, steps, axis=0)
        vec_bound_01_y = np.repeat(vec_bound_01_y, steps, axis=1)
        vec_bound_11_y = np.repeat(vec_bound_11_y, steps, axis=0)
        vec_bound_11_y = np.repeat(vec_bound_11_y, steps, axis=1)

        t3 = time.time()

        layer = noise(vec_bound_00_x,
                      vec_bound_10_x,
                      vec_bound_01_x,
                      vec_bound_11_x,
                      vec_bound_00_y,
                      vec_bound_10_y,
                      vec_bound_01_y,
                      vec_bound_11_y,
                      positions_m,
                      positions_n)

        t4 = time.time()

        

        # print(t1 - t0)
        # print(t2 - t1)
        # print(t3 - t2)
        # print(t4 - t3)

        # print(t4 - t0)

        # print("#" * 10)

        # print(100 * (t1 - t0) / (t4 - t0))
        # print(100 * (t2 - t1) / (t4 - t0))
        # print(100 * (t3 - t2) / (t4 - t0))
        # print(100 * (t4 - t3) / (t4 - t0))

        if gradient_use:
            grad_x, grad_y = np.gradient(layer[:row, :col])
            gradient_x += grad_x
            gradient_y += grad_y
            gradient = np.sqrt(gradient_x ** 2 + gradient_y ** 2)
            k = 80
            final_gradient = 1 / (1 + k * gradient)

            # cv.imwrite("data/grad_" + str(oc) + ".png", (normalize_array(final_gradient, 0, 1) * 255).astype(np.uint8))
        else:
            final_gradient = np.ones((row, col))

        out += layer[:row, :col] * (degeneration_rate ** oc) * final_gradient

        oc += 1

        if min_dim / (2 ** oc) > int(min_dim / (2 ** oc)):
            steps = int(min_dim / (2 ** oc)) + 1
        else:
            steps = int(min_dim / (2 ** oc))

    gt4 = time.time()

    # print(100 * (gt1 - gt0) / (gt4 - gt0))
    # print(100 * (gt2 - gt1) / (gt4 - gt0))
    # print(100 * (gt3 - gt2) / (gt4 - gt0))
    # print(100 * (gt4 - gt3) / (gt4 - gt0))

    # print(gt1 - gt0)
    # print(gt2 - gt1)
    # print(gt3 - gt2)
    # print(gt4 - gt3)

    return normalize_array(out, 0, 1)


if __name__ == "__main__":

    s = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    print(s)
    # row, col = 2160, 3840
    row, col = 1024, 1024
    
    src = noise_layer(s, 
                      row, 
                      col, 
                      0,
                      None,
                      5,
                      0.5,
                      False)
    
    img = np.zeros((src.shape[0], src.shape[1], 3))
    ocean = 0.4

    img_b = np.where(src < ocean, 210, 35 + (110 - 35) * (src - ocean) / (1 - ocean))
    img_g = np.where(src < ocean, 125, 117 + (155 - 117) * (src - ocean) / (1 - ocean))
    img_r = np.where(src < ocean, 105, 140 + (170 - 140) * (src - ocean) / (1 - ocean))

    # img_b = np.where(src < ocean, 210, 101)
    # img_g = np.where(src < ocean, 125, 163)
    # img_r = np.where(src < ocean, 105, 116)

    img[:, :, 0] = img_b
    img[:, :, 1] = img_g
    img[:, :, 2] = img_r
    
    print(img.shape)
    
    cv.imwrite("data/noise.png", (src * 255).astype(np.uint8))
    cv.imwrite("data/map.png", (img).astype(np.uint8))

