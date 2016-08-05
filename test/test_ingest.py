"""

"""

import configparser
import glob
import odo
import os
import pandas as pd
import perturbation.ingest
import pytest
import subprocess
import tempfile

def test_seed(dataset):
    assert 1 == 1

    if dataset["munge"]:
        subprocess.call(["./munge.sh", dataset["data_dir"]])

    config_file = os.path.join(dataset["data_dir"], "config.ini")

    config = configparser.ConfigParser()

    config.read(config_file)

    with tempfile.TemporaryDirectory() as temp_dir:

        sqlite_file = os.path.join(temp_dir, "test.db")

        perturbation.ingest.seed(config=config, input=dataset["data_dir"], output="sqlite:///{}".format(str(sqlite_file)))

        for (k, v) in dict({"cells" : "Cells.csv", "cytoplasm" : "Cytoplasm.csv", "nuclei" : "Nuclei.csv"}).items():
            config["filenames"][k] = v

        for table_key in ["image", "cells", "cytoplasm", "nuclei"]:
            csv_filename = os.path.join(temp_dir, config["filenames"][table_key])

            table_name = config["filenames"][table_key].split(".")[0]

            odo.odo("sqlite:///{}::{}".format(str(sqlite_file), table_name), csv_filename)

            df = pd.read_csv(csv_filename)

            assert df.shape[0] == dataset["ingest"]["{}_nrows".format(table_name)]

            assert df.shape[1] == dataset["ingest"]["{}_ncols".format(table_name)] + 1