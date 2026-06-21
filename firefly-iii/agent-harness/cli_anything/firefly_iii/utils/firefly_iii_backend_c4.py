# ruff: noqa: F403, F405, E501
from .firefly_iii_backend_base import *  # noqa: F403


class FireflyIIIBackendMixin4:
    def update_attachment(self, attachment_id: int, data: Dict) -> Dict[str, Any]:
        """Update attachment"""
        return self.put(f"/attachments/{attachment_id}", data=data)

    def delete_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """Delete attachment"""
        return self.delete(f"/attachments/{attachment_id}")

    def get_configuration(self) -> Dict[str, Any]:
        """Get configuration"""
        return self.get("/configuration")

    def update_configuration(self, data: Dict) -> Dict[str, Any]:
        """Update configuration"""
        return self.put("/configuration", data=data)

    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        return self.get("/preferences")

    def update_preference(self, key: str, data: Dict) -> Dict[str, Any]:
        """Update a preference"""
        return self.put(f"/preferences/{key}", data=data)

    def get_users(self, params: Dict = None) -> Dict[str, Any]:
        """Get user list"""
        return self.get("/users", params=params)

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get single user details"""
        return self.get(f"/users/{user_id}")

    def create_user(self, data: Dict) -> Dict[str, Any]:
        """Create new user"""
        return self.post("/users", data=data)

    def update_user(self, user_id: int, data: Dict) -> Dict[str, Any]:
        """Update user"""
        return self.put(f"/users/{user_id}", data=data)

    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete user"""
        return self.delete(f"/users/{user_id}")

    def get_user_groups(self, params: Dict = None) -> Dict[str, Any]:
        """Get user group list"""
        return self.get("/user-groups", params=params)

    def get_user_group(self, user_group_id: int) -> Dict[str, Any]:
        """Get single user group details"""
        return self.get(f"/user-groups/{user_group_id}")

    def bulk_update_transactions(self, data: Dict) -> Dict[str, Any]:
        """Bulk update transactions"""
        return self.post("/data/bulk/transactions", data=data)

    def destroy_data(self, data_type: str) -> Dict[str, Any]:
        """Destroy user data"""
        return self.delete(f"/data/destroy?objects={data_type}")

    def purge_data(self) -> Dict[str, Any]:
        """Purge deleted data"""
        return self.delete("/data/purge")
