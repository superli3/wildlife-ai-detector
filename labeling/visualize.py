import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.colors as mcolors
import argparse


def visualize_bbox(img_file, yolo_ann_file, label_dict, figure_size=(6, 8)):
    """
    Plots bounding boxes on images

    Input:
    img_file : numpy.array
    yolo_ann_file: Text file containing annotations in YOLO format
    label_dict: Dictionary of image categories
    figure_size: Figure size
    """

    img = mpimg.imread(img_file)
    fig, ax = plt.subplots(1, 1, figsize=figure_size)
    ax.imshow(img)

    im_height, im_width, _ = img.shape

    palette = mcolors.TABLEAU_COLORS
    colors = [c for c in palette.keys()]
    with open(yolo_ann_file, "r") as fin:
        for line in fin:
            cat, center_w, center_h, width, height = line.split()
            cat = int(cat)
            category_name = label_dict[cat]
            left = (float(center_w) - float(width) / 2) * im_width
            top = (float(center_h) - float(height) / 2) * im_height
            width = float(width) * im_width
            height = float(height) * im_height

            rect = plt.Rectangle(
                (left, top),
                width,
                height,
                fill=False,
                linewidth=2,
                edgecolor=colors[cat],
            )
            ax.add_patch(rect)
            props = dict(boxstyle="round", facecolor=colors[cat], alpha=0.5)
            ax.text(
                left,
                top,
                category_name,
                fontsize=14,
                verticalalignment="top",
                bbox=props,
            ) 
    plt.show()


def main():
    """
    Plots bounding boxes
    """

    labels = {0: "pencil", 1: "pen"}
    parser = argparse.ArgumentParser()
    parser.add_argument("img", help="image file")
    args = parser.parse_args()
    img_file = args.img
    ann_file = img_file.split(".")[0] + ".txt"
    visualize_bbox(img_file, ann_file, labels, figure_size=(6, 8))


if __name__ == "__main__":
    main()

