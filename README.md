# Home Assistant AWS Integration

This integration provides a service interface for interacting with Amazon Web Services (AWS) from Home Assistant.

## Installation

### HACS (Recommended)
1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Add this repository to HACS as a custom repository:
   - Go to HACS > Integrations > ⋮ (three dots menu in top right) > Custom repositories
   - Add URL: `https://github.com/drankard/home-assistant-aws`
   - Category: Integration
   - Click "ADD"
3. **Important**: After adding the repository, you must download it:
   - Click on "AWS Integration" in the list of custom repositories
   - Click "DOWNLOAD" in the bottom right corner
   - Wait for installation to complete
4. Restart Home Assistant from the Configuration menu
5. After restart, confirm the integration is available in Settings > Devices & Services > Add Integration

### Manual Installation
1. Download this repository as a ZIP file
2. Extract the ZIP file
3. Copy the `custom_components/aws` directory to your Home Assistant `custom_components` directory
4. Restart Home Assistant

## Configuration

1. Go to Home Assistant > Settings > Devices & Services
2. Click "+ Add Integration"
3. Search for "AWS" and select it
4. Enter your AWS credentials and region

## Usage

This integration provides a generic service to call any AWS API using boto3.

### Service: aws.boto3

Call any AWS API using boto3.

| Parameter | Description | Required | Example |
|-----------|-------------|----------|---------|
| client | AWS service client name | Yes | "s3" |
| method | Client method to call | Yes | "list_buckets" |
| params | Parameters to pass to the method | No | {"Bucket": "my-bucket"} |
| region_name | AWS region (overrides default) | No | "us-west-2" |
| sync | Wait for response and fire event | No | true |

### Examples

#### List S3 Buckets
```yaml
service: aws.boto3
data:
  client: s3
  method: list_buckets
  sync: true
```

#### Start an EC2 Instance
```yaml
service: aws.boto3
data:
  client: ec2
  method: start_instances
  params:
    InstanceIds:
      - i-1234567890abcdef0
```

### Event: aws_boto3_response

When `sync: true` is specified, an event `aws_boto3_response` will be fired with the API response.

## Development

### Testing

#### Basic Testing
For quick and simple tests that don't require the full Home Assistant test infrastructure:

1. Use simple unittest tests:
   ```bash
   python -m unittest tests/simple_test.py
   ```

   This runs basic tests that verify:
   - Core functionality works
   - AWS boto3 calls are made correctly
   - Integration structure is proper

2. This approach is faster and requires fewer dependencies than full pytest setup.

#### Full Test Suite
To run tests with the full Home Assistant test framework:

1. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

2. Run the tests:
   ```bash
   pytest
   ```

3. Run tests with coverage report:
   ```bash
   pytest --cov=custom_components.aws
   ```

## Security Notes

Store your AWS credentials securely and use an IAM account with minimal permissions needed for your use case.

## License

This project is licensed under the MIT License.
