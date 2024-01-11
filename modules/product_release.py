import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ProductReleaseComponent:
    def __init__(self) -> None:
        self.dyn_resource = boto3.resource("dynamodb", region_name="ap-northeast-1")
        self.menu_table = self.dyn_resource.Table("Menu_database")

    def addNewMachineToDatabase(self, data):
        message = "Add máy thành công"
        try:
            response = self.menu_table.put_item(Item=data)
        except ClientError as err:
            message = f"Couldn't update product list to table Menu_database. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}"
            logger.error(message)
        return message

    def updateProductListToDatabase(self, id, product_list):
        message = ""
        try:
            response = self.menu_table.update_item(
                Key={"id": id},
                UpdateExpression="SET #I=:i",
                ExpressionAttributeNames={"#I": "items"},
                ExpressionAttributeValues={":i": product_list},
            )
        except ClientError as err:
            message = f"Couldn't update product list to table Menu_database. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}"
            logger.error(
                message,
            )
        return message
