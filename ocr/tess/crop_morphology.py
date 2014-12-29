#!/usr/bin/env python
import sys
import random
import math
import json
from collections import defaultdict

import cv2
from PIL import Image, ImageDraw
import numpy as np
from scipy.ndimage.filters import rank_filter


def dilate(ary, N, iterations): 
    """Dilate using an NxN '+' sign shape. ary is np.uint8."""
    kernel = np.zeros((N,N), dtype=np.uint8)
    kernel[(N-1)/2,:] = 1
    dilated_image = cv2.dilate(ary / 255, kernel, iterations=iterations)

    kernel = np.zeros((N,N), dtype=np.uint8)
    kernel[:,(N-1)/2] = 1
    dilated_image = cv2.dilate(dilated_image, kernel, iterations=iterations)
    return dilated_image


def props_for_contours(contours, ary):
    """Calculate bounding box & the number of set pixels for each contour."""
    c_info = []
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        c_im = np.zeros(ary.shape)
        cv2.drawContours(c_im, [c], 0, 255, -1)
        c_info.append({
            'x1': x,
            'y1': y,
            'x2': x + w - 1,
            'y2': y + h - 1,
            'sum': np.sum(ary * (c_im > 0))/255
        })
    return c_info


def union_crops(crop1, crop2):
    """Union two (x1, y1, x2, y2) rects."""
    x11, y11, x21, y21 = crop1
    x12, y12, x22, y22 = crop2
    return min(x11, x12), min(y11, y12), max(x21, x22), max(y21, y22)


def crop_area(crop):
    x1, y1, x2, y2 = crop
    return (x2 - x1) * (y2 - y1)


def find_border_components(contours, ary):
    borders = []
    area = ary.shape[0] * ary.shape[1]
    for i, c in enumerate(contours):
        x,y,w,h = cv2.boundingRect(c)
        if w * h > 0.5 * area:
            borders.append((i, x, y, x + w - 1, y + h - 1))
    return borders


def angle_from_right(deg):
    return min(deg % 90, 90 - (deg % 90))


def remove_border(contour, ary):
    """Remove everything outside a border contour."""
    # Use a rotated rectangle (should be a good approximation of a border).
    # If it's far from a right angle, it's probably two sides of a border and
    # we should use the bounding box instead.
    c_im = np.zeros(ary.shape)
    r = cv2.minAreaRect(contour)
    degs = r[2]
    if angle_from_right(degs) <= 10.0:
        box = cv2.cv.BoxPoints(r)
        box = np.int0(box)
        cv2.drawContours(c_im, [box], 0, 255, -1)
        cv2.drawContours(c_im, [box], 0, 0, 4)
    else:
        x1, y1, x2, y2 = cv2.boundingRect(contour)
        cv2.rectangle(c_im, (x1, y1), (x2, y2), 255, -1)
        cv2.rectangle(c_im, (x1, y1), (x2, y2), 0, 4)

    return np.minimum(c_im, edges)


if __name__ == '__main__':
    for path in sys.argv[1:]:
        im = Image.open(path)
        edges = cv2.Canny(np.asarray(im), 100, 200)

        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        borders = find_border_components(contours, edges)
        borders.sort(key=lambda (i, x1, y1, x2, y2): (x2 - x1) * (y2 - y1))

        # print '%r' % borders

        if len(borders):
            border_contour = contours[borders[0][0]]
            edges = remove_border(border_contour, edges)

        edges = 255 * (edges > 0).astype(np.uint8)

        # Remove ~1px borders using a rank filter.
        maxed_rows = rank_filter(edges, -4, size=(1, 20))
        maxed_cols = rank_filter(edges, -4, size=(20, 1))
        debordered = np.minimum(np.minimum(edges, maxed_rows), maxed_cols)
        edges = debordered

        # Perform increasingly aggressive dilation until there are just a few
        # connected components.
        count = 21
        dilation = 5
        n = 1
        while count > 16:
            n += 1
            dilated_image = dilate(edges, N=3, iterations=n)

            contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            count = len(contours)

        #print dilation
        #Image.fromarray(edges).show()
        #Image.fromarray(255 * dilated_image).show()

        c_info = props_for_contours(contours, edges)
        c_info.sort(key=lambda x: -x['sum'])
        total = np.sum(edges) / 255
        area = edges.shape[0] * edges.shape[1]

        crop = None
        covered_sum = 0
        # while len(c_info) and 1.0 * c_info[0]['sum'] / total > 0.1:
        c = c_info[0]
        del c_info[0]
        this_crop = c['x1'], c['y1'], c['x2'], c['y2']
        crop = this_crop
        covered_sum = c['sum']

        while covered_sum < total:
            changed = False
            recall = 1.0 * covered_sum / total
            prec = 1 - 1.0 * crop_area(crop) / area
            f1 = 2 * (prec * recall / (prec + recall))
            #print '----'
            for i, c in enumerate(c_info):
                this_crop = c['x1'], c['y1'], c['x2'], c['y2']
                new_crop = union_crops(crop, this_crop)
                new_sum = covered_sum + c['sum']
                new_recall = 1.0 * new_sum / total
                new_prec = 1 - 1.0 * crop_area(new_crop) / area
                new_f1 = 2 * new_prec * new_recall / (new_prec + new_recall)

                # Add this crop if it improves f1 score,
                # _or_ it adds 25% of the remaining pixels for <15% crop expansion.
                # ^^^ very ad-hoc! make this smoother
                remaining_frac = c['sum'] / (total - covered_sum)
                new_area_frac = 1.0 * crop_area(new_crop) / crop_area(crop) - 1
                if new_f1 > f1 or (
                        remaining_frac > 0.25 and new_area_frac < 0.15):
                    print '%d %s -> %s / %s (%s), %s -> %s / %s (%s), %s -> %s' % (
                            i, covered_sum, new_sum, total, remaining_frac,
                            crop_area(crop), crop_area(new_crop), area, new_area_frac,
                            f1, new_f1)
                    crop = new_crop
                    covered_sum = new_sum
                    del c_info[i]
                    changed = True
                    break
                #else:
                #    print '%d %s -> %s / %s, %s -> %s / %s' % (
                #            i, covered_sum, new_sum, total,
                #            crop_area(crop), crop_area(new_crop), area)

            if not changed:
                break

        #draw = ImageDraw.Draw(im)
        #draw.rectangle(crop, outline='red')
        #draw.text((50, 50), path, fill='red')
        #im.show()
        out_path = path.replace('.jpg', '.crop.png')
        text_im = im.crop(crop)
        text_im.save(out_path)
        print '%s -> %s' % (path, out_path)
