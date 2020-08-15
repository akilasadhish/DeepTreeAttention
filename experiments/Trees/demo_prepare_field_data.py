
#Testing script that lives outside of pytest due to DeepForest dependency in a new conda env. PYTHONPATH manually added to root dir for relative paths.
import os
import pytest
import tensorflow

import prepare_field_data
from DeepTreeAttention.generators import boxes

data_dir = os.path.dirname(prepare_field_data.__file__)
data_path = "{}/test_data/sample.shp".format(data_dir)
rgb_pool = "{}/test_data/rgb/*.tif".format(data_dir)
hyperspec_pool = "{}/test_data/HSI/*.tif".format(data_dir)
hyperspectral_savedir = "{}/test_data/HSI/".format(data_dir)

height = 20
width = 20

created_records = prepare_field_data.main(
    field_data=data_path,
    hyperspectral_pool=hyperspec_pool,
    height=height,
    width=width,
    rgb_pool=rgb_pool,
    sensor="rgb",
    hyperspectral_savedir=hyperspectral_savedir,
    use_dask=False)

dataset = boxes.tf_dataset(created_records, batch_size=1)
iterator = dataset.make_one_shot_iterator()
next_element = iterator.get_next()

with tensorflow.Session() as sess:
    image, label = sess.run(next_element)
    assert image.shape == (1, height, width, 426)
    assert label.shape  == (1,1)
    