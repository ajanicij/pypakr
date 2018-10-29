import pytest
import pypakr
import os
import shutil

def test_basic(tmpdir):
  tmp = str(tmpdir)
  base = os.path.join(tmp, 'BASE')
  src = os.path.join(os.path.dirname(__file__), 'SRC.tar')
  image = os.path.join(tmp, 'IMAGE.tar')
  container = os.path.join(tmp, 'CONT')
  pypakr.init(base)
  pypakr.create_image(base, src, image)
  pypakr.create_container(base, image, container)
  pypakr.run(container, os.path.join('.', 'run'))
  assert os.path.isfile(os.path.join(container, 'myfile'))
  # Clean up: delete IMAGE.tar, CONT
  shutil.rmtree(container)
  os.remove(image)
