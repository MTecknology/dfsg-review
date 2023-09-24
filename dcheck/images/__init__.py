'''
DCheck Images
'''
# Python
import pathlib
import tkinter

# DCheck
import dcheck.core.config

# Keep cache of loaded PhotoImages
cached_photos = {}


def tk_photo(image, images_dir=None):
    '''
    Return a tkinter photo from <image>.png.
    '''
    # Return instance if one exists in cache
    if image in cached_photos:
        return cached_photos[image]

    if not images_dir:
        images_dir = dcheck.core.config.get('images_dir')

    # Add tkPhoto(image) to cache
    cached_photos[image] = tkinter.PhotoImage(
            file=pathlib.Path(images_dir) / f'{image}.png')

    # Return cached photo
    return cached_photos[image]
