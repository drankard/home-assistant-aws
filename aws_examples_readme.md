# AWS Integration Examples

These example automations demonstrate how to use the AWS integration with Home Assistant.

## Prerequisites

1. You must have the AWS integration installed and configured with valid AWS credentials.
2. The correlation ID feature must be available in your version of the AWS integration.

## Examples

### List S3 Buckets (`aws_list_s3_buckets.yaml`)

This automation demonstrates how to:
- Call the AWS boto3 service to list all S3 buckets
- Wait for the response using a correlation ID
- Process the response and send a notification with the results

**How to trigger:**
- Automatically at 12:00 PM daily
- Manually by firing an event `list_s3_buckets_request`

### Manage EC2 Instance (`aws_manage_ec2_instance.yaml`) 

This automation demonstrates how to:
- Start or stop an EC2 instance
- Use input parameters to control the behavior
- Wait for the response and notify about the result

**How to trigger:**
Fire an event `manage_ec2_instance` with the following data:
```yaml
service: event.fire
data:
  event_type: manage_ec2_instance
  event_data:
    action: "start"  # or "stop"
    instance_id: "i-0123456789abcdef0"  # your EC2 instance ID
```

## Using the Examples

To use these examples:

1. Copy the desired YAML file to your Home Assistant `/config/automations/` directory
2. Restart Home Assistant or reload automations
3. Trigger the automation as described above

## Correlation IDs

These examples use correlation IDs to link service calls with their responses. This allows automations to wait for specific responses from AWS before proceeding.

You can customize the correlation ID format or generate them in any way that makes sense for your use case. The important thing is that they're unique for each service call.

## Customizing

Feel free to modify these examples to:
- Use different notification services
- Integrate with other Home Assistant entities
- Add additional logic for your specific needs 