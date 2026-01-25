from __future__ import annotations

import io
import os
import logging
from typing import Union, Optional

__all__ = ('File',)

log = logging.getLogger(__name__)

class File:

    __slots__ = ('filename', 'fp')

    def __init__(
        self,
        fp: Union[str, bytes, io.IOBase],
        filename: Optional[str] = None,
    ):
        if isinstance(fp, bytes):
            self.fp = io.BytesIO(fp)
            log.debug('Arquivo carregado de bytes filename=%s', filename or 'unknow')
        elif isinstance(fp, io.IOBase):
            if not fp.readable():
                raise ValueError('The file must be readable.')
            self.fp = fp
            log.debug('Arquivo carregado de IOBase filename=%s', filename or getattr(fp, 'name', 'unknow'))
        else:
            self.fp = open(fp, 'rb')
            log.debug('Arquivo aberto do disco path=%s', fp)

        if filename is None:
            if isinstance(fp, str):
                filename = os.path.split(fp)[1]
            else:
                filename = getattr(fp, 'name', 'unknow')

        self.filename = filename
