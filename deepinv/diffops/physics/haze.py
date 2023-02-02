import torch
from deepinv.diffops.physics.forward import Forward


class Haze(Forward):
    def __init__(self, beta=0.1):
        super().__init__()
        self.beta = beta

    def A(self, x):
        im = x[0]
        d = x[1]
        A = x[2]

        t = torch.exp(-self.beta*d)
        y = t*im + (1-t)*A
        return y

    def A_adjoint(self, y):
        b,c,h,w = y.shape
        d = torch.ones((b, 1, h, w),device=y.device)
        A = 1.
        return y, d, A