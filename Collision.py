import math,numpy



def rays_triangles_intersection(ray_origin, ray_direction, triangles_vertices):
    
    """
    Möller–Trumbore intersection algorithm for calculating whether the ray intersects the triangle
    and for which t-value. Based on: https://github.com/kliment/Printrun/blob/master/printrun/stltool.py,
    which is based on:
    http://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    Parameters
    ----------
    ray_origin : np.ndarray(3)
        Origin coordinate (x, y, z) from which the ray is fired
        
    ray_directions : np.ndarray(n, 3)
        Directions (dx, dy, dz) in which the rays are going
        
    triangle_vertices : np.ndarray(m, 3, 3)
        3D vertices of multiple triangles
        
    Returns
    -------
    tuple[np.ndarray<bool>(n, m), np.ndarray(n, m)]
        The first array indicates whether or not there was an intersection, the second array
        contains the t-values of the intersections
    """

    output_shape = (len(ray_direction), len(triangles_vertices))

    all_rays_t = np.zeros(output_shape)
    all_rays_intersected = np.full(output_shape, True)

    v1 = triangles_vertices[0]
    v2 = triangles_vertices[1]
    v3 = triangles_vertices[2]

    eps = 0.000001

    edge1 = (v2[0] - v1[0],v2[1] - v1[1],v2[2] - v1[2])
    edge2 = (v3[0] - v1[0],v3[1] - v1[1],v3[2] - v1[2])

    for i, ray in enumerate(ray_direction):
        all_t = np.zeros((len(triangles_vertices)))
        intersected = np.full((len(triangles_vertices)), True)

        pvec = np.cross(ray, edge2)

        det = np.sum(edge1 * pvec, axis=1)

        non_intersecting_original_indices = np.absolute(det) < eps

        all_t[non_intersecting_original_indices] = np.nan
        intersected[non_intersecting_original_indices] = False

        inv_det = 1.0 / det

        tvec = ray_origin - v1

        u = np.sum(tvec * pvec, axis=1) * inv_det

        non_intersecting_original_indices = (u < 0.0) + (u > 1.0)
        all_t[non_intersecting_original_indices] = np.nan
        intersected[non_intersecting_original_indices] = False

        qvec = np.cross(tvec, edge1)

        v = np.sum(ray * qvec, axis=1) * inv_det

        non_intersecting_original_indices = (v < 0.0) + (u + v > 1.0)

        all_t[non_intersecting_original_indices] = np.nan
        intersected[non_intersecting_original_indices] = False

        t = (
            np.sum(
                edge2 * qvec,
                axis=1,
            )
            * inv_det
        )

        non_intersecting_original_indices = t < eps
        all_t[non_intersecting_original_indices] = np.nan
        intersected[non_intersecting_original_indices] = False

        intersecting_original_indices = np.invert(non_intersecting_original_indices)
        all_t[intersecting_original_indices] = t[intersecting_original_indices]

        all_rays_t[i] = all_t
        all_rays_intersected[i] = intersected

    return all_rays_intersected, all_rays_t




def intersect_ray_sphere(ray_origin, ray_direction, sphere_center, sphere_radius):
    
    oc = (
        ray_origin[0] - sphere_center[0],
        ray_origin[1] - sphere_center[1],
        ray_origin[2] - sphere_center[2]
    )

    a = ray_direction[0] ** 2 + ray_direction[1] ** 2 + ray_direction[2] ** 2
    b = 2 * (oc[0] * ray_direction[0] + oc[1] * ray_direction[1] + oc[2] * ray_direction[2])
    c = oc[0] ** 2 + oc[1] ** 2 + oc[2] ** 2 - sphere_radius ** 2

    discriminant = b ** 2 - 4 * a * c

    if discriminant < 0:
        return None
    else:
        t1 = (-b - math.sqrt(discriminant)) / (2 * a)
        t2 = (-b + math.sqrt(discriminant)) / (2 * a)

        if t1 >= 0:
            intersection_point = (
                ray_origin[0] + t1 * ray_direction[0],
                ray_origin[1] + t1 * ray_direction[1],
                ray_origin[2] + t1 * ray_direction[2]
            )
            return intersection_point
        
        elif t2 >= 0:
            intersection_point = (
                ray_origin[0] + t2 * ray_direction[0],
                ray_origin[1] + t2 * ray_direction[1],
                ray_origin[2] + t2 * ray_direction[2]
            )
            return intersection_point
        else:
            return None
    
