# ruff: noqa: F403, F405, E501
from .firefly_iii_backend_base import *  # noqa: F403


class FireflyIIIBackendMixin1:
    def create_account(self, data: Dict) -> Dict[str, Any]:
        """Create new account"""
        return self.post("/accounts", data=data)

    def update_account(self, account_id: int, data: Dict) -> Dict[str, Any]:
        """Update account"""
        return self.put(f"/accounts/{account_id}", data=data)

    def delete_account(self, account_id: int) -> Dict[str, Any]:
        """Delete account"""
        return self.delete(f"/accounts/{account_id}")

    def get_transactions(self, params: Dict = None) -> Dict[str, Any]:
        """Get transaction list"""
        return self.get("/transactions", params=params)

    def get_transaction(self, transaction_id: int) -> Dict[str, Any]:
        """Get single transaction details"""
        return self.get(f"/transactions/{transaction_id}")

    def create_transaction(self, data: Dict) -> Dict[str, Any]:
        """Create new transaction"""
        return self.post("/transactions", data=data)

    def update_transaction(self, transaction_id: int, data: Dict) -> Dict[str, Any]:
        """Update transaction"""
        return self.put(f"/transactions/{transaction_id}", data=data)

    def delete_transaction(self, transaction_id: int) -> Dict[str, Any]:
        """Delete transaction"""
        return self.delete(f"/transactions/{transaction_id}")

    def get_budgets(self, params: Dict = None) -> Dict[str, Any]:
        """Get budget list"""
        return self.get("/budgets", params=params)

    def get_budget(self, budget_id: int) -> Dict[str, Any]:
        """Get single budget details"""
        return self.get(f"/budgets/{budget_id}")

    def create_budget(self, data: Dict) -> Dict[str, Any]:
        """Create new budget"""
        return self.post("/budgets", data=data)

    def update_budget(self, budget_id: int, data: Dict) -> Dict[str, Any]:
        """Update budget"""
        return self.put(f"/budgets/{budget_id}", data=data)

    def delete_budget(self, budget_id: int) -> Dict[str, Any]:
        """Delete budget"""
        return self.delete(f"/budgets/{budget_id}")

    def get_budget_limits(self, budget_id: int, params: Dict = None) -> Dict[str, Any]:
        """Get budget limits for a budget"""
        return self.get(f"/budgets/{budget_id}/limits", params=params)

    def create_budget_limit(self, budget_id: int, data: Dict) -> Dict[str, Any]:
        """Create budget limit"""
        return self.post(f"/budgets/{budget_id}/limits", data=data)

    def update_budget_limit(self, budget_limit_id: int, data: Dict) -> Dict[str, Any]:
        """Update budget limit"""
        return self.put(f"/budget_limits/{budget_limit_id}", data=data)

    def delete_budget_limit(self, budget_limit_id: int) -> Dict[str, Any]:
        """Delete budget limit"""
        return self.delete(f"/budget_limits/{budget_limit_id}")

    def get_categories(self, params: Dict = None) -> Dict[str, Any]:
        """Get category list"""
        return self.get("/categories", params=params)

    def get_category(self, category_id: int) -> Dict[str, Any]:
        """Get single category details"""
        return self.get(f"/categories/{category_id}")

    def create_category(self, data: Dict) -> Dict[str, Any]:
        """Create new category"""
        return self.post("/categories", data=data)

    def update_category(self, category_id: int, data: Dict) -> Dict[str, Any]:
        """Update category"""
        return self.put(f"/categories/{category_id}", data=data)

    def delete_category(self, category_id: int) -> Dict[str, Any]:
        """Delete category"""
        return self.delete(f"/categories/{category_id}")

    def get_tags(self, params: Dict = None) -> Dict[str, Any]:
        """Get tag list"""
        return self.get("/tags", params=params)

    def get_tag(self, tag_id: str) -> Dict[str, Any]:
        """Get single tag details"""
        return self.get(f"/tags/{tag_id}")

    def create_tag(self, data: Dict) -> Dict[str, Any]:
        """Create new tag"""
        return self.post("/tags", data=data)

    def update_tag(self, tag_id: str, data: Dict) -> Dict[str, Any]:
        """Update tag"""
        return self.put(f"/tags/{tag_id}", data=data)

    def delete_tag(self, tag_id: str) -> Dict[str, Any]:
        """Delete tag"""
        return self.delete(f"/tags/{tag_id}")

    def get_bills(self, params: Dict = None) -> Dict[str, Any]:
        """Get bill list"""
        return self.get("/bills", params=params)

    def get_bill(self, bill_id: int) -> Dict[str, Any]:
        """Get single bill details"""
        return self.get(f"/bills/{bill_id}")

    def create_bill(self, data: Dict) -> Dict[str, Any]:
        """Create new bill"""
        return self.post("/bills", data=data)

    def update_bill(self, bill_id: int, data: Dict) -> Dict[str, Any]:
        """Update bill"""
        return self.put(f"/bills/{bill_id}", data=data)

    def delete_bill(self, bill_id: int) -> Dict[str, Any]:
        """Delete bill"""
        return self.delete(f"/bills/{bill_id}")

    def get_piggy_banks(self, params: Dict = None) -> Dict[str, Any]:
        """Get piggy bank list"""
        return self.get("/piggy-banks", params=params)

    def get_piggy_bank(self, piggy_bank_id: int) -> Dict[str, Any]:
        """Get single piggy bank details"""
        return self.get(f"/piggy-banks/{piggy_bank_id}")

    def create_piggy_bank(self, data: Dict) -> Dict[str, Any]:
        """Create new piggy bank"""
        return self.post("/piggy-banks", data=data)

    def update_piggy_bank(self, piggy_bank_id: int, data: Dict) -> Dict[str, Any]:
        """Update piggy bank"""
        return self.put(f"/piggy-banks/{piggy_bank_id}", data=data)
