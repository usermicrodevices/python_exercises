default_bot_settings = {'name':'bot_name', 'login':'your_login_bot', 'link':'http://t.me/mcd_support_bot', 'token':'bot_token', 'recipients':{0000000000:'John Doe'}}

import argparse, json, requests

def send(value):
	responses = []
	token = default_bot_settings['token']
	for chat_id, chat_desc in default_bot_settings['recipients'].items():
		send_url = f'https://api.telegram.org/bot{token}/sendMessage'
		send_data = {'chat_id':chat_id, 'text':value, 'parse_mode':'HTML'}
		data_as_json = json.dumps(send_data, ensure_ascii=False).encode('utf-8')
		headers_request = {'content-type':'application/json', 'content-length':f'{len(data_as_json)}'}
		try:
			response = requests.post(send_url, data=data_as_json, headers=headers_request, timeout=(3, 3))
		except Exception as e:
			responses.append(f'{chat_desc}::{e}')
		else:
			responses.append(response.json())
	return responses

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--test', help='send to telegram')
	parser.add_argument('--message', help='text send to telegram')
	args = parser.parse_args()
	resp = ''
	if args.test:
		resp = send('✉️essage 🎌rom 🐍ython')
	elif args.message:
		resp = send(args.message)
	elif args.help:
		parser.print_help()
	else:
		parser.print_help()
	if resp:
		print(resp)
