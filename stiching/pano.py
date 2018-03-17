import numpy as np
import cv2
import sys
from matchers import matchers
import time


class Stitch:

    def __init__(self, args):
        self.path = args
        fp = open(self.path, 'r')
        filenames = [each.rstrip('\r\n') for each in fp.readlines()]
        # print(filenames)
        # self.images = [cv2.imread(each) for each in filenames]
        self.images = [cv2.resize(cv2.imread(each), (480, 320))
                       for each in filenames]
        self.count = len(self.images)
        self.left_list, self.right_list, self.center_im = [], [], None
        self.matcher_obj = matchers()
        self.prepare_lists()

    def prepare_lists(self):
        # print("Number of images : %d" % self.count)
        self.centerIdx = self.count / 2
        # print("Center index image : %d" % self.centerIdx)
        self.center_im = self.images[int(self.centerIdx)]
        for i in range(self.count):
            if(i <= self.centerIdx):
                self.left_list.append(self.images[i])
            else:
                self.right_list.append(self.images[i])
        # print("Image lists prepared")

    def leftshift(self):
        # self.left_list = reversed(self.left_list)
        a = self.left_list[0]
        for b in self.left_list[1:]:
            H = self.matcher_obj.match(a, b, 'left')
            # print("Homography is : {}".format(H))
            xh = np.linalg.inv(H)
            # print("Inverse Homography : {}".format(xh))
            ds = np.dot(xh, np.array([a.shape[1], a.shape[0], 1]))
            ds = ds / ds[-1]
            # print("final ds=>{}".format(ds))
            f1 = np.dot(xh, np.array([0, 0, 1]))
            f1 = f1 / f1[-1]
            xh[0][-1] += abs(f1[0])
            xh[1][-1] += abs(f1[1])
            ds = np.dot(xh, np.array([a.shape[1], a.shape[0], 1]))
            offsety = abs(int(f1[1]))
            offsetx = abs(int(f1[0]))
            dsize = (int(ds[0]) + offsetx, int(ds[1]) + offsety)
            # print("image dsize => {}".format(dsize))

            tmp = cv2.warpPerspective(a, xh, dsize)
            # cv2.imshow("warped", tmp)
            # cv2.waitKey()
            # print(b.shape)
            # print(tmp.shape)
            if tmp.shape < b.shape:
                tmp = cv2.resize(tmp,
                                 (b.shape[1] + offsetx,
                                  b.shape[0] + offsety))
                # print(tmp.shape)
            # print(offsety)
            # print(offsetx)
            tmp[offsety:b.shape[0] + offsety,
                offsetx:b.shape[1] + abs(offsetx)] = b
            a = tmp

        self.leftImage = tmp

    def rightshift(self):
        for each in self.right_list:
            H = self.matcher_obj.match(self.leftImage, each, 'right')
            # print("Homography : {}".format(H))
            txyz = np.dot(H, np.array([each.shape[1], each.shape[0], 1]))
            txyz = txyz / txyz[-1]
            dsize = (int(txyz[0]) + self.leftImage.shape[1],
                     int(txyz[1]) + self.leftImage.shape[0])
            tmp = cv2.warpPerspective(each, H, dsize)
            # cv2.imshow("tp", tmp)
            # cv2.waitKey()
            # tmp[:self.leftImage.shape[0], :self.leftImage.shape[1]] =
            # self.leftImage
            tmp = self.mix_and_match(self.leftImage, tmp)
            # print("tmp shape {}".format(tmp.shape))
            # print("self.leftimage shape= {}".format(self.leftImage.shape))
            self.leftImage = tmp
        # self.showImage('left')

    def mix_and_match(self, leftImage, warpedImage):
        i1y, i1x = leftImage.shape[:2]
        i2y, i2x = warpedImage.shape[:2]
        # print(leftImage[-1, -1])

        t = time.time()
        black_l = np.where(leftImage == np.array([0, 0, 0]))
        black_wi = np.where(warpedImage == np.array([0, 0, 0]))
        # print(time.time() - t)
        # print(black_l[-1])

        for i in range(0, i1x):
            for j in range(0, i1y):
                try:
                    if(np.array_equal(leftImage[j, i], np.array([0, 0, 0])) and np.array_equal(warpedImage[j, i], np.array([0, 0, 0]))):
                        # print( "BLACK")
                        # instead of just putting it with black,
                        # take average of all nearby values and avg it.
                        warpedImage[j, i] = [0, 0, 0]
                    else:
                        if(np.array_equal(warpedImage[j, i], [0, 0, 0])):
                            # print( "PIXEL")
                            warpedImage[j, i] = leftImage[j, i]
                        else:
                            if not np.array_equal(leftImage[j, i], [0, 0, 0]):
                                bw, gw, rw = warpedImage[j, i]
                                bl, gl, rl = leftImage[j, i]
                                # b = (bl+bw)/2
                                # g = (gl+gw)/2
                                # r = (rl+rw)/2
                                warpedImage[j, i] = [bl, gl, rl]
                except:
                    pass
        # cv2.imshow("waRPED mix", warpedImage)
        # cv2.waitKey()
        return warpedImage

    def trim_left(self):
        pass

    def showImage(self, string=None):
        if string == 'left':
            cv2.imshow("left image", self.leftImage)
            cv2.imshow("left image", cv2.resize(self.leftImage, (400, 400)))
        elif string == "right":
            cv2.imshow("right Image", self.rightImage)
        cv2.waitKey()


def start_stiching(files_path, folder_path):
    # try:
    #     args = sys.argv[1]
    # except:
    #     args = "txtlists/files1.txt"
    # finally:
        # print("Parameters : {}".format(args))
    print("Parameters : {}".format(files_path))

    s = Stitch(files_path)
    s.leftshift()
    # s.showImage('left')
    s.rightshift()
    # print("done")

    # cv2.imwrite(folder_path, s.leftImage)
    save_cropped_image(s.leftImage, folder_path)
    # save_image_resized(s.leftImage, folder_path, width=720,
    #                    height=480, inter=cv2.INTER_AREA)
    # print("image written")
    cv2.destroyAllWindows()


def save_cropped_image(image, path):
    path = path.replace('panoramic', 'cropped_panoramic')
    imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    mask = imgray > 0

    # Busca coordenadas da mascara
    coords = np.argwhere(mask)

    # Bounding box of non-black pixels.
    x0, y0 = coords.min(axis=0)
    x1, y1 = coords.max(axis=0) + 1   # slices are exclusive at the top

    # Get the contents of the bounding box.
    cropped = image[x0:x1, y0:y1]

    cv2.imwrite(path, cropped)


def save_image_resized(image, path, width=None, height=None, inter=cv2.INTER_AREA):
    path = path.replace('panoramic', 'resized_panoramic')
    # Inicializa dimensoes de imagem e busca parâmetros de altura
    # e largura de imagem dada
    # dim = None
    # (h, w) = image.shape[:2]

    # # Se novas dimensoes nao foram especificadas,
    # #  retorna imagem original
    # if width is None and height is None:
    #     return image
    # # Checar se largura nao foi especifida
    # if width is None:
    #     # Calcula raio da altura, e controi dim
    #     r = height / float(h)
    #     dim = (int(w * r), height)
    # # Senao, altura nao foi especificada
    # else:
    #     # Calcula raio da altura e controi dim
    #     r = width / float(w)
    #     dim = (width, int(h * r))
    dim = (width, height)

    resized = cv2.resize(image, dim, interpolation=inter)
    save_cropped_image(resized, path)
    # cv2.imwrite(path, resized)
