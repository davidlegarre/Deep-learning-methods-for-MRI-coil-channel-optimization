import numpy as np
import sys
from numpy import linalg as LA, vectorize
import matplotlib.pyplot as plt
from methods.complex import *
from methods.matrix_manipulation import *
from methods.image_manipulation import *


def combine_coils(channels):
    # Start by combining images by the root sum of squares

    reconstructed_image = np.zeros(channels.shape[1:])
    for i in range(channels.shape[0]):
        reconstructed_image = (np.square(channels[i, :, :])
                                      + (reconstructed_image))

    return np.sqrt(reconstructed_image)

def ROVir_im(coils, regions, lowf=5):
    f = np.vectorize(convert_void_toC)

    A_W, A_H, B1_W, B1_H, B2_W = regions

    ncoils, x, width, height = coils.shape

    print("Converting to complex...")
    coils = f(coils)
    print("\nFinished converting")

    print(coils.shape)
    fig, ax = plt.subplots()
    coils_ = combine_coils(coils.real[0,...])
    coils_ = np.flip(coils_, 0)
    ax.imshow(coils_.T)

    A = np.zeros(coils.shape).astype(np.csingle)
    B = np.zeros(coils.shape).astype(np.csingle)

    A[:, :, A_H, A_W] = coils[:, :, A_H, A_W]
    B[:, :, B1_H, B1_W] = coils[:, :, B1_H, B1_W]
    B[:, :, B1_H, B2_W] = coils[:, :, B1_H, B2_W]

    A = A.sum(axis=1)
    B = B.sum(axis=1)

    # Convert regions to vectors for ease of calculation
    #A = matrix_to_vec(A)
    #B = matrix_to_vec(B)

    # Generate the regions according to ROVir method
    print("Generating matrices...")
    A = generate_matrix_im(A)
    B = generate_matrix_im(B)

    comb = LA.pinv(B)*A
    topNv, eigVal, weights = calculate_eig(comb, lowf)

    weights = expand_weights(weights, (ncoils, ncoils))

    return weights, topNv
    # return coils
