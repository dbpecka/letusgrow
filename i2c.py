import time
from atlas_i2c import atlas_i2c

dev = atlas_i2c.AtlasI2C()
dev.set_i2c_address(0x63)

dev.write("R")
time.sleep(1.5)
r = dev.read("R")
print(dir(r))
time.sleep(1.5)

result = dev.query("I", processing_delay=1500)
print(result)
result.status_code
result.data
result.original_cmd

>>> import time
>>> from atlas_i2c import atlas_i2c
>>> dev = atlas_i2c.AtlasI2C()
>>> dev.set_i2c_address(0x63)
>>> dev.write("R")
>>> r = dev.read("R")
>>> dir(r)
['__annotations__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'data', 'original_cmd', 'sensor_address', 'status_code']
>>> r.data
b'3.731'


