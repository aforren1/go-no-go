# -----------------------------------------------------------------------------
# Copyright (c) 2009-2016 Nicolas P. Rougier. All rights reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
""" Font Manager """
import os
import numpy as np
from . atlas import Atlas
#from glumpy.gloo.atlas import Atlas
from . agg_font import AggFont


class FontManager(object):
    """
    Font Manager

    The Font manager takes care of caching already loaded font. Currently, the only
    way to get a font is to get it via its filename.
    """

    # Default atlas
    _atlas_agg = None

    # Font cache
    _cache_agg = {}

    # The singleton instance
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get(cls, filename, size=12):
        """
        Get a font from the cache, the local data directory or the distant server
        (in that order).
        """

        basename = os.path.basename(filename)

        key = '%s-%d' % (basename, size)
        if FontManager._atlas_agg is None:
            # interesting that agg atlas is RGB?
            FontManager._atlas_agg = np.zeros((1024, 1024, 3), np.ubyte).view(Atlas)

        atlas = FontManager._atlas_agg
        cache = FontManager._cache_agg
        if key not in cache.keys():
            # AggFont does the actual loading
            cache[key] = AggFont(filename, size, atlas)
        return cache[key]

    @property
    def atlas_agg(self):
        if FontManager._atlas_agg is None:
            FontManager._atlas_agg = np.zeros((1024, 1024, 3), np.ubyte).view(Atlas)
        return FontManager._atlas_agg
