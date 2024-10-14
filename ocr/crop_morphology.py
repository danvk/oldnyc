#!/usr/bin/env python
"""Crop an image to just the portions containing text.

Usage:

    ./ocr/crop_morphology.py path/to/image.jpg

This will place the cropped image in path/to/image.crop.png.

For details on the methodology, see
http://www.danvk.org/2015/01/07/finding-blocks-of-text-in-an-image-using-python-opencv-and-numpy.html
"""

import argparse
import glob
import os
import sys

import cv2
from PIL import Image, ImageDraw
import numpy as np
from scipy.ndimage.filters import rank_filter


def dilate(ary, N, iterations):
    """Dilate using an NxN '+' sign shape. ary is np.uint8."""
    kernel = np.zeros((N, N), dtype=np.uint8)
    kernel[(N - 1) // 2, :] = 1
    dilated_image = cv2.dilate(ary // 255, kernel, iterations=iterations)

    kernel = np.zeros((N, N), dtype=np.uint8)
    kernel[:, (N - 1) // 2] = 1
    dilated_image = cv2.dilate(dilated_image, kernel, iterations=iterations)
    return dilated_image


def props_for_contours(contours, ary):
    """Calculate bounding box & the number of set pixels for each contour."""
    c_info = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        c_im = np.zeros(ary.shape)
        cv2.drawContours(c_im, [c], 0, 255, -1)
        c_info.append(
            {
                "x1": x,
                "y1": y,
                "x2": x + w - 1,
                "y2": y + h - 1,
                "sum": np.sum(ary * (c_im > 0)) / 255,
            }
        )
    return c_info


def union_crops(crop1, crop2):
    """Union two (x1, y1, x2, y2) rects."""
    x11, y11, x21, y21 = crop1
    x12, y12, x22, y22 = crop2
    return min(x11, x12), min(y11, y12), max(x21, x22), max(y21, y22)


def intersect_crops(crop1, crop2):
    x11, y11, x21, y21 = crop1
    x12, y12, x22, y22 = crop2
    return max(x11, x12), max(y11, y12), min(x21, x22), min(y21, y22)


def crop_area(crop):
    x1, y1, x2, y2 = crop
    return max(0, x2 - x1) * max(0, y2 - y1)


def find_border_components(contours, ary):
    borders = []
    area = ary.shape[0] * ary.shape[1]
    print(f"contours: {len(contours)}")
    # debug = np.zeros(ary.shape, dtype=np.uint8)
    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        rot_rect = cv2.minAreaRect(c)
        ((rx, ry), (rw, rh), deg) = rot_rect
        if 5 < deg < 45 and rw * rh > 1000:
            print(f"{i}: {rx:.0f},{ry:.0f} {rw:.0f}x{rh:.0f} +{deg}°")
            # box = cv2.boxPoints(rot_rect)
            # box = np.int0(box)
            # cv2.drawContours(debug, [box], 0, 255, 2)
        if w * h > 0.5 * area and angle_from_right(deg) < 5:
            print(f"{i}: {x},{y}+{w}x{h}: {w*h/area}")
            borders.append((i, x, y, x + w - 1, y + h - 1))
            # debug = np.zeros(ary.shape)
            # cv2.drawContours(debug, [c], 0, 255, 4)
            # Image.fromarray(debug).show()
    # Image.fromarray(debug).show()
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
    # print(r)
    if angle_from_right(degs) <= 10.0:
        box = cv2.boxPoints(r)
        box = np.int0(box)
        cv2.drawContours(c_im, [box], 0, 255, -1)
        cv2.drawContours(c_im, [box], 0, 0, 4)
        # print(f'Removing border: {box}')
    else:
        x1, y1, x2, y2 = cv2.boundingRect(contour)
        cv2.rectangle(c_im, (x1, y1), (x2, y2), 255, -1)
        cv2.rectangle(c_im, (x1, y1), (x2, y2), 0, 4)
        # print(f'Removing border bbox: {x1},{y1} - {x2},{y2}')
        # print(contour)

    return np.minimum(c_im, ary)


def find_components(edges, max_components=16):
    """Dilate the image until there are just a few connected components.

    Returns contours for these components."""
    # Perform increasingly aggressive dilation until there are just a few
    # connected components.
    count = 21
    # dilation = 5
    n = 15
    while count > 16:
        n += 1
        dilated_image = dilate(edges, N=3, iterations=n)
        contours, _hierarchy = cv2.findContours(
            dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        count = len(contours)
    print(f"dilation iterations: {n=}")
    # Image.fromarray(edges).show()
    # Image.fromarray(255 * dilated_image).show()
    return contours


def fscore(precision, recall, beta):
    b2 = beta**2
    return (1 + b2) * (precision * recall / (b2 * precision + recall))


def find_optimal_components_subset(contours, edges, beta):
    """Find a crop which strikes a good balance of coverage/compactness.

    Returns an (x1, y1, x2, y2) tuple.
    """
    c_info = props_for_contours(contours, edges)
    c_info.sort(key=lambda x: -x["sum"])
    total = np.sum(edges) / 255
    area = edges.shape[0] * edges.shape[1]

    c = c_info[0]
    del c_info[0]
    this_crop = c["x1"], c["y1"], c["x2"], c["y2"]
    crop = this_crop
    covered_sum = c["sum"]
    print(f"Initial crop: {this_crop}")

    xs = set()
    ys = set()
    for c in c_info:
        xs.add(c["x1"])
        xs.add(c["x2"])
        ys.add(c["y1"])
        ys.add(c["y2"])
    print(f"Unique xs: {len(xs)}, unique ys: {len(ys)}")

    while covered_sum < total:
        changed = False
        recall = 1.0 * covered_sum / total
        prec = 1 - 1.0 * crop_area(crop) / area
        f1 = fscore(prec, recall, beta)
        # print '----'
        for i, c in enumerate(c_info):
            this_crop = c["x1"], c["y1"], c["x2"], c["y2"]
            # if this_crop[1] > 1000:
            #     continue
            new_crop = union_crops(crop, this_crop)
            new_sum = covered_sum + c["sum"]
            new_recall = 1.0 * new_sum / total
            new_prec = 1 - 1.0 * crop_area(new_crop) / area
            new_f1 = fscore(new_prec, new_recall, beta)

            # Add this crop if it improves f1 score,
            # _or_ it adds 25% of the remaining pixels for <15% crop expansion.
            # ^^^ very ad-hoc! make this smoother
            remaining_frac = c["sum"] / (total - covered_sum)
            new_area_frac = 1.0 * crop_area(new_crop) / crop_area(crop) - 1
            if new_f1 > f1 or (remaining_frac > 0.25 and new_area_frac < 0.15):
                print(f"{i} Adding {this_crop}")
                print(
                    "%d %s -> %s / %s (%s), %s -> %s / %s (%s), %s -> %s"
                    % (
                        i,
                        covered_sum,
                        new_sum,
                        total,
                        remaining_frac,
                        crop_area(crop),
                        crop_area(new_crop),
                        area,
                        new_area_frac,
                        f1,
                        new_f1,
                    )
                )
                crop = new_crop
                covered_sum = new_sum
                del c_info[i]
                changed = True
                break

        if not changed:
            break

    return crop


def pad_crop(crop, contours, edges, border_contour, im_size):
    """Slightly expand the crop to get full contours.

    This will expand to include any contours it currently intersects, but will
    not expand past a border.
    """
    bx1, by1, bx2, by2 = 0, 0, *im_size
    if border_contour is not None and len(border_contour) > 0:
        c = props_for_contours([border_contour], edges)[0]
        bx1, by1, bx2, by2 = c["x1"] + 5, c["y1"] + 5, c["x2"] - 5, c["y2"] - 5

    def crop_in_border(crop):
        x1, y1, x2, y2 = crop
        x1 = max(x1, bx1)
        y1 = max(y1, by1)
        x2 = min(x2, bx2)
        y2 = min(y2, by2)
        return (x1, y1, x2, y2)

    crop = crop_in_border(crop)

    c_info = props_for_contours(contours, edges)
    changed = False
    for c in c_info:
        this_crop = c["x1"], c["y1"], c["x2"], c["y2"]
        this_area = crop_area(this_crop)
        int_area = crop_area(intersect_crops(crop, this_crop))
        new_crop = crop_in_border(union_crops(crop, this_crop))
        if 0 < int_area < this_area and crop != new_crop:
            print("%s -> %s" % (str(crop), str(new_crop)))
            changed = True
            crop = new_crop

    if changed:
        return pad_crop(crop, contours, edges, border_contour, im_size)
    else:
        return crop


def remove_stamp(edges: Image, path: str):
    """Look for a large contour that's a close match for a rotated rectangle.

    This is almost certainly a "New York Public Library" stamp, which does
    contain text and can throw off cropping for the rest of the image.
    """
    dilated_image = dilate(edges, N=3, iterations=5)
    contours, _hierarchy = cv2.findContours(
        dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    stamp_contours = []
    for c in contours:
        rot_rect = cv2.minAreaRect(c)
        ((rx, ry), (rw, rh), deg) = rot_rect
        # print(rw, rh)
        if 100 < rw < 300 and 100 < rh < 300:
            # Image.fromarray(edges).show()
            # dilated_image = dilate(edges, N=3, iterations=5)
            # Image.fromarray(255*dilated_image).show()
            bbox_area = rw * rh
            contour_area = cv2.contourArea(c)
            # print(f'   {contour_area=}, {bbox_area=}, {100*contour_area/bbox_area:.2f}%')
            if contour_area / bbox_area > 0.85:
                stamp_contours.append((c, rot_rect))
            # Image.fromarray(edges).show()
    if len(stamp_contours) == 1:
        c, rot_rect = stamp_contours[0]
        cv2.drawContours(edges, [c], 0, 0, cv2.FILLED)
        ((rx, ry), (rw, rh), deg) = rot_rect
        print(f"{path} Filled stamp: {rx:.0f},{ry:.0f} {rw:.0f}x{rh:.0f} +{deg}°")
        return c
    elif len(stamp_contours) > 1:
        print(f"{path} found multiple stamp candidates; ignoring them all.")
    return None


def downscale_image(im: Image.Image, max_dim=2048) -> tuple[float, Image.Image]:
    """Shrink im until its longest dimension is <= max_dim.

    Returns new_image, scale (where scale <= 1).
    """
    a, b = im.size
    if max(a, b) <= max_dim:
        return 1.0, im

    scale = 1.0 * max_dim / max(a, b)
    new_im = im.resize((int(a * scale), int(b * scale)), Image.Resampling.LANCZOS)
    return scale, new_im


def size(border):
    i, x1, y1, x2, y2 = border
    return (x2 - x1) * (y2 - y1)


def process_image(path, out_path, stroke=False, beta=1, border_only=False):
    print(f"Cropping {path}")
    orig_im = Image.open(path)
    print(orig_im.size)
    scale, im = downscale_image(orig_im)
    print(scale, im.size)

    edges = cv2.Canny(np.asarray(im), 100, 200)
    # Image.fromarray(edges).show()

    # TODO: dilate image _before_ finding a border. This is crazy sensitive!
    contours, _hierarchy = cv2.findContours(
        edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    borders = find_border_components(contours, edges)
    borders.sort(key=size)
    # print(f'{len(borders)=}')

    border_contours = [contours[border[0]] for border in borders]
    border_contour = None
    if len(borders):
        border_contour = contours[borders[0][0]]
        edges = remove_border(border_contour, edges)

    edges = 255 * (edges > 0).astype(np.uint8)
    # Image.fromarray(edges).show()

    stamp_contour = remove_stamp(edges, path)

    # Remove ~1px borders using a rank filter.
    maxed_rows = rank_filter(edges, -4, size=(1, 20))
    maxed_cols = rank_filter(edges, -4, size=(20, 1))
    debordered = np.minimum(np.minimum(edges, maxed_rows), maxed_cols)
    edges = debordered
    # Image.fromarray(edges).show()

    contours = find_components(edges)
    if len(contours) == 0:
        sys.stderr.write("%s: no text!\n" % path)
        return

    if not border_only:
        crop = find_optimal_components_subset(contours, edges, beta)
        crop = pad_crop(crop, contours, edges, border_contour, im.size)
    else:
        if border_contour is not None:
            c_info = props_for_contours([border_contour], edges)
            c = c_info[0]
            crop = c["x1"], c["y1"], c["x2"], c["y2"]
        else:
            crop = 0, 0, im.width, im.height

    if stroke:
        im = im.convert("RGB")
        draw = ImageDraw.Draw(im)
        c_info = props_for_contours(contours, edges)
        for c in c_info:
            this_crop = c["x1"], c["y1"], c["x2"], c["y2"]
            draw.rectangle(this_crop, outline="blue")
        draw.rectangle(crop, outline="red")
        if border_contour is not None:
            c_info = props_for_contours(border_contours, edges)
            for i, c in enumerate(c_info):
                this_crop = c["x1"], c["y1"], c["x2"], c["y2"]
                draw.rectangle(this_crop, outline="green", width=4 if i == 0 else 2)

        if stamp_contour is not None:
            draw.line(
                [(pt[0][0], pt[0][1]) for pt in stamp_contour], fill="hotpink", width=4
            )
        out_im = im
    else:
        crop = [int(x / scale) for x in crop]  # upscale to the original image size.
        out_im = orig_im.crop(crop)

    # draw.text((50, 50), path, fill='red')
    # orig_im.save(out_path)
    # im.show()
    out_im.save(out_path)
    print("%s -> %s" % (path, out_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crop images to just the text")
    parser.add_argument(
        "--beta",
        default=1.0,
        type=float,
        help="Relative weight of precision and recall for selecting a subset of boxes. "
        "Higher beta weights recall over precision, lower weights prec. over recall.",
    )
    parser.add_argument(
        "--ignore_errors",
        action="store_true",
        help="Log errors and continue instead of throwing.",
    )
    parser.add_argument(
        "--stroke",
        action="store_true",
        help="Draw a red box around the text instead of cropping.",
    )
    parser.add_argument(
        "--output_pattern",
        default="%s.crop.png",
        help="Output file pattern, relative to input file.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Write over existing output images instead of skipping them.",
    )
    parser.add_argument(
        "--border_only",
        action="store_true",
        help="Only remove the border, don't try to find the text.",
    )
    parser.add_argument(
        "files",
        type=str,
        nargs="+",
        help="Path to images to process, or a glob.",
    )

    args = parser.parse_args()

    files = []
    for file in args.files:
        if "*" in file:
            glob_files = glob.glob(file)
            # random.shuffle(glob_files)
            files += glob_files
        else:
            files.append(file)

    for path in files:
        path_dir, path_file = os.path.split(path)
        (path_base, _) = os.path.splitext(path_file)
        out_path = os.path.join(path_dir, args.output_pattern % path_base)
        if os.path.exists(out_path) and not args.overwrite:
            continue
        try:
            process_image(
                path,
                out_path,
                args.stroke,
                beta=args.beta,
                border_only=args.border_only,
            )
        except Exception as e:
            if args.ignore_errors:
                sys.stderr.write(f"Error on {path}: {e}\n")
            else:
                raise e
