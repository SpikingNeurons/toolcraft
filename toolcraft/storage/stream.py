"""
Here we will implement things for streaming
check try_pyarrow_stream.py

import pyarrow as pa
import numpy as np
import pathlib

data = {
    "a": np.zeros(10),
    "b": pa.array([_ for _ in np.zeros((10, 4))])
}

_rb = pa.record_batch([pa.array(np.zeros(10))], ["a"])
_fp = pathlib.Path("xxx")
sw = pa.RecordBatchStreamWriter(_fp, _rb.schema)

for _ in [_rb, _rb]:
    sw.write(_)


sr = pa.RecordBatchStreamReader(_fp)

xx = sr.read_all()

print(xx.to_pandas())


RATIONALE:
  Unlike Table here streaming happens to on file
  We will not need functions like
    + pivot
    + scan
    + filter
  So we will start a new stream api on top of this
  But note that we can always get pa.Table from it ;)
"""
