from math import sqrt


class MagwickFilter:

    gyroMeasError = 3.14159265358979 * (5.0 / 180.0)
    beta = sqrt(3.0 / 4.0) * gyroMeasError
    eps = 10**-7

    def __init__(self, deltat):
        self.SEq_1, self.SEq_2, self.SEq_3, self.SEq_4 = 1.0, 0.0, 0.0, 0.0
        self.deltat = deltat

    def filter_update(self, w_x, w_y, w_z, a_x, a_y, a_z):
        halfSEq_1, halfSEq_2, halfSEq_3, halfSEq_4 = self.SEq_1 / 2, self.SEq_2 / 2, self.SEq_3 / 2, self.SEq_4 / 2
        twoSEq_1, twoSEq_2, twoSEq_3, = 2 * self.SEq_1, 2 * self.SEq_2, 2 * self.SEq_3

        norm = sqrt(a_x ** 2 + a_y ** 2 + a_z ** 2 + self.eps**2)
        a_x /= norm
        a_y /= norm
        a_z /= norm

        f_1 = twoSEq_2 * self.SEq_4 - twoSEq_1 * self.SEq_3 - a_x
        f_2 = twoSEq_1 * self.SEq_2 + twoSEq_3 * self.SEq_4 - a_y
        f_3 = 1.0 - twoSEq_2 * self.SEq_2 - twoSEq_3 * self.SEq_3 - a_z
        J_11or24 = twoSEq_3
        J_12or23 = 2.0 * self.SEq_4
        J_13or22 = twoSEq_1
        J_14or21 = twoSEq_2
        J_32 = 2.0 * J_14or21
        J_33 = 2.0 * J_11or24

        SEqHatDot_1 = J_14or21 * f_2 - J_11or24 * f_1
        SEqHatDot_2 = J_12or23 * f_1 + J_13or22 * f_2 - J_32 * f_3
        SEqHatDot_3 = J_12or23 * f_2 - J_33 * f_3 - J_13or22 * f_1
        SEqHatDot_4 = J_14or21 * f_1 + J_11or24 * f_2

        norm = sqrt(SEqHatDot_1 ** 2 + SEqHatDot_2 ** 2 + SEqHatDot_3 ** 2 + SEqHatDot_4 ** 2 + self.eps**2)
        SEqHatDot_1 /= norm
        SEqHatDot_2 /= norm
        SEqHatDot_3 /= norm
        SEqHatDot_4 /= norm

        SEqDot_omega_1 = -halfSEq_2 * w_x - halfSEq_3 * w_y - halfSEq_4 * w_z
        SEqDot_omega_2 = halfSEq_1 * w_x + halfSEq_3 * w_z - halfSEq_4 * w_y
        SEqDot_omega_3 = halfSEq_1 * w_y - halfSEq_2 * w_z + halfSEq_4 * w_x
        SEqDot_omega_4 = halfSEq_1 * w_z + halfSEq_2 * w_y - halfSEq_3 * w_x

        self.SEq_1 += (SEqDot_omega_1 - (self.beta * SEqHatDot_1)) * self.deltat
        self.SEq_2 += (SEqDot_omega_2 - (self.beta * SEqHatDot_2)) * self.deltat
        self.SEq_3 += (SEqDot_omega_3 - (self.beta * SEqHatDot_3)) * self.deltat
        self.SEq_4 += (SEqDot_omega_4 - (self.beta * SEqHatDot_4)) * self.deltat

        norm = sqrt(self.SEq_1**2 + self.SEq_2**2 + self.SEq_3**2 + self.SEq_4**2)
        self.SEq_1 /= norm
        self.SEq_2 /= norm
        self.SEq_3 /= norm
        self.SEq_4 /= norm
