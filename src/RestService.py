import requests
from .defaultEnums import RestMethods
import json


class RestServiceProvider:
    def executeRest(self, args: dict):
        if args.get('method') == RestMethods.GET:
            url = self.construct_url(args.get('base_url'), args.get('endpoint'))
            response = requests.get(url, params=args.get('params'), headers=args.get('headers'))
            response = self.get_json(response.content) if response else None
            return response
        elif args.get('method') == RestMethods.POST:
            url = self.construct_url(args.get('base_url'), args.get('endpoint'))
            response = requests.post(
                url,
                params=args.get('params'),
                headers=args.get('headers'),
                json=args.get('data')
            )
            print("DEBUG: Status code after making POST request ->", response.status_code)
            print("DEBUG: Response content after making POST request ->", response.content)
            print(" \n ")
            response = self.get_json(response.content) if response else None
            return response

    def construct_url(self, base, endpoint):
        url = base + endpoint
        return url

    def get_json(self, data):
        return json.loads(data)
