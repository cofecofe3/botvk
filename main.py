from flask import Flask, abort
from random import randint
from urllib.parse import urlparse, parse_qs
from flask import request
import vk_api
import os

app = Flask(__name__)

vk = vk_api.VkApi(token=os.environ['VK_API_ACCESS_TOKEN'])
allowed_ids = map(lambda num: int(num), os.environ['ALLOWED_IDS'].split(','))

print(allowed_ids)


@app.route("/", methods=['POST', 'GET'])
def hello():
    print('got request, heh')
    if request.method == 'GET':
        return "This is bot!"
    else:
        # Real logic
        request_json = request.get_json(force=True)

        print(request_json)

        if request_json['type'] == 'message_new':
            user_id = request_json['object']['user_id']

            print(user_id)

            if user_id in allowed_ids:

                print('got one with allowed id')

                url = request_json['object']['body']
                parsed_url = urlparse(url)
                parsed_qs = parse_qs(parsed_url.query)
                post_id = parsed_qs['w'][0].split('-')[1]

                print(post_id)

                users_response = vk.method('groups.getMembers', {'group_id': post_id.split('_')[0]})

                print('this is user response, heh')
                print(users_response)

                total_user_count = users_response['count']
                users = users_response['items']

                while len(users) != total_user_count:
                    additional_users_response = vk.method('groups.getMembers', {'group_id': post_id.split('_')[0],
                                                                                'offset': len(users)})
                    users = users + additional_users_response['items']

                print(users)

                for user in users:
                    vk.method('messages.send', {'user_id': user, 'attachment': f'wall{post_id}',
                                                'random_id': randint(0, 2147483647)})
            else:
                vk.method('messages.send', {'user_id': user_id, 'message': f'Hello ! Your id is {user_id}. You have '
                                                                           f'no permission to interact with me',
                                            'random_id': randint(0, 2147483647)})
            return 'ok'
        elif request_json['type'] == 'confirmation':
            return os.environ['CALLBACK_API_CONFIRMATION_TOKEN']
        else:
            return "Unsupported request type"