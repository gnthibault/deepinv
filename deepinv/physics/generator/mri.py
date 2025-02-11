import numpy as np
import torch
from deepinv.physics.generator import PhysicsGenerator


class AccelerationMaskGenerator(PhysicsGenerator):
    r"""
    Generator for MRI cartesian acceleration masks.

    It generates a mask of vertical lines for MRI acceleration using fixed sampling in the low frequencies (center of k-space),
    and random uniform sampling in the high frequencies.

    :param tuple img_size: image size of shape (C, H, W) or (H, W)
    :param int acceleration: acceleration factor.
    :param str device: cpu or gpu.

    |sep|

    :Examples:

    >>> from deepinv.physics.generator import AccelerationMaskGenerator
    >>> import deepinv
    >>> mask_generator = AccelerationMaskGenerator((16, 16))
    >>> mask_dict = mask_generator.step() # dict_keys(['mask'])
    >>> deepinv.utils.plot(mask_dict['mask'].squeeze(1))
    >>> print(mask_dict['mask'].shape)
    torch.Size([1, 2, 16, 16])

    """

    def __init__(self, img_size: tuple, acceleration=4, device: str = "cpu"):
        super().__init__(shape=img_size, device=device)
        self.device = device
        self.img_size = img_size
        self.acceleration = acceleration

    def step(self, batch_size=1):
        r"""
        Create a mask of vertical lines.

        :param int batch_size: batch_size.
        :return: dictionary with key **'mask'**: tensor of size (batch_size, C, H, W) with values in {0, 1}.
        :rtype: dict
        """

        if len(self.img_size) == 2:
            H, W = self.img_size
            C = 2
        elif len(self.img_size) == 3:
            C, H, W = self.img_size
        else:
            raise ValueError("img_size must be (C, H, W) or (H, W)")

        acceleration_factor = self.acceleration

        if acceleration_factor == 4:
            central_lines_percent = 0.08
            num_lines_center = int(central_lines_percent * W)
            side_lines_percent = 0.25 - central_lines_percent
            num_lines_side = int(side_lines_percent * W)
        if acceleration_factor == 8:
            central_lines_percent = 0.04
            num_lines_center = int(central_lines_percent * W)
            side_lines_percent = 0.125 - central_lines_percent
            num_lines_side = int(side_lines_percent * W)

        mask = torch.zeros((batch_size, H, W), **self.factory_kwargs)

        center_line_indices = torch.linspace(
            H // 2 - num_lines_center // 2,
            H // 2 + num_lines_center // 2 + 1,
            steps=50,
            dtype=torch.long,
        )
        mask[:, :, center_line_indices] = 1

        for i in range(batch_size):
            random_line_indices = np.random.choice(
                H, size=(num_lines_side // 2,), replace=False
            )
            mask[i, :, random_line_indices] = 1

        return {"mask": torch.cat([mask.float().unsqueeze(1)] * C, dim=1)}
