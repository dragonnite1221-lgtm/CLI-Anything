# ruff: noqa: F403, F405, E501
from .firefly_iii_backend_base import *  # noqa: F403


class FireflyIIIBackendMixin3:
    def create_rule_group(self, data: Dict) -> Dict[str, Any]:
        """Create new rule group"""
        return self.post("/rule-groups", data=data)

    def update_rule_group(self, rule_group_id: int, data: Dict) -> Dict[str, Any]:
        """Update rule group"""
        return self.put(f"/rule-groups/{rule_group_id}", data=data)

    def delete_rule_group(self, rule_group_id: int) -> Dict[str, Any]:
        """Delete rule group"""
        return self.delete(f"/rule-groups/{rule_group_id}")

    def execute_rule_group(self, rule_group_id: int) -> Dict[str, Any]:
        """Execute a rule group"""
        return self.post(f"/rule-groups/{rule_group_id}/trigger")

    def get_summary(self, summary_type: str, params: Dict = None) -> Dict[str, Any]:
        """Get summary report"""
        return self.get(f"/summary/{summary_type}", params=params)

    def get_webhooks(self, params: Dict = None) -> Dict[str, Any]:
        """Get webhook list"""
        return self.get("/webhooks", params=params)

    def get_webhook(self, webhook_id: int) -> Dict[str, Any]:
        """Get single webhook details"""
        return self.get(f"/webhooks/{webhook_id}")

    def create_webhook(self, data: Dict) -> Dict[str, Any]:
        """Create new webhook"""
        return self.post("/webhooks", data=data)

    def update_webhook(self, webhook_id: int, data: Dict) -> Dict[str, Any]:
        """Update webhook"""
        return self.put(f"/webhooks/{webhook_id}", data=data)

    def delete_webhook(self, webhook_id: int) -> Dict[str, Any]:
        """Delete webhook"""
        return self.delete(f"/webhooks/{webhook_id}")

    def trigger_webhook(self, webhook_id: int) -> Dict[str, Any]:
        """Trigger a webhook"""
        return self.post(f"/webhooks/{webhook_id}/trigger")

    def get_insight(self, insight_type: str, params: Dict = None) -> Dict[str, Any]:
        """Get insight report"""
        return self.get(f"/insight/{insight_type}", params=params)

    def search(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Search transactions"""
        search_params = params or {}
        search_params["query"] = query
        return self.get("/search/transactions", params=search_params)

    def export_data(self, data_type: str, params: Dict = None) -> Dict[str, Any]:
        """Export data"""
        return self.get(f"/data/export/{data_type}", params=params)

    def get_chart_account_overview(self, params: Dict) -> Dict[str, Any]:
        """Get account overview chart"""
        return self.get("/chart/account/overview", params=params)

    def get_chart_balance(self, params: Dict) -> Dict[str, Any]:
        """Get balance chart"""
        return self.get("/chart/balance/balance", params=params)

    def get_chart_budget_overview(self, params: Dict) -> Dict[str, Any]:
        """Get budget overview chart"""
        return self.get("/chart/budget/overview", params=params)

    def get_chart_category_overview(self, params: Dict) -> Dict[str, Any]:
        """Get category overview chart"""
        return self.get("/chart/category/overview", params=params)

    def get_available_budgets(self, params: Dict = None) -> Dict[str, Any]:
        """Get available budgets"""
        return self.get("/available_budgets", params=params)

    def create_available_budget(self, data: Dict) -> Dict[str, Any]:
        """Create available budget"""
        return self.post("/available_budgets", data=data)

    def update_available_budget(
        self, available_budget_id: int, data: Dict
    ) -> Dict[str, Any]:
        """Update available budget"""
        return self.put(f"/available_budgets/{available_budget_id}", data=data)

    def delete_available_budget(self, available_budget_id: int) -> Dict[str, Any]:
        """Delete available budget"""
        return self.delete(f"/available_budgets/{available_budget_id}")

    def get_object_groups(self, params: Dict = None) -> Dict[str, Any]:
        """Get object group list"""
        return self.get("/object-groups", params=params)

    def get_object_group(self, object_group_id: int) -> Dict[str, Any]:
        """Get single object group details"""
        return self.get(f"/object-groups/{object_group_id}")

    def create_object_group(self, data: Dict) -> Dict[str, Any]:
        """Create new object group"""
        return self.post("/object-groups", data=data)

    def update_object_group(self, object_group_id: int, data: Dict) -> Dict[str, Any]:
        """Update object group"""
        return self.put(f"/object-groups/{object_group_id}", data=data)

    def delete_object_group(self, object_group_id: int) -> Dict[str, Any]:
        """Delete object group"""
        return self.delete(f"/object-groups/{object_group_id}")

    def get_links(self, params: Dict = None) -> Dict[str, Any]:
        """Get transaction link types"""
        return self.get("/links", params=params)

    def create_link(self, data: Dict) -> Dict[str, Any]:
        """Create transaction link type"""
        return self.post("/links", data=data)

    def update_link(self, link_id: int, data: Dict) -> Dict[str, Any]:
        """Update transaction link type"""
        return self.put(f"/links/{link_id}", data=data)

    def delete_link(self, link_id: int) -> Dict[str, Any]:
        """Delete transaction link type"""
        return self.delete(f"/links/{link_id}")

    def get_attachments(self, params: Dict = None) -> Dict[str, Any]:
        """Get attachment list"""
        return self.get("/attachments", params=params)

    def get_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """Get single attachment details"""
        return self.get(f"/attachments/{attachment_id}")

    def download_attachment(self, attachment_id: int) -> bytes:
        """Download attachment file"""
        url = f"{self.base_url}/api/v1/attachments/{attachment_id}/download"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.content

    def create_attachment(self, data: Dict) -> Dict[str, Any]:
        """Create new attachment"""
        return self.post("/attachments", data=data)
