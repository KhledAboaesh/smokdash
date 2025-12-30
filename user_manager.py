class UserManager:
    def __init__(self, db):
        self.db = db
        self.roles = {
            "admin": {
                "permissions": [
                    "view_dashboard",
                    "use_pos",
                    "manage_inventory",
                    "manage_customers",
                    "view_reports",
                    "manage_reports",
                    "manage_settings",
                    "manage_users",
                    "manage_backups"
                ]
            },
            "cashier": {
                "permissions": [
                    "view_dashboard",
                    "use_pos",
                    "view_inventory",
                    "view_customers",
                    "add_customers",
                    "view_reports"
                ]
            },
            "manager": {
                "permissions": [
                    "view_dashboard",
                    "use_pos",
                    "manage_inventory",
                    "manage_customers",
                    "view_reports",
                    "manage_reports"
                ]
            }
        }
    
    def check_permission(self, user, permission):
        """التحقق من صلاحية المستخدم"""
        user_role = user.get('role', 'cashier')
        
        if user_role in self.roles:
            return permission in self.roles[user_role]['permissions']
        
        return False
    
    def get_role_permissions(self, role):
        """الحصول على صلاحيات دور معين"""
        return self.roles.get(role, {}).get('permissions', [])
    
    def create_role(self, role_name, permissions):
        """إنشاء دور جديد"""
        if role_name not in self.roles:
            self.roles[role_name] = {"permissions": permissions}
            return True
        return False