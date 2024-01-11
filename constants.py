"""Constants to be used by main module."""

# Standard Library Imports
import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

ACCOUNTS_PATH = f"{ROOT_DIR}/data/accounts.csv"
ACCOUNTS_UPDATED_PATH = f"{ROOT_DIR}/data/accounts_updated.csv"
SUBSCRIPTIONS_PATH = f"{ROOT_DIR}/data/subscriptions.csv"
SUBSCRIPTION_ITEMS_PATH = f"{ROOT_DIR}/data/subscription_items.csv"
