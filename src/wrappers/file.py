from __future__ import annotations

import io
import os
from typing import Union, Optional

__all__ = ('File',)


class File:

    __slots__ = ('filename', 'fp')

    def __init__(
        self,
        fp: Union[str, bytes, io.IOBase],
        filename: Optional[str] = None,
    ):
        if isinstance(fp, bytes):
            self.fp = io.BytesIO(fp)
        elif isinstance(fp, io.IOBase):
            if not fp.readable():
                raise ValueError('The file must be readable.')
            self.fp = fp
        else:
            self.fp = open(fp, 'rb')

        if filename is None:
            if isinstance(fp, str):
                filename = os.path.split(fp)[1]
            else:
                filename = getattr(fp, 'name', 'unknow')

        self.filename = filename