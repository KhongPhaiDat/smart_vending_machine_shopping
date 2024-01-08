# import boto3


# class Order:
#     def __init__(self) -> None:
#         self.dyn_resource = boto3.resource("dynamodb", region_name="ap-northeast-1")
#         self.menu_table = self.dyn_resource.Table("order_history")

#     # Message is JSON form
#     def addToDatabase(self, message) -> None:
#         response = self.menu_table.put_item(Item=message)
#         return response
