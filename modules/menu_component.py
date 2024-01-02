import boto3


class MenuComponent:
    def __init__(self) -> None:
        self.dyn_resource = boto3.resource("dynamodb", region_name="ap-northeast-1")
        self.menu_table = self.dyn_resource.Table("Menu_database")

    def queryMenuByMachineIDFromDatabase(self, id):
        response = self.menu_table.get_item(Key={"id": id})
        return response["Item"]

    def returnMenuByMachineID(self, id):
        return self.queryMenuByMachineIDFromDatabase(id=id)
