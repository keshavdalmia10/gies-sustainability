"""
External API Clients

- NIH RePORTER (grants)
- NSF Awards (grants)
- USPTO PatentsView (patents)
"""

from .nih_client import NIHClient, get_nih_client
from .nsf_client import NSFClient, get_nsf_client
from .uspto_client import USPTOClient, get_uspto_client
from .google_scholar_client import GoogleScholarClient, get_google_scholar_client
from .scopus_client import ScopusClient, get_scopus_client
from .wos_client import WebOfScienceClient, get_wos_client

__all__ = [
    "NIHClient",
    "get_nih_client",
    "NSFClient",
    "get_nsf_client",
    "USPTOClient",
    "get_uspto_client",
    "GoogleScholarClient",
    "get_google_scholar_client",
    "ScopusClient",
    "get_scopus_client",
    "WebOfScienceClient",
    "get_wos_client"
]
