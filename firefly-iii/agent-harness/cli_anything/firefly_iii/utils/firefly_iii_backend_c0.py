# ruff: noqa: F403, F405, E501
from .firefly_iii_backend_base import *  # noqa: F403


class FireflyIIIBackendMixin0:
    """Firefly III API backend client"""

    def __init__(self, base_url: str, pat: str):
        """
        Initialize Firefly III backend client

        Args:
            base_url: Firefly III instance base URL
            pat: Personal Access Token
        """
        self.base_url = base_url.rstrip("/")
        self.pat = pat
        self.headers = {
            "Authorization": f"Bearer {pat}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Validate connection
        self._validate_connection()

    def _validate_connection(self):
        """Validate connection to Firefly III instance"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/about", headers=self.headers, timeout=10
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to Firefly III instance: {self.base_url}\n"
                f"Please ensure:\n"
                f"1. Firefly III instance is running\n"
                f"2. Base URL is correct\n"
                f"3. Network connection is normal"
            )
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise RuntimeError(
                    "Authentication failed: Personal Access Token is invalid\n"
                    "Please generate a new PAT in Firefly III Options > Profile > OAuth"
                )
            raise RuntimeError(f"HTTP Error {response.status_code}: {response.text}")

    def request(
        self, method: str, endpoint: str, params: Dict = None, data: Dict = None
    ) -> Dict[str, Any]:
        """
        Send request to Firefly III API

        Args:
            method: HTTP method (get, post, put, delete)
            endpoint: API endpoint path (e.g., /accounts)
            params: URL query parameters
            data: Request body data

        Returns:
            API response JSON data

        Raises:
            RuntimeError: Connection error or HTTP error
        """
        url = f"{self.base_url}/api/v1{endpoint}"

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=30,
            )
            response.raise_for_status()
            if response.status_code == 204:
                return {"status": "success", "code": 204}
            return response.json()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to Firefly III instance: {self.base_url}"
            )
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise RuntimeError(
                    "Authentication failed: Personal Access Token is invalid"
                )
            elif response.status_code == 404:
                raise RuntimeError(f"Resource not found: {endpoint}")
            elif response.status_code == 422:
                error_detail = response.json().get("message", "Unknown error")
                raise RuntimeError(f"Request parameter error: {error_detail}")
            else:
                raise RuntimeError(
                    f"HTTP Error {response.status_code}: {response.text}"
                )
        except requests.exceptions.Timeout:
            raise RuntimeError("Request timeout, please check network connection")
        except Exception as e:
            raise RuntimeError(f"Request failed: {e}")

    def get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Send GET request"""
        return self.request("get", endpoint, params=params)

    def post(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Send POST request"""
        return self.request("post", endpoint, data=data)

    def put(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Send PUT request"""
        return self.request("put", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Send DELETE request"""
        return self.request("delete", endpoint)

    def get_about(self) -> Dict[str, Any]:
        """Get Firefly III system information"""
        return self.get("/about")

    def get_accounts(self, params: Dict = None) -> Dict[str, Any]:
        """Get account list"""
        return self.get("/accounts", params=params)

    def get_account(self, account_id: int) -> Dict[str, Any]:
        """Get single account details"""
        return self.get(f"/accounts/{account_id}")
