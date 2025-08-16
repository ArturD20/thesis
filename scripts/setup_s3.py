import boto3
import time
import json

# settings
cur_bucket_name = "cur-bucket-thesis-20250816"  
test_buckets = {
    "standard": "test-bucket-standard-thesis-20250816",
    "warm": "test-bucket-warm-thesis-20250816",
    "cold": "test-bucket-cold-thesis-20250816",
    "intelligent": "test-bucket-intelligent-thesis-20250816"
}

# s3 client
s3 = boto3.client("s3")
s3control = boto3.client("s3control")
account_id = boto3.client("sts").get_caller_identity()["Account"]

# creating cur bucket
try:
    s3.create_bucket(
        Bucket=cur_bucket_name,
        CreateBucketConfiguration={"LocationConstraint": boto3.session.Session().region_name}
    )
    print(f"Bucket CUR '{cur_bucket_name}' utworzony")
except s3.exceptions.BucketAlreadyOwnedByYou:
    print(f"Bucket CUR '{cur_bucket_name}' już istnieje")

# creating buckets
for tier, name in test_buckets.items():
    try:
        s3.create_bucket(
            Bucket=name,
            CreateBucketConfiguration={"LocationConstraint": boto3.session.Session().region_name}
        )
        print(f"Bucket testowy '{name}' utworzony")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket testowy '{name}' już istnieje")

# 3️⃣ Przykład ustawienia lifecycle dla warm/cold/intelligent
# Stwórz JSON dla lifecycle
warm_lifecycle = {
    "Rules": [
        {
            "ID": "WarmTransition",
            "Status": "Enabled",
            "Filter": {"Prefix": ""},
            "Transitions": [
                {"Days": 30, "StorageClass": "STANDARD_IA"}
            ]
        }
    ]
}

cold_lifecycle = {
    "Rules": [
        {
            "ID": "ColdTransition",
            "Status": "Enabled",
            "Filter": {"Prefix": ""},
            "Transitions": [
                {"Days": 30, "StorageClass": "ONEZONE_IA"},
                {"Days": 60, "StorageClass": "GLACIER"}
            ]
        }
    ]
}

intelligent_lifecycle = {
    "Rules": [
        {
            "ID": "IntelligentTransition",
            "Status": "Enabled",
            "Filter": {"Prefix": ""},
            "Transitions": [
                {"Days": 0, "StorageClass": "INTELLIGENT_TIERING"}
            ]
        }
    ]
}

s3.put_bucket_lifecycle_configuration(
    Bucket=test_buckets["warm"],
    LifecycleConfiguration=warm_lifecycle
)
s3.put_bucket_lifecycle_configuration(
    Bucket=test_buckets["cold"],
    LifecycleConfiguration=cold_lifecycle
)
s3.put_bucket_lifecycle_configuration(
    Bucket=test_buckets["intelligent"],
    LifecycleConfiguration=intelligent_lifecycle
)

print("Lifecycle rules ustawione dla testowych bucketów")

# 4️⃣ Storage Lens (przykład prosty, tworzymy dashboard)
s3control.put_storage_lens_configuration(
    AccountId=account_id,
    ConfigId="test-dashboard",
    StorageLensConfiguration={
        "Id": "test-dashboard",
        "IsEnabled": True,
        "Include": {"Buckets": [f"arn:aws:s3:::{name}" for name in test_buckets.values()]},
        "AccountLevel": {
            "ActivityMetrics": {"IsEnabled": True},
            "BucketLevel": {"ActivityMetrics": {"IsEnabled": True}}
        }
    }
)
print("Storage Lens dashboard 'test-dashboard' utworzony")
