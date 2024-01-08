import time
import boto3
from datetime import datetime, timedelta
import streamlit as st
import pages.menu as menu
import uuid
import modules.access_control as access_control

NEW_ACCESS = 0
CONTINUE_ACCESS = 1
NO_ACCESS = 2

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

st.write("Your session id is: ", st.session_state['session_id'])

machine_id = st.experimental_get_query_params()['id'][0]

access_control = access_control.AccessControl(
    machine_id=machine_id,
    session_id=st.session_state['session_id']
)

# # Thiết lập kết nối DynamoDB
# dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
# table = dynamodb.Table('Access-lock')

# # Check if session expired


# def is_session_expired(start_time, timeout_seconds=180):
#     """Kiểm tra xem phiên có quá hạn chờ hay không."""
#     return datetime.now() - start_time > timedelta(seconds=timeout_seconds)


# def is_inactive(item):
#     return item['trang_thai'] == 'inactive'


# def is_match_session_id(item):
#     return item['session_id'] == st.session_state['session_id']

# # Check if session is active


# def get_access_info(machine_id):
#     response = table.get_item(Key={"machine_id": machine_id})

#     if 'Item' not in response:
#         return NEW_ACCESS

#     item = response['Item']
#     start_time = datetime.strptime(item['thoi_gian'], "%Y-%m-%d %H:%M:%S")

#     if is_inactive(item) or is_session_expired(start_time):
#         return NEW_ACCESS
#     elif (not is_inactive(item)) and is_match_session_id(item):
#         return CONTINUE_ACCESS
#     else:
#         return NO_ACCESS


# def start_user_session(machine_id):
#     """Bắt đầu một phiên người dùng mới."""
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     table.put_item(
#         Item={
#             'machine_id': machine_id,
#             'thoi_gian': timestamp,
#             'trang_thai': 'active',
#             'session_id': st.session_state['session_id']
#         }
#     )


def main():

    access_decision = access_control.get_access_info()
    if access_decision == NO_ACCESS:
        st.write(
            "Máy đang được sử dụng bởi người dùng khác. Vui lòng đợi một lát nhé!!!")
    elif access_decision == NEW_ACCESS:
        access_control.start_user_session()
        st.write("Bạn đang mua hàng tại máy số: ", machine_id)
        menu.main()
    elif access_decision == CONTINUE_ACCESS:
        st.write("Bạn đang mua hàng tại máy số: ", machine_id)
        menu.main()


main()
