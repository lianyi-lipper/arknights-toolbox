import requests
from urllib.parse import urljoin, urlparse
from skland.api import ZonaiApiClient, ZonaiResponse
from skland.model.exception import SklandApiException


class HttpxClient(ZonaiApiClient):
    """
    基于 requests 的底层 HTTP 通信客户端。
    负责管理基础 headers、设置请求凭证 (cred)，生成森空岛请求签名，并自动处理接口返回的错误代码。
    """
    def __init__(self, base_url: str, version="1.0.1"):
        super().__init__()
        self.version = version
        self.base_url = base_url
        self.client = requests.Session()
        self.cred = ""
        self.client.headers.update({
            "User-Agent": f"Skland/{self.version} (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0",
            "Accept-Encoding": "gzip",  # requests 不原生支持 br/zstd，强制只用 gzip 避免解压失败
            "os": "Android",
            "platform": "1",
            "manufacturer": "Android",
            "vName": self.version
        })

    def set_credential(self, cred: str, sign_token: str = ""):
        """
        设置森空岛的核心访问凭证 cred 和用于生成签名的 sign_token。
        该方法必须在发起实际的业务请求之前被调用。
        """
        self.cred = cred
        self.sign_token = sign_token
        self.client.headers.update(
            {"cred": cred}
        )

    def __process_response(self, resp: requests.Response) -> ZonaiResponse:
        """
        统一的响应处理与异常抛出逻辑。
        将原始 HTTP 响应转为 ZonaiResponse 实例。如果业务 code 非 0，则抛出对应的 SklandApiException 异常。
        """
        try:
            resp: ZonaiResponse = ZonaiResponse.from_dict(resp.json())
            if resp.code != 0:
                raise SklandApiException(resp.code, resp.message)
            return resp
        except SklandApiException as e:
            raise e
        except Exception as e:
            raise SklandApiException(-1, str(e))

    def _generate_signature(self, path: str, body_or_query: str) -> dict:
        """
        核心签名生成算法 (generate_signature)。
        根据请求路径、请求体 (或 query string)、当前时间戳和设备 dId，通过 HMAC-SHA256 和 MD5 计算出用于校验的 sign 签名。
        返回需要额外附加的 headers 字典（包括 timestamp、dId、vName 和 sign）。
        """
        import time
        import hmac
        import hashlib
        import json
        from skland.api.SecuritySm import get_d_id

        t = str(int(time.time()) - 2)
        token = self.sign_token.encode('utf-8') if hasattr(self, 'sign_token') and self.sign_token else b""
        
        # We need a new dId or a cached one
        if not hasattr(self, 'did') or not self.did:
            self.did = get_d_id()

        header_ca = {
            'platform': '1',
            'timestamp': t,
            'dId': self.did if self.did else '',
            'vName': self.version
        }
        
        header_ca_str = json.dumps(header_ca, separators=(',', ':'))
        s = path + body_or_query + t + header_ca_str
        
        if not token:
            hex_s = hmac.new(b'', s.encode('utf-8'), hashlib.sha256).hexdigest()
        else:
            hex_s = hmac.new(token, s.encode('utf-8'), hashlib.sha256).hexdigest()
            
        md5 = hashlib.md5(hex_s.encode('utf-8')).hexdigest().encode('utf-8').decode('utf-8')
        
        header_ca['sign'] = md5
        return header_ca

    def get(self, path, headers=None) -> ZonaiResponse:
        """
        发起 GET 请求，并会自动填充前面计算的签名相关的 Headers。
        """
        p = urlparse(path)
        sign_headers = self._generate_signature(p.path, p.query)
        req_headers = dict(self.client.headers)
        if headers:
            req_headers.update(headers)
        req_headers.update(sign_headers)
        
        return self.__process_response(
            self.client.request("GET", urljoin(self.base_url, path), headers=req_headers)
        )

    def post(self, path, data=None, headers=None) -> ZonaiResponse:
        """
        发起 POST 请求，同样会自动计算和填充签名 Headers。对于 POST 报文，会提取 body 字符串参与签名。
        """
        import json
        p = urlparse(path)
        body_str = json.dumps(data) if data else "{}"
        if not data:
            # skland auto sign requires body_str to be '' if None? Wait, skyland.py does `json.dumps(body)` which is "{}" if empty, or `""` if not post?
            # Actually skyland.py: `generate_signature(http_local.token, p.path, json.dumps(body))`
            # So {} is fine if body is {}
            pass

        sign_headers = self._generate_signature(p.path, body_str)
        req_headers = dict(self.client.headers)
        if headers:
            req_headers.update(headers)
        req_headers.update(sign_headers)
        
        return self.__process_response(
            self.client.request("POST", urljoin(self.base_url, path), json=data, headers=req_headers)
        )

    def put(self, path, data=None, headers=None) -> ZonaiResponse:
        return self.__process_response(
            self.client.put(urljoin(self.base_url, path), json=data, headers=headers)
        )

    def delete(self, path, data=None, headers=None) -> ZonaiResponse:
        return self.__process_response(
            self.client.request(
                "DELETE",
                urljoin(self.base_url, path),
                json=data,
                headers=headers
            )
        )
