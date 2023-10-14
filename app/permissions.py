from rest_framework import permissions

class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Kiểm tra xem người dùng có quyền là "admin" hay không
        account = request.account  # Đây là đối tượng User được trả về từ token
        if account.role == "admin":
            return True
        return False
    
class IsDoctorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Kiểm tra xem người dùng có quyền là "doctor" hay không
        account = request.account  # Đây là đối tượng User được trả về từ token
        if account.role == "doctor":
            return True
        return False

class IsHospitalPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Kiểm tra xem người dùng có quyền là "hospital" hay không
        account = request.account  # Đây là đối tượng User được trả về từ token
        if account.role == "hospital":
            return True
        return False