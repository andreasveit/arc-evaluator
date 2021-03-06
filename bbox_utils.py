#!/usr/bin/env python

def plot_bounding_box(filename, bbox_list, colorvector):
    """
    Input
        filename of image as string
        bbox_list as list of BoundingBox objects
        colovector as 3x1 np.array defining the color channels normalized to [0-1]

    Output
        image as np.array of shape (height, width, channels)
    """

    import skimage
    from skimage import io
    # mwilber note: moving the imports here, since skimage is a bit
    # harder to install for students

    line_width = 4
    #load image file
    image = skimage.img_as_float(io.imread(filename))
    for bbox in bbox_list:
        top = bbox.top
        left = bbox.left
        width = bbox.width
        height = bbox.height
        image[top:top+height, left-line_width/2:left+line_width/2, :] = colorvector
        image[top:top+height, left+width-line_width/2:left+width+line_width/2, :] = colorvector
        image[top-line_width/2:top+line_width/2, left:left+width, :] = colorvector
        image[top+height-line_width/2:top+height+line_width/2, left:left+width, :] = colorvector
    return image


class BoundingBox(object):
    def __init__(self, top, left, height, width, confidence = None):
        self.top = top
        self.left = left
        self.height = height
        self.width = width
        self.confidence = confidence

    def __repr__(self):
        return "<Box: %s,%s + %sx%s>"%(self.left, self.top, self.width, self.height)

    @property
    def area(self):
        """ In pixels """
        return self.height * self.width

    def intersect(self, other):
        """Return a new bounding box that contains the intersection of
        'self' and 'other', or None if there is no intersection
        """
        new_top = max(self.top, other.top)
        new_left = max(self.left, other.left)
        new_right = min(self.left+self.width, other.left+other.width)
        new_bottom = min(self.top+self.height, other.top+other.height)
        if new_top < new_bottom and new_left < new_right:
            return BoundingBox(top = new_top,
                               left = new_left,
                               width = new_right - new_left,
                               height = new_bottom - new_top,
                               )
        return None

    def iou_score(self, other):
        """Returns the Intersection-over-Union score, defined as the area of
        the intersection divided by the intersection over the union of
        the two bounding boxes. This measure is symmetric.
        """
        if self.intersect(other):
            intersection_area = self.intersect(other).area
        else:
            intersection_area = 0
        union_area = self.area + other.area - intersection_area
        if union_area > 0:
            return float(intersection_area) / float(union_area)
        else:
            return 0

    def ellipse_score(self, other, allowed_ellipse_size = 0.25):
        """
        Return 'True' if the center of 'other' is within a
        certain ellipse.
        """
        self_center_x = float(self.left + 0.5*self.width)
        self_center_y = float(self.top + 0.5*self.height)
        other_center_x = float(other.left + 0.5*other.width)
        other_center_y = float(other.top + 0.5*other.height)

        allow_width = float(allowed_ellipse_size * self.width)
        allow_height = float(allowed_ellipse_size * self.height)

        return (
            (self_center_x - other_center_x)**2 / (allow_width**2)
            +
            (self_center_y - other_center_y)**2 / (allow_height**2)
            )

    def ellipse_matches(self, other, allowed_ellipse_size=0.25):
        return self.ellipse_score(other, allowed_ellipse_size) <= 1.0
