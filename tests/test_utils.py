import os
import uuid
import src.utils as utils


def test_temp_data_handler():
    folder = "./tmp_data/"
    fileroot = str(uuid.uuid4())
    filename = fileroot + ".pdf"
    filepath = os.path.join(folder, filename)

    assert not os.path.exists(filepath)
    datahandler = utils.temp_data_handler(tmp_folder_name=folder, fileroot=fileroot)
    assert not os.path.exists(filepath)

    with datahandler as tmp_filepath:
        with open(tmp_filepath, "wb") as fp:
            fp.write(b"\x34\x32")
        assert os.path.exists(filepath)

    assert not os.path.exists(filepath)

    os.rmdir(folder)
    fileroot = str(uuid.uuid4())
    filename = fileroot + ".pdf"
    filepath = os.path.join(folder, filename)

    assert not os.path.exists(filepath)
    datahandler = utils.temp_data_handler(tmp_folder_name=folder, fileroot=fileroot)
    assert not os.path.exists(filepath)

    with datahandler as tmp_filepath:
        with open(tmp_filepath, "wb") as fp:
            fp.write(b"\x34\x32")
        assert os.path.exists(filepath)

    assert not os.path.exists(filepath)
