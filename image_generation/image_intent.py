IMAGE_KEYWORDS = [

    "draw",
    "generate image",
    "create image",
    "make image",
    "paint",
    "illustrate",
    "picture",
    "artwork",
    "icon",
    "poster"
]


def is_image_request(query):

    q = query.lower()

    for word in IMAGE_KEYWORDS:

        if word in q:
            return True

    return False