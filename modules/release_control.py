import boto3


class ReleaseControl:
    def __init__(self, order_id) -> None:
        self.dyn_resource = boto3.resource(
            "dynamodb", region_name="ap-northeast-1")
        self.table = self.dyn_resource.Table("release_control")
        self.order_id = order_id

    def get_order_release_status(self):
        response = self.table.get_item(Key={"order_id": self.order_id})
        if response.get("Item", None) is None:
            return None
        return response["Item"]["release_status"]

    def is_order_not_released(self):
        release_status = self.get_order_release_status()
        if release_status == "released":
            return False
        else:
            return True

    def update_order_release_status(self):
        self.table.update_item(
            Key={"order_id": self.order_id},
            UpdateExpression="SET #R=:r",
            ExpressionAttributeNames={"#R": "release_status"},
            ExpressionAttributeValues={":r": "released"},
        )
