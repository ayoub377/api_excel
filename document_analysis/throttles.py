from rest_framework.throttling import UserRateThrottle


class RoleBasedThrottle(UserRateThrottle):
    def allow_request(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_plus_member:
                self.rate = '500/day'
            elif not user.is_plus_member:
                self.rate = '50/day'

        self.num_requests, self.duration = self.parse_rate(self.rate)

        return super().allow_request(request, view)
