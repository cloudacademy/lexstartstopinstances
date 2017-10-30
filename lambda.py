import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

AWS_REGION = 'ap-southeast-2'
INTENT_START_INSTANCES = 'StartInstances'
INTENT_STOP_INSTANCES = 'StopInstances'

def lambda_handler(event, context):
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)


def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']

    if intent_name == INTENT_START_INSTANCES:
        return ec2_instances_start(intent_request)

    elif intent_name == INTENT_STOP_INSTANCES:
        return ec2_instances_stop(intent_request)

    raise Exception('Lex Intent with name {} not supported'.format(intent_name))


def ec2_instances_start(intent_request):
    logger.debug("ec2_instances_start entered...")
    logger.debug(intent_request)

    instance_tag = intent_request['currentIntent']['slots']['serverType']

    try:
        ec2 = boto3.client('ec2', region_name=AWS_REGION)
        filters = [{'Name': 'tag:Type', 'Values': [instance_tag]}]
        response = ec2.describe_instances(Filters=filters)

        instance_ids = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instance_ids.append(instance["InstanceId"])

        ec2.start_instances(InstanceIds=instance_ids)

        message = "EC2 instances with tag {} were STARTED successfully!".format(instance_tag)

    except BaseException as e:
        message = "A problem was encountered trying to START the {} EC2 instances".format(instance_tag)
        logger.error('ec2_instances_start, error={}'.format(str(e)))

    return close(message)


def ec2_instances_stop(intent_request):
    logger.debug("ec2_instances_stop entered...")
    logger.debug(intent_request)

    instance_tag = intent_request['currentIntent']['slots']['serverType']

    try:
        ec2 = boto3.client('ec2', region_name=AWS_REGION)
        filters = [{'Name': 'tag:Type', 'Values': [instance_tag]}]
        response = ec2.describe_instances(Filters=filters)

        instance_ids = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instance_ids.append(instance["InstanceId"])

        ec2.stop_instances(InstanceIds=instance_ids)

        message = "EC2 instances with tag {} were STOPPED successfully!".format(instance_tag)

    except BaseException as e:
        message = "A problem was encountered trying to START the {} EC2 instances.".format(instance_tag)
        logger.error('ec2_instances_stop, error={}'.format(str(e)))

    return close(message)


def close(message):
    response = {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": message
            }
        }
    }

    return response
