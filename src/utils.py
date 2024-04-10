# sanitize all names! some contain apostrophes or other garbage data that
# MySQL really doesn't cope with well.

def sanitize(data: str) -> str:
    # apostrophes can be a catastrophe
    if '\'' in data:
        data = data.replace('\'', '')

    # remove any non-ascii characters. for some reason, the data has a lot of
    # odd symbols that can mangle MySQL
    data = ''.join(ch for ch in data if ord(ch) < 128).strip()
    if len(data) > 0 and data[-1] == ',':
        data = data[:-1]
    return data
