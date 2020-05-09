import os


def massage_path(file_name_path):
    """
    function to massage file path and do some transformations
    for different scenarios of file inputs

    :param file_name_path:
    :return:
    """
    massaged_path = file_name_path
    # pprint(massaged_path)

    # convert possible windows style path to unix path
    massaged_path = massaged_path.replace('\\', '/')

    # expand home directory in path
    massaged_path = massaged_path.replace('~', os.path.expanduser('~'))
    # pprint(massaged_path)

    # expand possible current directory reference in path
    if massaged_path[0:2] == '.\\' or massaged_path[0:2] == './':
        massaged_path = os.path.abspath(massaged_path)

    return massaged_path


def extract_file_dict(filename, metadata):
    """
    Function to extract obj dict from metadata

    :param filename:
    :param metadata:
    :return:
    """
    # print(metadata)
    info = {
        "fileName": filename,
        # "creationDate":
        #   metadata['ResponseMetadata']['HTTPHeaders']['date'],
        "lastModificationDate":
            metadata['ResponseMetadata']['HTTPHeaders']['last-modified'],
        "contentLength":
            metadata['ResponseMetadata']['HTTPHeaders']['content-length']
    }

    return info
