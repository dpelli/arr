"""Unit testing for main module."""

# Standard Library Imports
import datetime
import os
import unittest
from unittest import mock

# Third-Party Imports
from freezegun import freeze_time

# Project-Level Imports
from main import main

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

ACCOUNTS_PATH = f"{ROOT_DIR}/test_data/accounts.csv"
SUBSCRIPTIONS_PATH = f"{ROOT_DIR}/test_data/subscriptions.csv"
SUBSCRIPTION_ITEMS_PATH = f"{ROOT_DIR}/test_data/subscription_items.csv"


@freeze_time("2023-11-27")
@mock.patch("main.ACCOUNTS_PATH", ACCOUNTS_PATH)
@mock.patch("main.SUBSCRIPTIONS_PATH", SUBSCRIPTIONS_PATH)
@mock.patch("main.SUBSCRIPTION_ITEMS_PATH", SUBSCRIPTION_ITEMS_PATH)
class TestMain(unittest.TestCase):
    def test_frozen_date(self):
        self.assertEqual(datetime.datetime.today().date(), datetime.datetime(2023, 11, 27).date())

    def test_when_id_is_ultimate_parent(self):
        result = main()
        result_ultimate_parent_id = result.loc[0]["ultimate_parent_id"]

        self.assertEqual(
            result_ultimate_parent_id, "bef9e851-552f-4330-96e1-a01adb2e7466"
        )

    def test_correct_ultimate_parent_for_indirect_child(self):
        result = main()
        result_ultimate_parent_id = result.loc[1]["ultimate_parent_id"]

        self.assertEqual(
            result_ultimate_parent_id, "a0aa1af7-dd7c-4a57-a2c1-08cb9317c826"
        )

    def test_correct_arr(self):
        result = main()
        result_arr = result[result["id"] == "194de40b-4c88-40be-8bc3-535afea06305"]

        self.assertEqual(result_arr["arr"].values[0], 641784.36)

    def test_correct_hierarchy_arr(self):
        result = main()
        result_arr = result[result["id"] == "9d58c9e6-4c5b-4d07-bf7a-f4a9e7ee9002"]

        self.assertEqual(result_arr["hierarchy_arr"].values[0], 462306.33)


if __name__ == "__main__":
    unittest.main()
