import requests
from utils.db import Db
from math import ceil
import urllib.parse


class Parse(Db):
    def __init__(self):
        super().__init__()
        self.rpc_links = [
            'https://story-testnet-rpc.contributiondao.com/validators',
            'https://story-testnet.rpc.kjnodes.com/validators',
            'https://story-testnet-rpc.itrocket.net/validators',
            'https://odyssey.storyrpc.io/validators'
            ]
        self.api_links = [
            'https://api-story-testnet.itrocket.net/cosmos/staking/v1beta1/validators'
            ]
    
    def run(self) -> list:
        try:
            rpc_datas = self.get_rpcs()
            addresses = self.get_address(rpc_datas)
            moniker_datas = self.get_apis()
            parse_result = self.get_result_list(addresses, moniker_datas)
            result = self.get_db_result(parse_result)
            self._logger.info(f'Received {len(result)} new RPC and API tokens.')
            return result
        except Exception as ex:
            self._logger.error(ex)

    def get_db_result(self, parse_result: list) -> list:
        result = []
        for data in parse_result:
            if not self.does_record_exist(f"rpc = '{data['rpc']}'"):
                self.insert(data)
                result.append(data)
        return result

    def get_result_list(self, addresses: list, moniker_datas: list) -> list:
        result = []
        filtered_data = [
            {"moniker": entry["description"]["moniker"], "key": entry["consensus_pubkey"]["key"]}
            for entry in moniker_datas
            if "description" in entry and "moniker" in entry["description"] and "consensus_pubkey" in entry and "key" in entry["consensus_pubkey"]
        ]
        for address in addresses:
            moniker = self.get_moniker(address['value'], filtered_data)
            if moniker:
                res = {
                    'rpc': address['address'],
                    'moniker': moniker
                }
                result.append(res)
        if result:
            return result
        raise Exception("In the obtained RPC and API lists, there are no matching linking keys.")

    def get_moniker(self, rpc_value: str, moniker_datas: list) -> str:
        for moniker_data in moniker_datas:
            if moniker_data['key'] == rpc_value:
                return moniker_data['moniker']
        return None

    def get_address(self, datas: list) -> list:
        result = [
            {"address": entry["address"], "value": entry["pub_key"]["value"]}
            for entry in datas
            if "address" in entry and "pub_key" in entry and "value" in entry["pub_key"]
        ]
        if result:
            return result
        raise Exception("In the resulting list, there is no address and value.")

    def get_rpcs(self) -> list:
        for link in self.rpc_links:
            result = self.get_next_rpcs(link) 
            if result:
                return result
        raise Exception("Failed to retrieve RPC data from the specified links.")
    
    def get_next_rpcs(self, url: str, result_nex: list = [], pages:int = 1, total_pages:int = 0) -> dict:
        result = self.get_respose(url)
        if result:
            if 'result' in result and result['result']:
                r = result['result']
                if total_pages == 0 and 'total' in r and r['total'] and 'count' in r and r['count']:
                    total_pages = ceil(int(r['total'])/int(r['count']))
                if 'validators' in result['result'] and result['result']['validators']:
                    result_nex.extend(result['result']['validators'])  
                if pages <= total_pages:
                    page = pages + 1
                    link = url.split('?')[0] + f'?page={pages}'
                    return self.get_next_rpcs(link, result_nex, page, total_pages)       
        return result_nex
    
    def get_apis(self) -> list:
        for link in self.api_links:
            result = self.get_next_moniker(link)
            if result:
                return result
        raise Exception("Failed to retrieve API data from the specified links.")
    
    def get_next_moniker(self, url: str, result_nex: list = []) -> dict:
        result = self.get_respose(url)
        if result:
            if 'validators' in result and result['validators']:
                result_nex.extend(result['validators']) 
                if 'pagination' in result and result['pagination']:
                    url = url.split('?')[0]
                    encoded_next_key = encoded_next_key = urllib.parse.quote(result['pagination']['next_key'])
                    link = url + f"?pagination.key={encoded_next_key}"
                    return self.get_next_moniker(link, result_nex)                    
        return result_nex

    def get_respose(self, link: str) -> dict:
        try:
            response = requests.get(url=link, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as ex:
            self._logger.error(ex)
        return None
