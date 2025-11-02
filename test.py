import boto3
import concurrent.futures
from botocore.exceptions import ClientError

lambda_client = boto3.client("lambda")

def check_concurrency(fn_name):
    try:
        resp = lambda_client.get_function_concurrency(FunctionName=fn_name)
        reserved = resp.get("ReservedConcurrentExecutions")
        if reserved is not None:
            print(f"{fn_name} -> ReservedConcurrency = {reserved}")
        else:
            print(f"{fn_name} -> No reserved concurrency")
    except ClientError as e:
        # most common when concurrency is not configured
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"{fn_name} -> No reserved concurrency")
        else:
            print(f"{fn_name} -> Error: {e}")

def main():
    functions = []
    paginator = lambda_client.get_paginator("list_functions")
    for page in paginator.paginate():
        for fn in page["Functions"]:
            functions.append(fn["FunctionName"])

    print(f"Checking {len(functions)} functions...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(check_concurrency, functions)

if __name__ == "__main__":
    main()