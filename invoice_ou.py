import boto3
import datetime
import io
import csv


current_date = datetime.date.today()
current_month_first_day = current_date.replace(day=1)
prev_month_last_day = current_month_first_day - datetime.timedelta(days=1)
prev_month_first_day = prev_month_last_day.replace(day=1)
end_date = current_month_first_day.strftime('%Y-%m-%d')
start_date = prev_month_first_day.strftime('%Y-%m-%d')


boto3.setup_default_session(profile_name='abra-cloud-reseller')
org_client = boto3.client('organizations')
ce_client = boto3.client('ce')
ous = org_client.list_organizational_units_for_parent(
    ParentId='ou-tnek-b3svcnrz'
)

data = []
customers = {}
csv_buffer = io.StringIO()
writer = csv.writer(csv_buffer)
writer.writerow(['Customer', 'Currency', 'BeforeTax', 'AfterTax', 'MarketPlace', 'Total'])

file_path = f"aws_invoice_{end_date}.csv"
with open(file_path, mode='a', newline='') as csv_file:
    writer2 = csv.writer(csv_file)
    writer2.writerow(['Customer', 'Currency', 'BeforeTax', 'AfterTax', 'MarketPlace', 'Total'])

for customer in ous['OrganizationalUnits']:
    customers[customer['Name']] = customer['Id']
print(customers)
for customer, ou_id in customers.items():

    response = org_client.list_accounts_for_parent(ParentId=ou_id)
    accounts = response['Accounts']

    total_invoice_amount = 0
    total_invoice_withouttax = 0
    total_invoice_marketplace = 0
    for account in accounts:

        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            Filter={
                'And': [
                    {
                        'Dimensions': {
                            'Key': 'LINKED_ACCOUNT',
                            'Values': [account['Id']]
                        }
                    },
                    {
                        'Dimensions': {
                            'Key': 'BILLING_ENTITY',
                            'Values': ['AWS']
                        }
                    },
                ]
            }
        )
        invoice_amount = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
        total_invoice_amount += invoice_amount
        result_by_time = response['ResultsByTime']

        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            Filter={
                'And': [
                    {
                        'Dimensions': {
                            'Key': 'LINKED_ACCOUNT',
                            'Values': [account['Id']]
                        }
                    },
                    {
                        'Dimensions': {
                            'Key': 'BILLING_ENTITY',
                            'Values': ['AWS']
                        }
                    },
                    {
                        'Not': {
                            'Dimensions': {
                                'Key': 'RECORD_TYPE',
                                'Values': ['Tax']
                            }
                        }
                    }

                ]
            }
        )
        invoice_withouttax = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
        total_invoice_withouttax += invoice_withouttax
        result_by_time = response['ResultsByTime']
        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            Filter={
                'And': [
                    {
                        'Dimensions': {
                            'Key': 'LINKED_ACCOUNT',
                            'Values': [account['Id']]
                        }
                    },
                    {
                        'Dimensions': {
                            'Key': 'BILLING_ENTITY',
                            'Values': ['AWS']
                        }
                    },
                ]
            }
        )
        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            Filter={
                'And': [
                    {
                        'Dimensions': {
                            'Key': 'LINKED_ACCOUNT',
                            'Values': [account['Id']]
                        }
                    },
                    {
                        'Dimensions': {
                            'Key': 'BILLING_ENTITY',
                            'Values': ['AWS Marketplace']
                        }
                    },
                ]
            }
        )
        invoice_amount_marketplace = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
        total_invoice_marketplace += invoice_amount_marketplace
        result_by_time = response['ResultsByTime']
    invoice = round(total_invoice_amount, 2)
    invoicewithouttax = round(total_invoice_withouttax, 2)
    writer.writerow([customer, 'USD', invoicewithouttax, invoice, total_invoice_marketplace, invoice+total_invoice_marketplace])
    with open(file_path, mode='a', newline='') as csv_file:
        writer2 = csv.writer(csv_file)
        writer2.writerow([customer, 'USD', invoicewithouttax, invoice, total_invoice_marketplace, invoice+total_invoice_marketplace])
#print(csv_buffer.getvalue())