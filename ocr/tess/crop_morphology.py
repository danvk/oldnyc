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


def dilate(ary, N): 
    """Dilate using an NxN '+' sign shape. ary is np.uint8."""
    kernel = np.zeros((N,N), dtype=np.uint8)
    kernel[(N-1)/2,:] = 1
    dilated_image = cv2.dilate(ary / 255, kernel, iterations=2)

    kernel = np.zeros((N,N), dtype=np.uint8)
    kernel[:,(N-1)/2] = 1
    dilated_image = cv2.dilate(dilated_image, kernel, iterations=2)
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


if __name__ == '__main__':
    for path in sys.argv[1:]:
        im = Image.open(path)
        edges = cv2.Canny(np.asarray(im), 100, 200)

        # Remove ~1px borders using a rank filter.
        maxed_rows = rank_filter(edges, -4, size=(1, 20))
        maxed_cols = rank_filter(edges, -4, size=(20, 1))
        edges = np.minimum(np.minimum(edges, maxed_rows), maxed_cols)

        # Perform increasingly aggressive dilation until there are just a few
        # connected components.
        count = 21
        dilation = 9
        while count > 16:
            dilation += 2
            dilated_image = dilate(edges, dilation)

            contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            count = len(contours)

        # Image.fromarray(edges).show()
        # Image.fromarray(255 * dilated_image).show()

        c_info = props_for_contours(contours, edges)
        c_info.sort(key=lambda x: -x['sum'])
        total = np.sum(edges) / 255
        area = edges.shape[0] * edges.shape[1]

        crop = None
        covered_sum = None
        while len(c_info) and 1.0 * c_info[0]['sum'] / total > 0.1:
            c = c_info[0]
            del c_info[0]
            this_crop = c['x1'], c['y1'], c['x2'], c['y2']
            if crop is None:
                crop = this_crop
                covered_sum = c['sum']
            else:
                crop = union_crops(crop, this_crop)
                covered_sum += c['sum']

        while True:
            changed = False
            recall = 1.0 * covered_sum / total
            prec = 1 - 1.0 * crop_area(crop) / area
            f1 = 2 * (prec * recall / (prec + recall))
            for i, c in enumerate(c_info):
                this_crop = c['x1'], c['y1'], c['x2'], c['y2']
                new_crop = union_crops(crop, this_crop)
                new_sum = covered_sum + c['sum']
                new_recall = 1.0 * new_sum / total
                new_prec = 1 - 1.0 * crop_area(new_crop) / area
                new_f1 = 2 * new_prec * new_recall / (new_prec + new_recall)
                if new_f1 > f1:
                    crop = new_crop
                    covered_sum = new_sum
                    del c_info[i]
                    changed = True
                    break

            if not changed:
                break

        draw = ImageDraw.Draw(im)
        draw.rectangle(crop, outline='red')
        im.show()
