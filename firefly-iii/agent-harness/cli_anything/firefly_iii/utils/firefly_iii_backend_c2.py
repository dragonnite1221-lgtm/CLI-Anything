# ruff: noqa: F403, F405, E501
from .firefly_iii_backend_base import *  # noqa: F403


class FireflyIIIBackendMixin2:
    def delete_piggy_bank(self, piggy_bank_id: int) -> Dict[str, Any]:
        """Delete piggy bank"""
        return self.delete(f"/piggy-banks/{piggy_bank_id}")

    def get_piggy_bank_events(self, piggy_bank_id: int) -> Dict[str, Any]:
        """Get piggy bank events"""
        return self.get(f"/piggy-banks/{piggy_bank_id}/events")

    def create_piggy_bank_event(self, piggy_bank_id: int, data: Dict) -> Dict[str, Any]:
        """Add money to piggy bank"""
        return self.post(f"/piggy-banks/{piggy_bank_id}/events", data=data)

    def autocomplete_accounts(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete accounts"""
        return self.get("/autocomplete/accounts", params=params)

    def autocomplete_bills(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete bills"""
        return self.get("/autocomplete/bills", params=params)

    def autocomplete_budgets(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete budgets"""
        return self.get("/autocomplete/budgets", params=params)

    def autocomplete_categories(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete categories"""
        return self.get("/autocomplete/categories", params=params)

    def autocomplete_currencies(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete currencies"""
        return self.get("/autocomplete/currencies", params=params)

    def autocomplete_piggy_banks(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete piggy banks"""
        return self.get("/autocomplete/piggy-banks", params=params)

    def autocomplete_tags(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete tags"""
        return self.get("/autocomplete/tags", params=params)

    def autocomplete_transactions(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete transactions"""
        return self.get("/autocomplete/transactions", params=params)

    def autocomplete_rule_groups(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete rule groups"""
        return self.get("/autocomplete/rule-groups", params=params)

    def autocomplete_rules(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete rules"""
        return self.get("/autocomplete/rules", params=params)

    def autocomplete_recurring(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete recurring transactions"""
        return self.get("/autocomplete/recurring", params=params)

    def autocomplete_object_groups(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete object groups"""
        return self.get("/autocomplete/object-groups", params=params)

    def autocomplete_transaction_types(self, params: Dict = None) -> Dict[str, Any]:
        """Autocomplete transaction types"""
        return self.get("/autocomplete/transaction-types", params=params)

    def get_currencies(self, params: Dict = None) -> Dict[str, Any]:
        """Get currency list"""
        return self.get("/currencies", params=params)

    def get_currency(self, currency_id: int) -> Dict[str, Any]:
        """Get single currency details"""
        return self.get(f"/currencies/{currency_id}")

    def create_currency(self, data: Dict) -> Dict[str, Any]:
        """Create new currency"""
        return self.post("/currencies", data=data)

    def update_currency(self, currency_id: int, data: Dict) -> Dict[str, Any]:
        """Update currency"""
        return self.put(f"/currencies/{currency_id}", data=data)

    def delete_currency(self, currency_id: int) -> Dict[str, Any]:
        """Delete currency"""
        return self.delete(f"/currencies/{currency_id}")

    def get_currency_exchange_rates(self, params: Dict = None) -> Dict[str, Any]:
        """Get currency exchange rates"""
        return self.get("/currency_exchange_rates", params=params)

    def get_recurrences(self, params: Dict = None) -> Dict[str, Any]:
        """Get recurring transaction list"""
        return self.get("/recurrences", params=params)

    def get_recurrence(self, recurrence_id: int) -> Dict[str, Any]:
        """Get single recurring transaction details"""
        return self.get(f"/recurrences/{recurrence_id}")

    def create_recurrence(self, data: Dict) -> Dict[str, Any]:
        """Create new recurring transaction"""
        return self.post("/recurrences", data=data)

    def update_recurrence(self, recurrence_id: int, data: Dict) -> Dict[str, Any]:
        """Update recurring transaction"""
        return self.put(f"/recurrences/{recurrence_id}", data=data)

    def delete_recurrence(self, recurrence_id: int) -> Dict[str, Any]:
        """Delete recurring transaction"""
        return self.delete(f"/recurrences/{recurrence_id}")

    def get_rules(self, params: Dict = None) -> Dict[str, Any]:
        """Get rule list"""
        return self.get("/rules", params=params)

    def get_rule(self, rule_id: int) -> Dict[str, Any]:
        """Get single rule details"""
        return self.get(f"/rules/{rule_id}")

    def create_rule(self, data: Dict) -> Dict[str, Any]:
        """Create new rule"""
        return self.post("/rules", data=data)

    def update_rule(self, rule_id: int, data: Dict) -> Dict[str, Any]:
        """Update rule"""
        return self.put(f"/rules/{rule_id}", data=data)

    def delete_rule(self, rule_id: int) -> Dict[str, Any]:
        """Delete rule"""
        return self.delete(f"/rules/{rule_id}")

    def test_rule(self, rule_id: int, data: Dict = None) -> Dict[str, Any]:
        """Test a rule"""
        return self.post(f"/rules/{rule_id}/test", data=data)

    def execute_rule(self, rule_id: int) -> Dict[str, Any]:
        """Execute a rule"""
        return self.post(f"/rules/{rule_id}/trigger")

    def get_rule_groups(self, params: Dict = None) -> Dict[str, Any]:
        """Get rule group list"""
        return self.get("/rule-groups", params=params)

    def get_rule_group(self, rule_group_id: int) -> Dict[str, Any]:
        """Get single rule group details"""
        return self.get(f"/rule-groups/{rule_group_id}")
