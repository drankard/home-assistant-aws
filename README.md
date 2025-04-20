# Home Assistant AWS Integration

This integration provides a service interface for interacting with Amazon Web Services (AWS) from Home Assistant.

## Installation

### HACS (Recommended)
1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. In HACS, add this repository as a custom repository (category: Integration)
3. Download the integration and restart Home Assistant

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
| correlation_id | Unique ID for this request (auto-generated if not provided) | No | "my-request-id" |

### Examples

#### Basic STS Get Caller Identity
```yaml
service: aws.boto3
data:
  client: sts
  method: get_caller_identity
  sync: true
```

### Event: aws_boto3_response

When `sync: true` is specified, an event `aws_boto3_response` will be fired with the API response.

## Automation Examples

A complete automation example using the AWS STS identity API is available in the `examples/aws_sts_identity_automation.yaml` file.

## Development

### Testing

The integration includes pytest-based tests that verify core functionality:

1. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

2. Run the tests:
   ```bash
   pytest
   ```

The tests cover:
- Service registration
- Successful AWS API calls
- Error handling
- Response storage and retrieval
- Event firing

## Security Best Practices

### AWS IAM Security

This integration requires AWS credentials to function. Follow these best practices to ensure secure usage:

1. **Use Least Privilege IAM Policies**
   - **NEVER** use Administrator access for this integration
   - Create dedicated IAM users with only the specific permissions needed
   - Start with zero permissions and add only what's required for your specific use case
   - Use AWS IAM Access Analyzer to audit and refine permissions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

We use semantic versioning with standard `vX.Y.Z` format for all tags.