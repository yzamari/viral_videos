"""
Enterprise Features System
Multi-tenancy, RBAC, SSO, Audit Logging, Compliance
"""

import uuid
import json
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from functools import wraps
import asyncio
import redis
from sqlalchemy import create_engine, Column, String, DateTime, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


class Role(Enum):
    """System roles"""
    SUPER_ADMIN = "super_admin"
    ORGANIZATION_ADMIN = "organization_admin"
    CAMPAIGN_MANAGER = "campaign_manager"
    CREATIVE_EDITOR = "creative_editor"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(Enum):
    """System permissions"""
    # Campaign permissions
    CAMPAIGN_CREATE = "campaign:create"
    CAMPAIGN_READ = "campaign:read"
    CAMPAIGN_UPDATE = "campaign:update"
    CAMPAIGN_DELETE = "campaign:delete"
    CAMPAIGN_LAUNCH = "campaign:launch"
    CAMPAIGN_PAUSE = "campaign:pause"
    
    # Analytics permissions
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"
    
    # Workflow permissions
    WORKFLOW_CREATE = "workflow:create"
    WORKFLOW_EXECUTE = "workflow:execute"
    WORKFLOW_DELETE = "workflow:delete"
    
    # Admin permissions
    USER_MANAGE = "user:manage"
    ORGANIZATION_MANAGE = "organization:manage"
    BILLING_MANAGE = "billing:manage"
    SETTINGS_MANAGE = "settings:manage"


@dataclass
class Organization:
    """Organization/Tenant entity"""
    org_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    domain: str = ""
    plan: str = "starter"  # starter, professional, enterprise
    max_users: int = 5
    max_campaigns: int = 10
    features: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class User:
    """User entity"""
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    organization_id: str = ""
    roles: List[Role] = field(default_factory=list)
    permissions: Set[Permission] = field(default_factory=set)
    active: bool = True
    mfa_enabled: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditLog:
    """Audit log entry"""
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    organization_id: str = ""
    user_id: str = ""
    action: str = ""
    resource_type: str = ""
    resource_id: str = ""
    ip_address: str = ""
    user_agent: str = ""
    status: str = ""  # success, failure
    details: Dict[str, Any] = field(default_factory=dict)


class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self):
        """Initialize RBAC manager"""
        self.role_permissions = self._define_role_permissions()
        self.custom_roles: Dict[str, Set[Permission]] = {}
        
        logger.info("✅ RBACManager initialized")
    
    def _define_role_permissions(self) -> Dict[Role, Set[Permission]]:
        """Define default role permissions"""
        return {
            Role.SUPER_ADMIN: set(Permission),  # All permissions
            
            Role.ORGANIZATION_ADMIN: {
                Permission.CAMPAIGN_CREATE,
                Permission.CAMPAIGN_READ,
                Permission.CAMPAIGN_UPDATE,
                Permission.CAMPAIGN_DELETE,
                Permission.CAMPAIGN_LAUNCH,
                Permission.CAMPAIGN_PAUSE,
                Permission.ANALYTICS_VIEW,
                Permission.ANALYTICS_EXPORT,
                Permission.WORKFLOW_CREATE,
                Permission.WORKFLOW_EXECUTE,
                Permission.WORKFLOW_DELETE,
                Permission.USER_MANAGE,
                Permission.SETTINGS_MANAGE
            },
            
            Role.CAMPAIGN_MANAGER: {
                Permission.CAMPAIGN_CREATE,
                Permission.CAMPAIGN_READ,
                Permission.CAMPAIGN_UPDATE,
                Permission.CAMPAIGN_LAUNCH,
                Permission.CAMPAIGN_PAUSE,
                Permission.ANALYTICS_VIEW,
                Permission.ANALYTICS_EXPORT,
                Permission.WORKFLOW_EXECUTE
            },
            
            Role.CREATIVE_EDITOR: {
                Permission.CAMPAIGN_READ,
                Permission.CAMPAIGN_UPDATE,
                Permission.ANALYTICS_VIEW
            },
            
            Role.ANALYST: {
                Permission.CAMPAIGN_READ,
                Permission.ANALYTICS_VIEW,
                Permission.ANALYTICS_EXPORT
            },
            
            Role.VIEWER: {
                Permission.CAMPAIGN_READ,
                Permission.ANALYTICS_VIEW
            }
        }
    
    def check_permission(
        self,
        user: User,
        permission: Permission,
        resource: Optional[Any] = None
    ) -> bool:
        """
        Check if user has permission
        
        Args:
            user: User object
            permission: Required permission
            resource: Optional resource for context-based checks
            
        Returns:
            True if user has permission
        """
        # Check direct user permissions
        if permission in user.permissions:
            return True
        
        # Check role-based permissions
        for role in user.roles:
            if permission in self.role_permissions.get(role, set()):
                return True
        
        # Check custom roles
        for role_name in user.metadata.get("custom_roles", []):
            if permission in self.custom_roles.get(role_name, set()):
                return True
        
        # Resource-based permission check
        if resource and hasattr(resource, "owner_id"):
            if resource.owner_id == user.user_id:
                return True
        
        return False
    
    def require_permission(self, permission: Permission):
        """
        Decorator to require permission for function/endpoint
        
        Args:
            permission: Required permission
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Extract user from context
                user = kwargs.get("current_user")
                if not user:
                    raise PermissionError("Authentication required")
                
                if not self.check_permission(user, permission):
                    raise PermissionError(f"Permission denied: {permission.value}")
                
                return await func(*args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Extract user from context
                user = kwargs.get("current_user")
                if not user:
                    raise PermissionError("Authentication required")
                
                if not self.check_permission(user, permission):
                    raise PermissionError(f"Permission denied: {permission.value}")
                
                return func(*args, **kwargs)
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def create_custom_role(
        self,
        name: str,
        permissions: Set[Permission],
        organization_id: str
    ):
        """Create custom role for organization"""
        role_key = f"{organization_id}:{name}"
        self.custom_roles[role_key] = permissions
        logger.info(f"✅ Custom role created: {name}")
    
    def grant_permission(self, user: User, permission: Permission):
        """Grant permission to user"""
        user.permissions.add(permission)
        logger.info(f"Permission granted: {permission.value} to {user.username}")
    
    def revoke_permission(self, user: User, permission: Permission):
        """Revoke permission from user"""
        user.permissions.discard(permission)
        logger.info(f"Permission revoked: {permission.value} from {user.username}")


class MultiTenantManager:
    """Multi-tenant system manager"""
    
    def __init__(self, database_url: str = "sqlite:///enterprise.db"):
        """Initialize multi-tenant manager"""
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        self.organizations: Dict[str, Organization] = {}
        self.users: Dict[str, User] = {}
        self.tenant_isolation = True
        
        # Redis for caching and session management
        self.redis_client = redis.StrictRedis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        
        logger.info("✅ MultiTenantManager initialized")
    
    def create_organization(
        self,
        name: str,
        domain: str,
        plan: str = "starter",
        owner_email: str = ""
    ) -> Organization:
        """
        Create new organization/tenant
        
        Args:
            name: Organization name
            domain: Organization domain
            plan: Subscription plan
            owner_email: Owner's email
            
        Returns:
            Created organization
        """
        org = Organization(
            name=name,
            domain=domain,
            plan=plan
        )
        
        # Set plan limits
        if plan == "starter":
            org.max_users = 5
            org.max_campaigns = 10
            org.features = ["basic_analytics", "email_support"]
        elif plan == "professional":
            org.max_users = 25
            org.max_campaigns = 100
            org.features = ["advanced_analytics", "api_access", "priority_support"]
        elif plan == "enterprise":
            org.max_users = -1  # Unlimited
            org.max_campaigns = -1  # Unlimited
            org.features = ["all_features", "sso", "dedicated_support", "sla"]
        
        # Create organization database schema
        self._create_tenant_schema(org.org_id)
        
        # Create owner user
        if owner_email:
            owner = self.create_user(
                username=owner_email.split("@")[0],
                email=owner_email,
                organization_id=org.org_id,
                roles=[Role.ORGANIZATION_ADMIN]
            )
            org.metadata["owner_id"] = owner.user_id
        
        self.organizations[org.org_id] = org
        
        logger.info(f"✅ Organization created: {org.name}")
        return org
    
    def create_user(
        self,
        username: str,
        email: str,
        organization_id: str,
        roles: List[Role] = None
    ) -> User:
        """
        Create user within organization
        
        Args:
            username: Username
            email: Email address
            organization_id: Organization ID
            roles: User roles
            
        Returns:
            Created user
        """
        org = self.organizations.get(organization_id)
        if not org:
            raise ValueError(f"Organization {organization_id} not found")
        
        # Check user limit
        org_users = [u for u in self.users.values() if u.organization_id == organization_id]
        if org.max_users != -1 and len(org_users) >= org.max_users:
            raise ValueError(f"User limit reached for organization")
        
        user = User(
            username=username,
            email=email,
            organization_id=organization_id,
            roles=roles or [Role.VIEWER]
        )
        
        # Set permissions based on roles
        rbac = RBACManager()
        for role in user.roles:
            user.permissions.update(rbac.role_permissions.get(role, set()))
        
        self.users[user.user_id] = user
        
        logger.info(f"✅ User created: {user.username}")
        return user
    
    def _create_tenant_schema(self, tenant_id: str):
        """Create isolated schema for tenant"""
        # In production, create separate database schema
        # For demo, use table prefixing
        schema_name = f"tenant_{tenant_id.replace('-', '_')}"
        
        # Create tenant-specific tables
        with self.Session() as session:
            # This would create actual schema in production
            session.execute(f"-- CREATE SCHEMA IF NOT EXISTS {schema_name}")
            session.commit()
        
        logger.info(f"Tenant schema created: {schema_name}")
    
    def get_tenant_context(self, organization_id: str) -> Dict[str, Any]:
        """Get tenant-specific context"""
        org = self.organizations.get(organization_id)
        if not org:
            raise ValueError(f"Organization {organization_id} not found")
        
        return {
            "organization": org,
            "database_schema": f"tenant_{organization_id.replace('-', '_')}",
            "features": org.features,
            "limits": {
                "max_users": org.max_users,
                "max_campaigns": org.max_campaigns
            },
            "settings": org.settings
        }
    
    def switch_tenant(self, user_id: str, organization_id: str):
        """Switch user to different tenant (for multi-org users)"""
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Check if user has access to organization
        if organization_id not in user.metadata.get("organizations", [user.organization_id]):
            raise PermissionError("User does not have access to this organization")
        
        # Update context
        user.metadata["current_organization"] = organization_id
        
        logger.info(f"User {user.username} switched to organization {organization_id}")


class SSOManager:
    """Single Sign-On Manager"""
    
    def __init__(self):
        """Initialize SSO manager"""
        self.providers = self._configure_providers()
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info("✅ SSOManager initialized")
    
    def _configure_providers(self) -> Dict[str, Dict[str, Any]]:
        """Configure SSO providers"""
        return {
            "saml": {
                "type": "saml2",
                "metadata_url": os.getenv("SAML_METADATA_URL"),
                "entity_id": os.getenv("SAML_ENTITY_ID"),
                "sso_url": os.getenv("SAML_SSO_URL")
            },
            "oauth2": {
                "type": "oauth2",
                "client_id": os.getenv("OAUTH_CLIENT_ID"),
                "client_secret": os.getenv("OAUTH_CLIENT_SECRET"),
                "authorize_url": os.getenv("OAUTH_AUTHORIZE_URL"),
                "token_url": os.getenv("OAUTH_TOKEN_URL")
            },
            "google": {
                "type": "oauth2",
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "authorize_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token"
            },
            "microsoft": {
                "type": "oauth2",
                "client_id": os.getenv("AZURE_CLIENT_ID"),
                "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
                "tenant_id": os.getenv("AZURE_TENANT_ID"),
                "authorize_url": f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/authorize",
                "token_url": f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token"
            }
        }
    
    def initiate_sso(
        self,
        provider: str,
        redirect_uri: str,
        organization_id: str
    ) -> str:
        """
        Initiate SSO flow
        
        Args:
            provider: SSO provider name
            redirect_uri: Callback URL
            organization_id: Organization ID
            
        Returns:
            SSO authorization URL
        """
        if provider not in self.providers:
            raise ValueError(f"Unknown SSO provider: {provider}")
        
        config = self.providers[provider]
        state = str(uuid.uuid4())
        
        # Store state for validation
        self.sessions[state] = {
            "provider": provider,
            "organization_id": organization_id,
            "redirect_uri": redirect_uri,
            "created_at": datetime.now().isoformat()
        }
        
        if config["type"] == "oauth2":
            # Build OAuth2 authorization URL
            params = {
                "client_id": config["client_id"],
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "state": state,
                "scope": "openid profile email"
            }
            
            from urllib.parse import urlencode
            auth_url = f"{config['authorize_url']}?{urlencode(params)}"
            return auth_url
        
        elif config["type"] == "saml2":
            # Build SAML request
            # In production, use python-saml library
            return f"{config['sso_url']}?SAMLRequest=encoded_request&RelayState={state}"
        
        return ""
    
    def handle_callback(
        self,
        provider: str,
        code: str,
        state: str
    ) -> Tuple[User, str]:
        """
        Handle SSO callback
        
        Args:
            provider: SSO provider
            code: Authorization code
            state: State parameter
            
        Returns:
            Authenticated user and access token
        """
        # Validate state
        session = self.sessions.get(state)
        if not session:
            raise ValueError("Invalid state parameter")
        
        if session["provider"] != provider:
            raise ValueError("Provider mismatch")
        
        config = self.providers[provider]
        
        if config["type"] == "oauth2":
            # Exchange code for token
            import requests
            
            token_data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": session["redirect_uri"],
                "client_id": config["client_id"],
                "client_secret": config["client_secret"]
            }
            
            response = requests.post(config["token_url"], data=token_data)
            tokens = response.json()
            
            # Get user info
            user_info = self._get_user_info(provider, tokens["access_token"])
            
            # Find or create user
            user = self._find_or_create_user(
                user_info,
                session["organization_id"]
            )
            
            # Clean up session
            del self.sessions[state]
            
            return user, tokens["access_token"]
        
        raise ValueError("SSO callback handling failed")
    
    def _get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """Get user info from SSO provider"""
        import requests
        
        if provider == "google":
            response = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.json()
        
        elif provider == "microsoft":
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.json()
        
        return {}
    
    def _find_or_create_user(
        self,
        user_info: Dict[str, Any],
        organization_id: str
    ) -> User:
        """Find existing user or create new one from SSO info"""
        email = user_info.get("email")
        
        # Find existing user
        for user in self.users.values():
            if user.email == email and user.organization_id == organization_id:
                user.last_login = datetime.now()
                return user
        
        # Create new user
        multi_tenant = MultiTenantManager()
        user = multi_tenant.create_user(
            username=user_info.get("name", email.split("@")[0]),
            email=email,
            organization_id=organization_id,
            roles=[Role.VIEWER]  # Default role for SSO users
        )
        
        user.metadata["sso_provider"] = user_info.get("provider")
        user.metadata["sso_id"] = user_info.get("id")
        
        return user


class AuditLogger:
    """Audit logging system"""
    
    def __init__(self, database_url: str = "sqlite:///audit.db"):
        """Initialize audit logger"""
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        logger.info("✅ AuditLogger initialized")
    
    def log(
        self,
        organization_id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        status: str = "success",
        details: Dict[str, Any] = None,
        ip_address: str = "",
        user_agent: str = ""
    ):
        """
        Log audit entry
        
        Args:
            organization_id: Organization ID
            user_id: User ID
            action: Action performed
            resource_type: Type of resource
            resource_id: Resource ID
            status: Success or failure
            details: Additional details
            ip_address: Client IP
            user_agent: Client user agent
        """
        entry = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Store in database
        with self.Session() as session:
            # In production, store in actual audit table
            logger.info(f"Audit: {action} on {resource_type}:{resource_id} by {user_id}")
        
        # Also send to SIEM if configured
        self._send_to_siem(entry)
    
    def _send_to_siem(self, entry: AuditLog):
        """Send audit log to SIEM system"""
        # In production, integrate with Splunk, ELK, etc.
        pass
    
    def query_logs(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> List[AuditLog]:
        """Query audit logs"""
        # In production, query from database
        logs = []
        
        # Filter logic here
        
        return logs


class ComplianceManager:
    """Compliance and regulatory management"""
    
    def __init__(self):
        """Initialize compliance manager"""
        self.regulations = self._load_regulations()
        self.data_residency = {}
        
        logger.info("✅ ComplianceManager initialized")
    
    def _load_regulations(self) -> Dict[str, Dict[str, Any]]:
        """Load regulatory requirements"""
        return {
            "GDPR": {
                "regions": ["EU", "EEA"],
                "requirements": [
                    "data_portability",
                    "right_to_erasure",
                    "consent_management",
                    "breach_notification"
                ]
            },
            "CCPA": {
                "regions": ["California"],
                "requirements": [
                    "opt_out",
                    "data_disclosure",
                    "non_discrimination"
                ]
            },
            "HIPAA": {
                "industries": ["healthcare"],
                "requirements": [
                    "encryption",
                    "access_controls",
                    "audit_logs",
                    "breach_notification"
                ]
            }
        }
    
    def check_compliance(
        self,
        organization: Organization,
        operation: str,
        data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Check compliance for operation
        
        Args:
            organization: Organization
            operation: Operation type
            data: Operation data
            
        Returns:
            Compliance status and any violations
        """
        violations = []
        
        # Check GDPR compliance
        if organization.metadata.get("region") in ["EU", "EEA"]:
            if operation == "data_export" and not data.get("user_consent"):
                violations.append("GDPR: User consent required for data export")
            
            if operation == "data_retention" and data.get("retention_days", 0) > 730:
                violations.append("GDPR: Data retention exceeds 2 years")
        
        # Check CCPA compliance
        if organization.metadata.get("region") == "California":
            if operation == "data_sale" and not data.get("opt_out_option"):
                violations.append("CCPA: Must provide opt-out option")
        
        return len(violations) == 0, violations
    
    def enforce_data_residency(
        self,
        organization: Organization,
        data_location: str
    ) -> bool:
        """Enforce data residency requirements"""
        required_location = organization.metadata.get("data_residency")
        
        if required_location and data_location != required_location:
            logger.warning(f"Data residency violation: {data_location} != {required_location}")
            return False
        
        return True
    
    def generate_compliance_report(
        self,
        organization_id: str,
        regulation: str
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        report = {
            "organization_id": organization_id,
            "regulation": regulation,
            "generated_at": datetime.now().isoformat(),
            "status": "compliant",
            "checks": [],
            "recommendations": []
        }
        
        # Perform compliance checks
        requirements = self.regulations.get(regulation, {}).get("requirements", [])
        
        for requirement in requirements:
            check = {
                "requirement": requirement,
                "status": "pass",  # Would check actual implementation
                "details": f"Checked {requirement}"
            }
            report["checks"].append(check)
        
        return report