# Sentinel's Journal 🛡️

## 2025-05-14 - [Initial Security Audit and Remediation]
**Vulnerability:**
1. **OTP Leakage**: The `/auth/forgot-password` endpoint returned the generated OTP in the API response, allowing anyone with a user's email to reset their password.
2. **Predictable User IDs**: User IDs were sequential 6-digit strings, making user enumeration and IDOR attacks trivial.
3. **Missing Authentication/Authorization**: Most endpoints lacked any form of authentication, and user-specific data (Cart, Profile) could be accessed/modified by anyone knowing the `user_id`.
4. **User Enumeration**: Sign-in and forgot-password endpoints leaked account existence via `404 Not Found` errors.

**Learning:**
The application was built with focus on functionality but lacked "security by design". Direct feedback of sensitive tokens (OTP) and lack of auth middleware are common but critical gaps in early-stage projects.

**Prevention:**
- Never return secrets (OTPs, tokens) in responses.
- Use non-sequential identifiers (like UUIDs).
- Implement centralized authentication (JWT) and always verify that the authenticated user owns the resource they are accessing.
- Use generic error messages for authentication-related failures.
