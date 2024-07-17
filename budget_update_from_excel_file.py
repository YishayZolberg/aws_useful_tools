import boto3
import pandas as pd

client = boto3.client('budgets')
download_path = '/path-to/file-location/'
excel_file = 'file_name.xlsx'
df = pd.read_excel(download_path + excel_file)
PAYER_ACCOUNT_ID = '1234567890'
for index, row in df.iterrows():
    # Change the value like the headers values in the xls file
    budget_name = row['Budget Name']
    new_threshold_amount = row['Budget - New']

    response = client.describe_budget(
        AccountId=PAYER_ACCOUNT_ID,
        BudgetName=budget_name
    )
    budget_details = response['Budget']

    budget_details['BudgetLimit']['Amount'] = str(new_threshold_amount)
    client.update_budget(
        AccountId=PAYER_ACCOUNT_ID,
        NewBudget=budget_details
    )

    print(f"The threshold for budget '{budget_name}' has been updated to ${new_threshold_amount}.")

print("All budgets have been updated.")
