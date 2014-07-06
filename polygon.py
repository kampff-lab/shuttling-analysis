# -*- coding: utf-8 -*-
"""
Created on Sat Oct 05 23:04:42 2013

@author: gonca_000
"""

import math
import numpy as np

def centroid(vertices):
    
    centroid = [0.0, 0.0]
    signedArea = 0.0

    # For all vertices except last
    for i in range(len(vertices)-1):
        x0 = vertices[i][0];
        y0 = vertices[i][1];
        x1 = vertices[i+1][0];
        y1 = vertices[i+1][1];
        a = x0*y1 - x1*y0;
        signedArea += a;
        centroid[0] += (x0 + x1)*a;
        centroid[1] += (y0 + y1)*a;

    # Do last vertex
    x0 = vertices[i][0];
    y0 = vertices[i][1];
    x1 = vertices[0][0];
    y1 = vertices[0][1];
    a = x0*y1 - x1*y0;
    signedArea += a;
    centroid[0] += (x0 + x1)*a;
    centroid[1] += (y0 + y1)*a;

    signedArea *= 0.5;
    centroid[0] /= (6.0*signedArea);
    centroid[1] /= (6.0*signedArea);

    return np.array(centroid)

def area_for_polygon(polygon):
    result = 0
    imax = len(polygon) - 1
    for i in range(0,imax):
        result += (polygon[i][0] * polygon[i+1][1]) - (polygon[i+1][0] * polygon[i][1])
    result += (polygon[imax][0] * polygon[0][1]) - (polygon[0][0] * polygon[imax][1])
    return result / 2.

def centroid_for_polygon(polygon):
    area = area_for_polygon(polygon)
    imax = len(polygon) - 1

    result_x = 0
    result_y = 0
    for i in range(0,imax):
        result_x += (polygon[i][0] + polygon[i+1][0]) * ((polygon[i][0] * polygon[i+1][1]) - (polygon[i+1][0] * polygon[i][1]))
        result_y += (polygon[i][1] + polygon[i+1][1]) * ((polygon[i][0] * polygon[i+1][1]) - (polygon[i+1][0] * polygon[i][1]))
    result_x += (polygon[imax][0] + polygon[0][0]) * ((polygon[imax][0] * polygon[0][1]) - (polygon[0][0] * polygon[imax][1]))
    result_y += (polygon[imax][1] + polygon[0][1]) * ((polygon[imax][0] * polygon[0][1]) - (polygon[0][0] * polygon[imax][1]))
    result_x /= (area * 6.0)
    result_y /= (area * 6.0)

    return np.array([result_x, result_y])

def bottommost_index_for_polygon(polygon):
    bottommost_index = 0
    for index, point in enumerate(polygon):
        if (point[1] < polygon[bottommost_index][1]):
            bottommost_index = index
    return bottommost_index

def angle_for_vector(start_point, end_point):
    y = end_point[1] - start_point[1]
    x = end_point[0] - start_point[0]
    angle = 0

    if (x == 0):
        if (y > 0):
            angle = 90.0
        else:
            angle = 270.0
    elif (y == 0):
        if (x > 0):
            angle = 0.0
        else:
            angle = 180.0
    else:
        angle = math.degrees(math.atan((y+0.0)/x))
        if (x < 0):
            angle += 180
        elif (y < 0):
            angle += 360

    return angle

def convex_hull_for_polygon(polygon):
    starting_point_index = bottommost_index_for_polygon(polygon)
    convex_hull = [polygon[starting_point_index]]
    polygon_length = len(polygon)

    hull_index_candidate = 0 #arbitrary
    previous_hull_index_candidate = starting_point_index
    previous_angle = 0
    while True:
        smallest_angle = 360

        for j in range(0,polygon_length):
            if (previous_hull_index_candidate == j):
                continue
            current_angle = angle_for_vector(polygon[previous_hull_index_candidate], polygon[j])
            if (current_angle < smallest_angle and current_angle > previous_angle):
                hull_index_candidate = j
                smallest_angle = current_angle

        if (hull_index_candidate == starting_point_index): # we've wrapped all the way around
            break
        else:
            convex_hull.append(polygon[hull_index_candidate])
            previous_angle = smallest_angle
            previous_hull_index_candidate = hull_index_candidate

    return np.array(convex_hull)