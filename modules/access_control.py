import boto3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

NEW_ACCESS = 0
CONTINUE_ACCESS = 1
NO_ACCESS = 2


class AccessControl:
    def __init__(self, machine_id, session_id) -> None:
        self.dyn_resource = boto3.resource("dynamodb", region_name="ap-northeast-1")
        self.table = self.dyn_resource.Table("Access_lock")
        self.machine_id = machine_id
        self.session_id = session_id
        self.timezone = ZoneInfo("Asia/Ho_Chi_Minh")

    def is_session_expired(self, start_time, timeout_seconds=20):
        return datetime.now(self.timezone) - start_time > timedelta(
            seconds=timeout_seconds
        )

    def is_inactive(self, item):
        return item["trang_thai"] == "inactive"

    def is_match_session_id(self, item):
        return item["session_id"] == self.session_id

    def get_access_info(self):
        response = self.table.get_item(Key={"machine_id": self.machine_id})

        if "Item" not in response:
            return NEW_ACCESS

        item = response["Item"]
        start_time = datetime.strptime(item["thoi_gian"], "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=self.timezone
        )

        if self.is_inactive(item) or self.is_session_expired(start_time):
            return NEW_ACCESS
        elif (not self.is_inactive(item)) and self.is_match_session_id(item):
            return CONTINUE_ACCESS
        else:
            return NO_ACCESS

    def start_user_session(self):
        """Bắt đầu một phiên người dùng mới."""
        timestamp = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        self.table.put_item(
            Item={
                "machine_id": self.machine_id,
                "thoi_gian": timestamp,
                "trang_thai": "active",
                "session_id": self.session_id,
            }
        )

    def start_vnpay_session(self):
        """Bắt đầu một phiên người dùng mới."""
        timestamp = (datetime.now(self.timezone) + timedelta(minutes=2)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.table.put_item(
            Item={
                "machine_id": self.machine_id,
                "thoi_gian": timestamp,
                "trang_thai": "active",
                "session_id": self.session_id,
            }
        )
