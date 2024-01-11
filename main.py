"""Module to perform Annual Recurring Revenue calculations."""

# Standard Library Imports
import logging
import os
from datetime import datetime

# Third-Party Imports
import pandas as pd

# Project-Level Imports
from constants import (
    ACCOUNTS_PATH,
    ACCOUNTS_UPDATED_PATH,
    SUBSCRIPTION_ITEMS_PATH,
    SUBSCRIPTIONS_PATH,
)

logger = logging.getLogger()
logger.setLevel("INFO")
logging.basicConfig()


def get_ultimate_parent(account_id: str, account_dict: dict) -> str:
    """
    Function to recursively find the ultimate parent id.

    :param account_id: the specified account id
    :param account_dict: dict containing account id and corresponding parent id {account id: parent id}
    :return: the ultimate parent id for the specified account id
    """

    if account_dict[account_id] == "":
        return account_id

    return get_ultimate_parent(account_dict[account_id], account_dict)


def calculate_arr(subscription_item: pd.DataFrame) -> float:
    """
    Function to calculate ARR (Annual Recurring Revenue) for a given subscription item.

    :param subscription_item: dataframe containing subscription item information
    :return: an ARR value
    """

    unit_price = round(
        subscription_item["list_price"] * (1 - subscription_item["discount"]), 2
    )
    arr = subscription_item["quantity"] * unit_price

    return arr


def main() -> pd.DataFrame:
    """
    Function to produce an updated accounts.csv containing the ARR,
    hierarchical ARR, and ultimate parent for each account.

    :return: a dataframe containing information for all accounts
    """

    try:
        os.path.exists(ACCOUNTS_PATH)
        os.path.exists(SUBSCRIPTIONS_PATH)
        os.path.exists(SUBSCRIPTION_ITEMS_PATH)
    except FileNotFoundError:
        logging.error("Please verify necessary files exist.")

    logging.info("Loading csvs into dataframes.")

    # Load CSV files into DataFrames
    accounts_df = pd.read_csv(ACCOUNTS_PATH, keep_default_na=False)
    subscriptions_df = pd.read_csv(SUBSCRIPTIONS_PATH)
    subscription_items_df = pd.read_csv(SUBSCRIPTION_ITEMS_PATH)

    # Convert date columns to datetime objects
    # subscriptions_df["start_date"] = pd.to_datetime(subscriptions_df["start_date"])
    # subscriptions_df["end_date"] = pd.to_datetime(subscriptions_df["end_date"])
    # subscription_items_df["start_date"] = pd.to_datetime(
    #     subscription_items_df["start_date"]
    # )
    # subscription_items_df["end_date"] = pd.to_datetime(
    #     subscription_items_df["end_date"]
    # )
    subscriptions_df["start_date"] = pd.to_datetime(subscriptions_df["start_date"])
    subscriptions_df["end_date"] = pd.to_datetime(subscriptions_df["end_date"])
    subscription_items_df["start_date"] = pd.to_datetime(
        subscription_items_df["start_date"]
    )
    subscription_items_df["end_date"] = pd.to_datetime(
        subscription_items_df["end_date"]
    )

    logging.info("Getting ultimate parent ids.")

    # Create a dictionary of account ids and corresponding parent ids from accounts_df
    accounts_dict = accounts_df.set_index("id").to_dict()["parent_id"]

    # Generate list of ultimate parent ids using recursive search
    ultimate_parents = [
        get_ultimate_parent(acct_id, accounts_dict) for acct_id in accounts_dict.keys()
    ]

    # Create a new dataframe with list of ultimate parents
    ultimate_parents_df = pd.DataFrame(
        pd.Series(ultimate_parents),
        columns=[
            "ultimate_parent_id",
        ],
    )

    # Update accounts_df with the ultimate_parent_ids
    accounts_df.loc[accounts_df.index, "ultimate_parent_id"] = ultimate_parents_df[
        "ultimate_parent_id"
    ]

    logging.info("Calculating ARR values.")

    # Calculate ARR for each subscription item
    subscription_items_df["arr"] = subscription_items_df.apply(calculate_arr, axis=1)

    # Filter out inactive subscription items
    active_subscription_items = subscription_items_df[
        (subscription_items_df["start_date"] <= datetime.today().date())
        & (subscription_items_df["end_date"] >= datetime.today().date())
    ]

    # Calculate ARR for each subscription
    subscriptions_df["arr"] = subscriptions_df["id"].map(
        active_subscription_items.groupby("subscription_id")["arr"].sum()
    )

    # Filter out inactive subscriptions
    active_subscriptions = subscriptions_df[
        (subscriptions_df["start_date"] <= datetime.today().date())
        & (subscriptions_df["end_date"] >= datetime.today().date())
    ]

    # Calculate ARR for each account
    accounts_df["arr"] = accounts_df["id"].map(
        active_subscriptions.groupby("account_id")["arr"].sum()
    )

    # Calculate hierarchy ARR for each account
    accounts_df["hierarchy_arr"] = accounts_df["ultimate_parent_id"].map(
        accounts_df.groupby("ultimate_parent_id")["arr"].sum()
    )

    logging.info("Saving to file: accounts_updated.csv")

    # Save the updated accounts df
    accounts_df.to_csv(ACCOUNTS_UPDATED_PATH, index=False)

    return accounts_df


if __name__ == "__main__":
    main()
