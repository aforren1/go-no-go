import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# a = np.array([[1, 2, 3], [4, 5, 6]])
# print(a.shape)
# json_dump = json.dumps({'a': a, 'aa': [2, (2, 3, 4), a], 'bb': [2], 'cc': np.float32(5)}, cls=NumpyEncoder)
# print(json_dump)

